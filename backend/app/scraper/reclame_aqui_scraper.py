import time
import random
import logging
import re
import json
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)


class ReclameAquiScraper:
    """Scraper for collecting complaints from Reclame Aqui"""

    def __init__(self, company_url: str, max_pages: int = 10, delay_min: int = 2, delay_max: int = 5, max_workers: int = 3, start_page: int = 1, fetch_details: bool = False, page_step: int = 1):
        self.company_url = company_url
        self.max_pages = max_pages
        self.start_page = start_page  # Starting page number for batch processing
        self.page_step = page_step  # Step between pages (e.g., 10 to skip pages and avoid duplicates)
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_workers = max_workers  # Number of parallel threads for fetching complaints
        self.fetch_details = fetch_details  # If True, fetch individual pages for complete data (slower)
        self.complaints = []
        self.errors = []
        self._lock = threading.Lock()  # Thread-safe access to complaints list
        self.on_page_complete = None  # Callback for incremental imports

        # Extract company slug from URL (e.g., "drogaria-venancio-site-e-televendas" from the company URL)
        # URL format: https://www.reclameaqui.com.br/empresa/drogaria-venancio-site-e-televendas
        url_parts = company_url.rstrip('/').split('/')
        self.company_slug = url_parts[-1] if url_parts else ''

    def _get_driver(self) -> uc.Chrome:
        """Configure and return undetected ChromeDriver to bypass Cloudflare"""
        try:
            # Create undetected Chrome options
            options = uc.ChromeOptions()

            # NOTE: Headless mode removed - undetected-chromedriver works better in visible mode
            # The window will be moved off-screen to minimize visual intrusion

            # Basic options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')

            # Move window off-screen (still works even in headless)
            options.add_argument('--window-position=-2400,-2400')

            # Disable popups and notifications
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')

            # Reduce logging and noise
            options.add_argument('--log-level=3')
            options.add_argument('--silent')

            # PERFORMANCE OPTIMIZATIONS - Make scraper lighter and faster
            options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-component-update')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-domain-reliability')
            options.add_argument('--disable-features=AutofillServerCommunication')
            options.add_argument('--disable-sync')
            options.add_argument('--metrics-recording-only')
            options.add_argument('--mute-audio')
            options.add_argument('--dns-prefetch-disable')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')

            # Additional preferences - ENHANCED for performance
            prefs = {
                'profile.default_content_setting_values.notifications': 2,
                'credentials_enable_service': False,
                'profile.password_manager_enabled': False,
                'profile.default_content_settings.popups': 0,
                # Disable images for faster loading (we only need text data)
                'profile.managed_default_content_settings.images': 2,
                # Disable JavaScript is NOT recommended as the site needs it to render content
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': False,
                'safebrowsing.disable_download_protection': True,
            }
            options.add_experimental_option('prefs', prefs)

            # NOTE: excludeSwitches not compatible with undetected-chromedriver
            # The library handles automation detection automatically

            # Initialize undetected-chromedriver
            # version_main parameter ensures compatibility with installed Chrome
            driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                version_main=None  # Auto-detect Chrome version
            )

            # Set timeouts - INCREASED for better reliability
            driver.set_page_load_timeout(90)  # Increased from 60 to 90 seconds
            driver.implicitly_wait(15)  # Increased from 10 to 15 seconds

            logger.info("Undetected ChromeDriver initialized (minimized off-screen for Cloudflare bypass)")
            return driver

        except Exception as e:
            logger.error(f"Failed to initialize undetected ChromeDriver: {e}")
            raise

    def _random_delay(self, min_sec: Optional[int] = None, max_sec: Optional[int] = None):
        """Random delay to avoid detection"""
        min_sec = min_sec or self.delay_min
        max_sec = max_sec or self.delay_max
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)

    def _fetch_single_complaint(self, complaint_url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a single complaint page (thread-safe)
        Each thread gets its own WebDriver instance
        """
        driver = None
        try:
            logger.info(f"Fetching complaint: {complaint_url[:60]}...")
            driver = self._get_driver()

            driver.get(complaint_url)

            # Wait for page load - INCREASED timeout for better reliability
            WebDriverWait(driver, 30).until(  # Increased from 10 to 30 seconds
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for Cloudflare - INCREASED timeout
            self._wait_for_cloudflare(driver, timeout=20)  # Increased from 15 to 20 seconds

            # Small delay to avoid overwhelming server
            self._random_delay(1, 2)

            # Parse and return
            complaint_soup = BeautifulSoup(driver.page_source, 'html.parser')
            logger.info(f"Successfully parsed complaint from {complaint_url[:60]}...")
            return complaint_soup

        except Exception as e:
            logger.error(f"Error fetching complaint {complaint_url}: {e}")
            with self._lock:
                self.errors.append(f"Fetch error for {complaint_url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def _wait_for_cloudflare(self, driver, timeout=30):
        """Wait for Cloudflare challenge to complete"""
        logger.info("Checking for Cloudflare challenge...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            page_source = driver.page_source.lower()

            # Check if Cloudflare challenge is present
            if 'cloudflare' in page_source and ('just a moment' in page_source or 'verify you are human' in page_source):
                logger.info("Cloudflare challenge detected, waiting for resolution...")
                time.sleep(2)
                continue
            else:
                logger.info("Cloudflare challenge passed or not present")
                return True

        logger.warning(f"Cloudflare challenge not resolved after {timeout} seconds")
        return False

    def _fetch_complaint_details_with_driver(self, driver, complaint_url: str, basic_data: Dict) -> Dict:
        """
        Fetch individual complaint page using existing driver to extract complete details including location.
        Returns updated complaint data with all fields populated.
        """
        try:
            logger.info(f"Fetching details for: {basic_data.get('title', 'N/A')[:40]}...")
            logger.info(f"URL: {complaint_url}")

            driver.get(complaint_url)

            # Wait for page load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for Cloudflare
            self._wait_for_cloudflare(driver, timeout=20)

            # Small delay
            time.sleep(2)

            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract from __NEXT_DATA__ JSON in individual complaint page
            script = soup.find('script', id='__NEXT_DATA__')
            if script:
                try:
                    data = json.loads(script.string)
                    complaint_detail = data.get('props', {}).get('pageProps', {}).get('complaint', {})

                    if complaint_detail:
                        # Extract location (city + state)
                        city = complaint_detail.get('userCity', '')
                        state = complaint_detail.get('userState', '')
                        if city and state:
                            basic_data['location'] = f"{city} - {state}"
                        elif city:
                            basic_data['location'] = city
                        elif state:
                            basic_data['location'] = state

                        # Extract full description
                        if complaint_detail.get('description'):
                            basic_data['text'] = complaint_detail.get('description', basic_data.get('text', ''))

                        # Extract company response
                        interactions = complaint_detail.get('interactions', [])
                        logger.info(f"Found {len(interactions)} interactions in complaint")

                        # Debug: Log all interaction types found
                        if interactions:
                            for i, interaction in enumerate(interactions):
                                int_type = interaction.get('type', 'UNKNOWN')
                                int_msg = interaction.get('message', '')[:100] if interaction.get('message') else 'NO MESSAGE'
                                logger.info(f"  Interaction {i}: type={int_type}, message_preview={int_msg}...")

                        for interaction in interactions:
                            int_type = interaction.get('type', '')
                            # Company response - can be ANSWER or REPLY
                            if int_type in ('ANSWER', 'REPLY'):
                                basic_data['company_response_text'] = interaction.get('message', '')
                                created = interaction.get('created', '')
                                if created:
                                    try:
                                        basic_data['company_response_date'] = datetime.fromisoformat(created.replace('Z', '+00:00').split('+')[0])
                                    except:
                                        pass
                                logger.info(f"Found {int_type}: {basic_data['company_response_text'][:100]}...")
                            # Customer evaluation - can be FINAL_ANSWER or EVALUATION
                            elif int_type in ('FINAL_ANSWER', 'EVALUATION'):
                                basic_data['customer_evaluation'] = interaction.get('message', '')
                                created = interaction.get('created', '')
                                if created:
                                    try:
                                        basic_data['evaluation_date'] = datetime.fromisoformat(created.replace('Z', '+00:00').split('+')[0])
                                    except:
                                        pass
                                logger.info(f"Found {int_type}: {basic_data['customer_evaluation'][:100]}...")

                        logger.info(f"Extracted details from JSON - Location: {basic_data.get('location', 'N/A')}")

                        # Save individual page HTML for debugging (first 3 only)
                        if hasattr(self, '_debug_count'):
                            self._debug_count += 1
                        else:
                            self._debug_count = 1

                        if self._debug_count <= 3:
                            debug_file = f"debug_html/individual_{self._debug_count}.html"
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(driver.page_source)
                            logger.info(f"Saved individual page HTML to {debug_file}")

                except Exception as e:
                    logger.error(f"Error parsing complaint detail JSON: {e}")

            # Fallback: extract location from HTML if not found in JSON
            if not basic_data.get('location'):
                location_elem = soup.find('span', {'data-testid': 'complaint-location'})
                if location_elem:
                    basic_data['location'] = location_elem.get_text(strip=True)
                    logger.info(f"Extracted location from HTML: {basic_data['location']}")

            return basic_data

        except Exception as e:
            logger.error(f"Error fetching complaint details: {e}")
            with self._lock:
                self.errors.append(f"Detail fetch error: {e}")
            return basic_data

    def _extract_complaints_from_json(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract complaints data from __NEXT_DATA__ JSON in the page.
        This is more reliable than parsing HTML as it contains structured data.
        """
        try:
            script = soup.find('script', id='__NEXT_DATA__')
            if not script:
                return []

            data = json.loads(script.string)
            complaints_data = data.get('props', {}).get('pageProps', {}).get('complaints', {})

            # Get the list of complaints (usually in 'LAST' key)
            items = complaints_data.get('LAST', [])
            if not items:
                # Try other possible keys
                for key in ['data', 'items', 'list']:
                    if key in complaints_data and isinstance(complaints_data[key], list):
                        items = complaints_data[key]
                        break

            if not items:
                logger.warning("No complaints found in JSON data")
                return []

            extracted = []
            for item in items:
                try:
                    # Parse ISO date format: "2025-11-17T18:22:27"
                    created_str = item.get('created', '')
                    complaint_date = datetime.now()
                    if created_str:
                        try:
                            complaint_date = datetime.fromisoformat(created_str.replace('Z', '+00:00').split('+')[0])
                        except:
                            pass

                    # Map status
                    status_map = {
                        'SOLVED': 'Resolvido',
                        'REPLIED': 'Respondida',
                        'ANSWERED': 'Respondida',
                        'NOT_SOLVED': 'Não resolvido',
                        'NOT_REPLIED': 'Não respondida',
                        'PENDING': 'Não respondida',
                        'IN_REPLICA': 'Em réplica',
                        'EVALUATED': 'Avaliada',
                    }
                    raw_status = item.get('status', '')
                    status = status_map.get(raw_status, raw_status)

                    complaint_data = {
                        'title': item.get('title', 'Sem título'),
                        'text': item.get('description', ''),
                        'user_name': item.get('userName', 'Anônimo'),
                        'complaint_date': complaint_date,
                        'status': status,
                        'location': item.get('userState'),
                        'external_id': str(item.get('id', '')),
                        'url': item.get('url', ''),  # URL for fetching details
                        # Response data if available
                        'company_response_text': None,
                        'company_response_date': None,
                        'customer_evaluation': item.get('dealAgain'),
                        'evaluation_date': None,
                    }

                    # Only add if we have meaningful data
                    if complaint_data['title'] and complaint_data['external_id']:
                        extracted.append(complaint_data)

                except Exception as e:
                    logger.error(f"Error extracting complaint from JSON: {e}")
                    continue

            return extracted

        except Exception as e:
            logger.error(f"Error parsing __NEXT_DATA__ JSON: {e}")
            return []

    def _parse_relative_date(self, date_str: str) -> datetime:
        """
        Parse relative dates like 'hÃ¡ 2 dias', 'hÃ¡ 3 horas', 'ontem'
        """
        date_str = date_str.lower().strip()
        now = datetime.now()

        # Handle 'hoje' (today)
        if 'hoje' in date_str or 'agora' in date_str:
            return now

        # Handle 'ontem' (yesterday)
        if 'ontem' in date_str:
            return now - timedelta(days=1)

        # Handle 'hÃ¡ X dias'
        match = re.search(r'hÃ¡\s+(\d+)\s+dia', date_str)
        if match:
            days = int(match.group(1))
            return now - timedelta(days=days)

        # Handle 'hÃ¡ X horas'
        match = re.search(r'hÃ¡\s+(\d+)\s+hora', date_str)
        if match:
            hours = int(match.group(1))
            return now - timedelta(hours=hours)

        # Handle 'hÃ¡ X minutos'
        match = re.search(r'hÃ¡\s+(\d+)\s+minuto', date_str)
        if match:
            minutes = int(match.group(1))
            return now - timedelta(minutes=minutes)

        # Handle 'hÃ¡ X meses'
        match = re.search(r'hÃ¡\s+(\d+)\s+m[eÃª]s', date_str)
        if match:
            months = int(match.group(1))
            return now - timedelta(days=months * 30)

        # Handle 'hÃ¡ X anos'
        match = re.search(r'hÃ¡\s+(\d+)\s+ano', date_str)
        if match:
            years = int(match.group(1))
            return now - timedelta(days=years * 365)

        # Default to now if can't parse
        logger.warning(f"Could not parse date: {date_str}, using current time")
        return now

    def _parse_absolute_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse absolute dates like '18/11/2025 às 15:05' or '18/11/2025'
        """
        date_str = date_str.strip()

        # Try format with time: "18/11/2025 às 15:05"
        # Also handle encoding issues where "às" may appear as different characters
        match = re.search(r'(\d{2}/\d{2}/\d{4})\s*(?:às|as|�s)?\s*(\d{2}:\d{2})?', date_str)
        if match:
            date_part = match.group(1)
            time_part = match.group(2) if match.group(2) else "00:00"
            try:
                return datetime.strptime(f"{date_part} {time_part}", "%d/%m/%Y %H:%M")
            except ValueError:
                pass

        # Try just date format: "18/11/2025"
        match = re.search(r'(\d{2}/\d{2}/\d{4})', date_str)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d/%m/%Y")
            except ValueError:
                pass

        return None

    def _extract_complaint_data(self, element: BeautifulSoup, page_html: str = "") -> Optional[Dict]:
        """
        Extract data from a complaint element
        Uses current Reclame Aqui HTML structure (data-testid attributes)
        """
        try:
            complaint_data = {}

            # Extract title using data-testid
            title_elem = element.find('h1', {'data-testid': 'complaint-title'})
            complaint_data['title'] = title_elem.get_text(strip=True) if title_elem else 'Sem tÃ­tulo'

            # Extract text/description using data-testid
            text_elem = element.find('p', {'data-testid': 'complaint-description'})
            complaint_data['text'] = text_elem.get_text(strip=True) if text_elem else ''

            # If text is too short, it might be a preview - mark it
            if len(complaint_data['text']) < 50:
                complaint_data['text'] = complaint_data['text'] + " [Preview - full text may require detail page]"

            # Extract date using data-testid
            date_elem = element.find('span', {'data-testid': 'complaint-creation-date'})
            if date_elem:
                date_str = date_elem.get_text(strip=True)
                complaint_data['complaint_date'] = self._parse_relative_date(date_str)
            else:
                complaint_data['complaint_date'] = datetime.now()

            # Extract user name (if available)
            user_elem = element.find('span', {'data-testid': 'complaint-user'})
            complaint_data['user_name'] = user_elem.get_text(strip=True) if user_elem else 'AnÃ´nimo'

            # Extract status using data-testid
            status_elem = element.find('div', {'data-testid': 'complaint-status'})
            complaint_data['status'] = status_elem.get_text(strip=True) if status_elem else 'NÃ£o respondida'

            # Extract location using data-testid
            location_elem = element.find('span', {'data-testid': 'complaint-location'})
            complaint_data['location'] = location_elem.get_text(strip=True) if location_elem else None

            # Extract category (if available)
            # Try multiple selectors for category
            category_elem = element.find('a', {'id': 'info_segmento_hero'})
            if category_elem:
                # Category is in <p> tag inside the link
                category_p = category_elem.find('p')
                if category_p:
                    complaint_data['category'] = category_p.get_text(strip=True)
                else:
                    complaint_data['category'] = None
            else:
                # Fallback: try old selector
                category_elem = element.find('li', {'data-testid': 'listitem-categoria'})
                complaint_data['category'] = category_elem.get_text(strip=True) if category_elem else None

            # Extract company response using data-testid="complaint-interaction"
            # HTML structure: <div data-testid="complaint-interaction">
            #   <span>Resposta da empresa</span>
            #   <span>18/11/2025 às 15:05</span>
            #   <p>Response text...</p>
            # </div>
            response_elem = element.find('div', {'data-testid': 'complaint-interaction'})

            if response_elem:
                # Extract response text from <p> tag
                response_text_elem = response_elem.find('p')
                complaint_data['company_response_text'] = response_text_elem.get_text(strip=True) if response_text_elem else None

                # Extract response date from spans - look for date pattern
                spans = response_elem.find_all('span')
                complaint_data['company_response_date'] = None
                for span in spans:
                    span_text = span.get_text(strip=True)
                    # Check if it's a date (contains "/" and numbers)
                    if '/' in span_text and re.search(r'\d{2}/\d{2}/\d{4}', span_text):
                        parsed_date = self._parse_absolute_date(span_text)
                        if parsed_date:
                            complaint_data['company_response_date'] = parsed_date
                            break
            else:
                # Fallback to old selectors
                response_elem = element.find('div', class_=re.compile('company-response|resposta-empresa', re.I))
                if response_elem:
                    response_text_elem = response_elem.find('p')
                    complaint_data['company_response_text'] = response_text_elem.get_text(strip=True) if response_text_elem else None
                    complaint_data['company_response_date'] = None
                else:
                    complaint_data['company_response_text'] = None
                    complaint_data['company_response_date'] = None

            # Extract customer evaluation using data-testid="complaint-evaluation-interaction"
            # HTML structure: <div data-testid="complaint-evaluation-interaction">
            #   <span>Consideração do consumidor</span>
            #   <span>18/11/2025 às 19:29</span>
            #   <p>Evaluation text...</p>
            # </div>
            evaluation_elem = element.find('div', {'data-testid': 'complaint-evaluation-interaction'})

            if evaluation_elem:
                # Extract evaluation text from <p> tag
                eval_text_elem = evaluation_elem.find('p')
                complaint_data['customer_evaluation'] = eval_text_elem.get_text(strip=True) if eval_text_elem else None

                # Extract evaluation date from spans
                spans = evaluation_elem.find_all('span')
                complaint_data['evaluation_date'] = None
                for span in spans:
                    span_text = span.get_text(strip=True)
                    if '/' in span_text and re.search(r'\d{2}/\d{2}/\d{4}', span_text):
                        parsed_date = self._parse_absolute_date(span_text)
                        if parsed_date:
                            complaint_data['evaluation_date'] = parsed_date
                            break
            else:
                # Fallback to old selectors
                evaluation_elem = element.find('span', {'data-testid': 'customer-evaluation'}) or \
                                element.find('div', class_=re.compile('evaluation|avaliacao', re.I))
                if evaluation_elem:
                    complaint_data['customer_evaluation'] = evaluation_elem.get_text(strip=True)
                else:
                    complaint_data['customer_evaluation'] = None
                complaint_data['evaluation_date'] = None

            # Try to extract external ID (from URL or data attribute)
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                id_match = re.search(r'/(\d+)/?$', href)
                if id_match:
                    complaint_data['external_id'] = id_match.group(1)

            # Add metadata
            complaint_data['scraped_at'] = datetime.now()

            # Validate minimum data
            if not complaint_data.get('text') or len(complaint_data.get('text', '')) < 10:
                logger.warning(f"Complaint has insufficient text, skipping: {complaint_data.get('title', 'N/A')}")
                return None

            return complaint_data

        except Exception as e:
            logger.error(f"Error extracting complaint data: {e}")
            self.errors.append(f"Extraction error: {e}")
            return None

    def _save_debug_html(self, html: str, page: int):
        """Save HTML for debugging purposes"""
        debug_dir = Path("debug_html")
        debug_dir.mkdir(exist_ok=True)
        filepath = debug_dir / f"page_{page}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Debug HTML saved to {filepath}")

    def scrape_complaints(self, save_debug: bool = False) -> List[Dict]:
        """
        Main scraping method

        Args:
            save_debug: If True, saves HTML pages for debugging

        Returns:
            List of complaint dictionaries
        """
        driver = None
        retry_count = 0
        max_retries = 3

        try:
            driver = self._get_driver()
            logger.info(f"Starting scrape of {self.company_url}")

            # Navigate to the first page initially
            base_url = self.company_url.rstrip('/')
            initial_url = f"{base_url}/lista-reclamacoes/?pagina={self.start_page}"

            logger.info(f"Loading initial page: {initial_url}")
            driver.get(initial_url)

            # Wait for initial page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for Cloudflare
            self._wait_for_cloudflare(driver, timeout=30)

            # Wait for JavaScript to load
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(3)  # Give React time to render
            except:
                pass

            # Generate page numbers using step (e.g., 1, 11, 21... with step=10)
            end_page = 1 + (self.max_pages - 1) * self.page_step
            page_numbers = list(range(1, end_page + 1, self.page_step))[:self.max_pages]

            for page_index, page in enumerate(page_numbers, 1):
                logger.info(f"Scraping page {page} ({page_index}/{len(page_numbers)})")

                # For pages after the first, click on the pagination button
                if page > 1:
                    try:
                        target_page = self.start_page + page - 1
                        logger.info(f"Navigating to page {target_page} via pagination click")

                        # Scroll down to make pagination visible
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)

                        # Try multiple strategies to click the next page
                        clicked = False

                        # Strategy 1: Click the specific page number link
                        try:
                            # Look for pagination links with the target page number
                            page_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="pagina="]')
                            for link in page_links:
                                href = link.get_attribute('href') or ''
                                if f'pagina={target_page}' in href:
                                    driver.execute_script("arguments[0].scrollIntoView(true);", link)
                                    time.sleep(0.5)
                                    link.click()
                                    clicked = True
                                    logger.info(f"Clicked pagination link for page {target_page}")
                                    break
                        except Exception as e:
                            logger.debug(f"Strategy 1 failed: {e}")

                        # Strategy 2: Click the "next" button
                        if not clicked:
                            try:
                                next_selectors = [
                                    'button[aria-label*="Próxima"]',
                                    'button[aria-label*="proxima"]',
                                    'a[aria-label*="Próxima"]',
                                    'a[aria-label*="proxima"]',
                                    '[data-testid="next-page"]',
                                    '.pagination-next',
                                    'button:has(svg[data-icon="chevron-right"])',
                                    'a:has(svg[data-icon="chevron-right"])',
                                ]
                                for selector in next_selectors:
                                    try:
                                        next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                                        if next_btn and next_btn.is_displayed():
                                            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                                            time.sleep(0.5)
                                            next_btn.click()
                                            clicked = True
                                            logger.info(f"Clicked next button with selector: {selector}")
                                            break
                                    except:
                                        continue
                            except Exception as e:
                                logger.debug(f"Strategy 2 failed: {e}")

                        # Strategy 3: Use JavaScript to trigger router navigation
                        if not clicked:
                            try:
                                # Trigger Next.js router push
                                url = f"{base_url}/lista-reclamacoes/?pagina={target_page}"
                                script = f"""
                                    if (window.__NEXT_DATA__ && window.next && window.next.router) {{
                                        window.next.router.push('{url}');
                                        return true;
                                    }}
                                    return false;
                                """
                                result = driver.execute_script(script)
                                if result:
                                    clicked = True
                                    logger.info(f"Used Next.js router to navigate to page {target_page}")
                            except Exception as e:
                                logger.debug(f"Strategy 3 failed: {e}")

                        # Strategy 4: Fallback - full page reload (last resort)
                        if not clicked:
                            url = f"{base_url}/lista-reclamacoes/?pagina={target_page}"
                            driver.get(url)
                            logger.info(f"Fallback: Full page reload for page {target_page}")

                        # Wait for content to update
                        time.sleep(3)
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )

                        # Wait for Cloudflare
                        self._wait_for_cloudflare(driver, timeout=30)

                        # Wait for React to render and content to change
                        try:
                            WebDriverWait(driver, 10).until(
                                lambda d: d.execute_script('return document.readyState') == 'complete'
                            )
                            time.sleep(3)  # Additional time for React hydration
                        except:
                            pass

                    except Exception as e:
                        logger.error(f"Error navigating to page {page}: {e}")
                        continue

                # Scroll to load lazy content
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)

                # Get page source
                page_source = driver.page_source

                if save_debug:
                    self._save_debug_html(page_source, page)

                # Parse HTML
                soup = BeautifulSoup(page_source, 'html.parser')

                # Extract company category from page header (applies to all complaints)
                # This is more reliable than trying to extract from individual complaint pages
                page_category = None
                category_link = soup.find('a', {'id': 'info_segmento_hero'})
                if category_link:
                    category_p = category_link.find('p')
                    if category_p:
                        page_category = category_p.get_text(strip=True)
                        logger.info(f"Extracted company category from page: {page_category}")

                # Extract complaints data from __NEXT_DATA__ JSON (more reliable than HTML parsing)
                complaints_from_json = self._extract_complaints_from_json(soup)
                if complaints_from_json:
                    logger.info(f"Extracted {len(complaints_from_json)} complaints from JSON on page {page}")

                    # If fetch_details is enabled, fetch individual pages for complete data
                    if self.fetch_details:
                        logger.info(f"Fetching detailed data for {len(complaints_from_json)} complaints...")

                        # Use same driver sequentially to avoid DNS errors
                        for i, complaint_data in enumerate(complaints_from_json):
                            # Build complaint URL - format: /{company-slug}/{complaint-slug_ID}/
                            url_path = complaint_data.get('url', '')
                            if url_path:
                                if not url_path.startswith('http'):
                                    # Remove any leading slash from url_path
                                    url_path = url_path.lstrip('/')
                                    # Build URL with company slug: /company-slug/complaint-slug/
                                    complaint_url = f"https://www.reclameaqui.com.br/{self.company_slug}/{url_path}/"
                                else:
                                    complaint_url = url_path

                                try:
                                    updated_data = self._fetch_complaint_details_with_driver(driver, complaint_url, complaint_data)
                                    if page_category:
                                        updated_data['category'] = page_category
                                    updated_data['scraped_at'] = datetime.now()
                                    # Remove URL field before saving
                                    updated_data.pop('url', None)
                                    with self._lock:
                                        self.complaints.append(updated_data)
                                    logger.info(f"Progress: {i+1}/{len(complaints_from_json)} complaints processed")

                                    # Small delay between requests
                                    time.sleep(1)
                                except Exception as e:
                                    logger.error(f"Error fetching details: {e}")
                                    # Add basic data on error
                                    if page_category:
                                        complaint_data['category'] = page_category
                                    complaint_data['scraped_at'] = datetime.now()
                                    complaint_data.pop('url', None)
                                    with self._lock:
                                        self.complaints.append(complaint_data)
                            else:
                                # No URL, add with basic data
                                if page_category:
                                    complaint_data['category'] = page_category
                                complaint_data['scraped_at'] = datetime.now()
                                with self._lock:
                                    self.complaints.append(complaint_data)
                    else:
                        # Fast mode: just use basic JSON data
                        for complaint_data in complaints_from_json:
                            if page_category:
                                complaint_data['category'] = page_category
                            complaint_data['scraped_at'] = datetime.now()
                            complaint_data.pop('url', None)  # Remove URL field
                            with self._lock:
                                self.complaints.append(complaint_data)

                    # Call callback for incremental imports if set
                    if self.on_page_complete:
                        # Get the complaints from this page (last N added to self.complaints)
                        page_complaints_count = len(complaints_from_json)
                        if self.fetch_details:
                            page_complaints = self.complaints[-page_complaints_count:] if len(self.complaints) >= page_complaints_count else self.complaints[:]
                        else:
                            page_complaints = complaints_from_json
                        self.on_page_complete(page, page_complaints)

                    # Random delay between pages
                    self._random_delay(self.delay_min, self.delay_max)
                    continue  # Skip the old link-based extraction

                # Fallback: Use the old selector-based approach if JSON extraction fails
                # Use the correct selector for complaint links from the list page
                # This gets the links to individual complaint pages
                complaint_links = []
                link_selector = 'div.sc-1sm4sxr-0 a'

                # Find all complaint links
                link_elements = soup.select(link_selector)

                if link_elements:
                    logger.info(f"Found {len(link_elements)} complaint links on page {page}")

                    # Process each complaint link
                    for link_elem in link_elements[:10]:  # Limit to 10 per page to avoid overload
                        try:
                            complaint_url = link_elem.get('href', '')
                            # Complaint URLs match pattern: /COMPANY-NAME/complaint-title_ID/
                            # Example: /magazine-luiza-loja-online/atraso-na-entrega_RAK1x8bO1QIHfH11/
                            if complaint_url and complaint_url.count('/') >= 3 and not any(x in complaint_url for x in ['lista-reclamacoes', 'sobre', 'cupons', 'compare', '#']):
                                # Make absolute URL
                                if not complaint_url.startswith('http'):
                                    complaint_url = f"https://www.reclameaqui.com.br{complaint_url}"

                                complaint_links.append(complaint_url)
                        except Exception as e:
                            logger.error(f"Error extracting link: {e}")

                # Now fetch each complaint page individually using parallel workers
                complaint_elements = []
                logger.info(f"Fetching {len(complaint_links)} complaint pages in parallel with {self.max_workers} workers...")

                # Use ThreadPoolExecutor for parallel fetching
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    # Submit all fetch tasks
                    future_to_url = {
                        executor.submit(self._fetch_single_complaint, url): url
                        for url in complaint_links
                    }

                    # Collect results as they complete
                    completed_count = 0
                    for future in as_completed(future_to_url):
                        completed_count += 1
                        complaint_url = future_to_url[future]
                        try:
                            complaint_soup = future.result()
                            if complaint_soup:
                                complaint_elements.append(complaint_soup)
                                logger.info(f"Progress: {completed_count}/{len(complaint_links)} complaints fetched")
                        except Exception as e:
                            logger.error(f"Thread exception for {complaint_url}: {e}")

                if not complaint_elements:
                    logger.warning(f"No complaints found on page {page}")
                    logger.debug(f"Page title: {soup.title.string if soup.title else 'N/A'}")
                    # Save HTML for analysis if no complaints found
                    if save_debug or page == 1:
                        self._save_debug_html(page_source, page)

                # Extract data from each complaint
                for idx, elem in enumerate(complaint_elements):
                    try:
                        complaint = self._extract_complaint_data(elem, page_source)
                        if complaint:
                            # Apply page category as fallback if complaint doesn't have one
                            if not complaint.get('category') and page_category:
                                complaint['category'] = page_category
                                logger.debug(f"Applied page category '{page_category}' to complaint")

                            self.complaints.append(complaint)
                            logger.debug(f"Extracted complaint {idx + 1}: {complaint.get('title', 'N/A')[:50]}")
                    except Exception as e:
                        logger.error(f"Error processing complaint {idx + 1} on page {page}: {e}")
                        self.errors.append(f"Page {page}, complaint {idx + 1}: {e}")

                # Random delay between pages
                if page < self.max_pages:
                    self._random_delay()

        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            self.errors.append(f"Fatal error: {e}")

        finally:
            if driver:
                driver.quit()
                logger.info("WebDriver closed")

        logger.info(f"Scraping completed. Collected {len(self.complaints)} complaints")
        if self.errors:
            logger.warning(f"Encountered {len(self.errors)} errors during scraping")

        return self.complaints

    def get_errors(self) -> List[str]:
        """Return list of errors encountered during scraping"""
        return self.errors
