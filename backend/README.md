# Venâncio RPA - Backend API

Backend system for scraping and managing Reclame Aqui complaints for Venâncio.

## Features

- Web scraping of Reclame Aqui complaints
- SQLite/PostgreSQL database storage
- REST API for data access
- Automated polling system
- AI analysis integration (Chat B)
- Response generation integration (Chat C)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and adjust settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration.

### 5. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

Once running, access:

- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### Main Endpoints

- `GET /complaints` - List complaints with filters
- `GET /complaints/{id}` - Get complaint details
- `GET /complaints/stats` - Get statistics
- `POST /complaints` - Create complaint (testing)
- `PATCH /complaints/{id}/analysis` - Update AI analysis
- `PATCH /complaints/{id}/response` - Update response data

## Database

The system uses SQLite by default for simplicity. To use PostgreSQL:

1. Install PostgreSQL
2. Create database: `createdb venancio_rpa`
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/venancio_rpa
   ```

## Scraper

The scraper runs automatically based on the polling interval configured in `.env`.

To run manually:
```bash
POST http://localhost:8000/scrape/run
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── complaints.py    # API endpoints
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── database.py         # Database setup
│   ├── db/
│   │   ├── base.py            # Base imports
│   │   ├── crud.py            # Database operations
│   │   └── models.py          # SQLAlchemy models
│   ├── schemas/
│   │   └── complaint.py       # Pydantic schemas
│   ├── scraper/
│   │   ├── reclame_aqui_scraper.py  # Scraper logic
│   │   └── scheduler.py             # Polling system
│   └── main.py                # FastAPI application
├── tests/                     # Tests
├── requirements.txt          # Dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Development

### Run Tests

```bash
pytest
```

### Code Style

Follow PEP 8. Use:

```bash
black .
flake8 .
```

## Integration with Other Chats

- **Chat B (AI Analysis):** Uses `PATCH /complaints/{id}/analysis` to store sentiment analysis
- **Chat C (Response Generation):** Uses `PATCH /complaints/{id}/response` to store responses and coupons
- **Chat D (Frontend):** Consumes all GET endpoints to display data
- **Chat E (Documentation):** Documents this API

## Troubleshooting

### ChromeDriver Issues

If Selenium fails, ensure ChromeDriver is installed:

```bash
# Download from: https://chromedriver.chromium.org/
# Add to PATH or place in project root
```

### Database Connection Errors

Check DATABASE_URL in `.env` and ensure database exists.

### Import Errors

Ensure virtual environment is activated and dependencies are installed.

## License

Internal project for Venâncio.
