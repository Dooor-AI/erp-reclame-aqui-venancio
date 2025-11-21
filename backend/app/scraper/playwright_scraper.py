"""
Optimized Playwright-based scraper for Reclame Aqui
Much faster than Selenium - uses async operations and parallel processing
"""
import asyncio
import logging
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PlaywrightReclameAquiScraper:
    """Fast async scraper using Playwright"""

    def __init__(self, company_url: str, max_pages: int = 10, delay_min: float = 1.0, delay_max: float = 2.0, max_concurrent: int = 5):
        self.company_url = company_url
        self.max_pages = max_pages
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_concurrent = max_concurrent  # Concurrent browser contexts
        self.complaints = []
        self.errors = []

    async def scrape_complaints(self, save_debug: bool = False) -> List[Dict]:
        """
        Main scraping method using Playwright
        Returns list of complaint dictionaries
        """
        async with async_playwright() as p:
            # Launch browser with Chromium (faster and better supported than Firefox/WebKit)
            browser = await p.chromium.launch(
                headless=True,  # Playwright's headless is undetectable
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            )

            try:
                # Create browser context with extra headers to avoid detection
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    extra_http_headers={
                        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                    }
                )

                # Navigate to first page to get total pages and complaint links
                page = await context.new_page()
                logger.info(f"Starting scrape of {self.company_url}")

                all_complaint_links = []

                # Scrape all listing pages to collect complaint URLs
                for page_num in range(1, self.max_pages + 1):
                    # Build correct URL format: /lista-reclamacoes/?pagina=X
                    base_url = self.company_url.rstrip('/')
                    page_url = f"{base_url}/lista-reclamacoes/?pagina={page_num}"

                    logger.info(f"Scraping page {page_num}/{self.max_pages}: {page_url}")

                    try:
                        await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(3)  # Wait for dynamic content and React to render

                        # Scroll to load lazy content
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(1)
                        await page.evaluate("window.scrollTo(0, 0)")
                        await asyncio.sleep(1)

                        # Wait for complaints to load - using correct selector
                        try:
                            await page.wait_for_selector('div.sc-1sm4sxr-0 a', timeout=10000)
                        except:
                            logger.warning(f"No complaints found on page {page_num}")
                            break

                        # Get page content
                        content = await page.content()

                        # Save debug HTML if requested
                        if save_debug:
                            debug_dir = Path("debug_html")
                            debug_dir.mkdir(exist_ok=True)
                            debug_file = debug_dir / f"playwright_page_{page_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            logger.info(f"Debug HTML saved to {debug_file}")

                        # Parse with BeautifulSoup to extract complaint links
                        soup = BeautifulSoup(content, 'html.parser')

                        # Find all complaint links using the correct selector
                        complaint_links = soup.select('div.sc-1sm4sxr-0 a')

                        if not complaint_links:
                            logger.warning(f"No complaint links found on page {page_num}")
                            break

                        page_links = []
                        for link in complaint_links:
                            href = link.get('href', '')
                            # Limit to 10 per page like the original scraper
                            if len(page_links) >= 10:
                                break

                            if href:
                                # Build full URL
                                full_url = f"https://www.reclameaqui.com.br{href}" if not href.startswith('http') else href

                                # Avoid duplicates
                                if full_url not in [l['url'] for l in page_links]:
                                    # Extract category from listing page (much more reliable!)
                                    category = None

                                    # Find the parent complaint card
                                    parent = link.find_parent('div', class_=re.compile(r'sc-1sm4sxr-0', re.I))
                                    if parent:
                                        # Look for category link in the same card
                                        cat_link = parent.find('a', {'id': 'info_segmento_hero'})
                                        if cat_link:
                                            cat_p = cat_link.find('p')
                                            if cat_p:
                                                category = cat_p.get_text(strip=True)

                                    # Try to get category from siblings if not found in parent
                                    if not category:
                                        # Search siblings/nearby elements
                                        parent_div = link.find_parent('div')
                                        if parent_div:
                                            cat_link = parent_div.find('a', {'id': 'info_segmento_hero'})
                                            if cat_link:
                                                cat_p = cat_link.find('p')
                                                if cat_p:
                                                    category = cat_p.get_text(strip=True)

                                    page_links.append({
                                        'url': full_url,
                                        'category_from_listing': category  # Save category from listing
                                    })

                        logger.info(f"Found {len(page_links)} complaint links on page {page_num}")
                        all_complaint_links.extend(page_links)

                        # Small delay between pages
                        await asyncio.sleep(1)

                    except Exception as e:
                        logger.error(f"Error scraping page {page_num}: {e}")
                        self.errors.append(f"Page {page_num}: {str(e)}")
                        continue

                await page.close()

                logger.info(f"Total complaint links collected: {len(all_complaint_links)}")

                # Now fetch complaint details in parallel (much faster!)
                logger.info(f"Fetching {len(all_complaint_links)} complaint pages in parallel with {self.max_concurrent} workers...")

                # Create semaphore to limit concurrent requests
                semaphore = asyncio.Semaphore(self.max_concurrent)

                async def fetch_complaint(link_data: Dict):
                    """Fetch a single complaint page"""
                    async with semaphore:
                        complaint_url = link_data['url']
                        try:
                            # Create new page for this complaint
                            page = await context.new_page()

                            try:
                                logger.info(f"Fetching complaint: {complaint_url[:80]}...")
                                await page.goto(complaint_url, wait_until='domcontentloaded', timeout=30000)
                                await asyncio.sleep(1)

                                # Get page content
                                content = await page.content()
                                soup = BeautifulSoup(content, 'html.parser')

                                # Parse complaint data
                                complaint_data = self._parse_complaint_page(soup, complaint_url)

                                # If category not found on detail page, use the one from listing
                                if not complaint_data.get('category') and link_data.get('category_from_listing'):
                                    complaint_data['category'] = link_data['category_from_listing']
                                    logger.debug(f"Using category from listing: {complaint_data['category']}")

                                if complaint_data:
                                    logger.info(f"Successfully parsed complaint from {complaint_url[:80]}...")
                                    return complaint_data
                                else:
                                    self.errors.append(f"{complaint_url}: Failed to parse")
                                    return None

                            finally:
                                await page.close()

                        except Exception as e:
                            logger.error(f"Fetch error for {complaint_url}: {e}")
                            self.errors.append(f"{complaint_url}: {str(e)}")
                            return None

                # Fetch all complaints in parallel
                tasks = [fetch_complaint(link_data) for link_data in all_complaint_links]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Filter out None and exceptions
                self.complaints = [r for r in results if r and not isinstance(r, Exception)]

                logger.info(f"Successfully fetched {len(self.complaints)} complaints out of {len(all_complaint_links)}")

            finally:
                await context.close()
                await browser.close()

        return self.complaints

    def _parse_complaint_page(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Parse complaint data from BeautifulSoup object"""
        try:
            complaint_data = {
                'external_id': url.split('/')[-1] if '/' in url else None,
                'scraped_at': datetime.now()
            }

            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            complaint_data['title'] = title_elem.get_text(strip=True) if title_elem else None

            # Extract complaint text
            text_elem = soup.find('div', {'data-testid': 'complaint-description'}) or \
                       soup.find('div', class_=re.compile(r'complaint-text|description|texto-reclamacao', re.I)) or \
                       soup.find('p', class_=re.compile(r'complaint-text|description', re.I))

            if text_elem:
                complaint_data['text'] = text_elem.get_text(strip=True)
            else:
                # Fallback: find all paragraphs in main content
                main_content = soup.find('main') or soup.find('article') or soup.body
                if main_content:
                    paragraphs = main_content.find_all('p', limit=10)
                    complaint_data['text'] = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                else:
                    complaint_data['text'] = None

            # Extract user name
            user_elem = soup.find('span', {'data-testid': 'complaint-author'}) or \
                       soup.find('div', class_=re.compile(r'author|user-name|autor', re.I)) or \
                       soup.find('p', class_=re.compile(r'author|user', re.I))
            complaint_data['user_name'] = user_elem.get_text(strip=True) if user_elem else 'Anônimo'

            # Extract date
            date_elem = soup.find('time') or \
                       soup.find('span', {'data-testid': 'complaint-date'}) or \
                       soup.find('div', class_=re.compile(r'date|data', re.I))

            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                try:
                    complaint_data['complaint_date'] = self._parse_relative_date(date_str)
                except:
                    complaint_data['complaint_date'] = None
            else:
                complaint_data['complaint_date'] = None

            # Extract status
            status_elem = soup.find('span', {'data-testid': 'complaint-status'}) or \
                         soup.find('div', class_=re.compile(r'status|estado', re.I)) or \
                         soup.find('span', class_=re.compile(r'status|badge', re.I))
            complaint_data['status'] = status_elem.get_text(strip=True) if status_elem else 'Não respondida'

            # Extract location
            location_elem = soup.find('span', {'data-testid': 'complaint-location'}) or \
                          soup.find('div', class_=re.compile(r'location|local|cidade', re.I))
            complaint_data['location'] = location_elem.get_text(strip=True) if location_elem else None

            # Extract category (try detail page first)
            category_elem = soup.find('a', {'id': 'info_segmento_hero'})
            if category_elem:
                category_p = category_elem.find('p')
                if category_p:
                    complaint_data['category'] = category_p.get_text(strip=True)
                else:
                    complaint_data['category'] = None
            else:
                # Try other selectors
                category_elem = soup.find('a', href=re.compile(r'/segmentos?/', re.I))
                if category_elem:
                    complaint_data['category'] = category_elem.get_text(strip=True)
                else:
                    complaint_data['category'] = None

            # Extract company response
            response_elem = soup.find('div', {'data-testid': 'company-response'}) or \
                          soup.find('div', class_=re.compile(r'company-response|resposta-empresa', re.I))

            if response_elem:
                response_text_elem = response_elem.find('p') or response_elem.find('div', class_=re.compile(r'text|content'))
                complaint_data['company_response_text'] = response_text_elem.get_text(strip=True) if response_text_elem else None

                response_date_elem = response_elem.find('time') or response_elem.find('span', class_=re.compile(r'date'))
                if response_date_elem:
                    date_str = response_date_elem.get('datetime') or response_date_elem.get_text(strip=True)
                    try:
                        complaint_data['company_response_date'] = self._parse_relative_date(date_str)
                    except:
                        complaint_data['company_response_date'] = None
                else:
                    complaint_data['company_response_date'] = None
            else:
                complaint_data['company_response_text'] = None
                complaint_data['company_response_date'] = None

            # Extract customer evaluation
            eval_elem = soup.find('span', {'data-testid': 'customer-evaluation'}) or \
                       soup.find('div', class_=re.compile(r'evaluation|avaliacao', re.I))
            complaint_data['customer_evaluation'] = eval_elem.get_text(strip=True) if eval_elem else None

            return complaint_data

        except Exception as e:
            logger.error(f"Error parsing complaint page: {e}")
            return None

    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative dates like 'há 2 dias' to datetime"""
        try:
            # Try ISO format first
            if 'T' in date_str or '-' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00').split('+')[0].split('T')[0])

            # Parse Brazilian relative dates
            date_str = date_str.lower()
            now = datetime.now()

            # há X horas
            if 'hora' in date_str or 'hour' in date_str:
                hours = int(re.search(r'\d+', date_str).group())
                return now - timedelta(hours=hours)

            # há X dias
            elif 'dia' in date_str or 'day' in date_str:
                days = int(re.search(r'\d+', date_str).group())
                return now - timedelta(days=days)

            # há X semanas
            elif 'semana' in date_str or 'week' in date_str:
                weeks = int(re.search(r'\d+', date_str).group())
                return now - timedelta(weeks=weeks)

            # há X meses
            elif 'mês' in date_str or 'mes' in date_str or 'month' in date_str:
                months = int(re.search(r'\d+', date_str).group())
                return now - timedelta(days=months * 30)

            # Default: try to parse as date
            else:
                # Try common formats
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(date_str.split()[0], fmt)
                    except:
                        continue

                return None

        except:
            return None

    def get_errors(self) -> List[str]:
        """Return list of errors encountered"""
        return self.errors
