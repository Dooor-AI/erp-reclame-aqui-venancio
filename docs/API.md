# VenÃ¢ncio RPA API Documentation

**Version:** 1.0.0
**API Title:** VenÃ¢ncio RPA API
**Description:** API para gerenciamento de reclamaÃ§Ãµes da VenÃ¢ncio no Reclame Aqui

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Endpoints](#endpoints)
   - [Complaints](#complaints)
   - [Analytics](#analytics)
   - [Responses](#responses)
   - [Scraper](#scraper)
   - [Health & Status](#health--status)

---

## Overview

The VenÃ¢ncio RPA API is a complaint management system integrated with Reclame Aqui. It provides endpoints for:

- **Managing Complaints**: CRUD operations for complaints scraped from Reclame Aqui
- **AI Analysis**: Sentiment analysis, classification, entity extraction, and urgency scoring
- **Response Generation**: AI-powered response generation for complaints with manual editing capabilities
- **Analytics**: Comprehensive statistics and insights about complaints
- **Automatic Scraping**: Background job that automatically scrapes new complaints

### Key Features

- Automatic complaint scraping from Reclame Aqui
- AI-powered sentiment analysis and classification
- Urgency scoring for prioritization
- AI-generated responses with manual editing
- Discount coupon generation
- Comprehensive analytics and statistics
- Batch analysis capabilities

---

## Base URL

```
http://localhost:8000
```

For production, update the host and port in configuration.

---

## Authentication

**Current Status:** No authentication required

This API currently operates without authentication. In production, implement:

- Bearer token authentication
- API key authentication
- OAuth 2.0
- JWT tokens

**Recommendation:** Add authentication middleware for production deployments.

---

## Error Handling

All errors follow a standard format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status Code | Description | Scenario |
|-------------|-------------|----------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request creating a resource |
| 400 | Bad Request | Invalid parameters or malformed request |
| 404 | Not Found | Resource does not exist |
| 500 | Internal Server Error | Server error or AI service failure |

### Example Error Response

```json
{
  "detail": "ReclamaÃ§Ã£o nÃ£o encontrada"
}
```

---

## Rate Limiting

**Current Status:** No rate limiting implemented

### Recommendations for Production

1. **Per-Endpoint Limits:**
   - Analysis endpoints: 10 requests/minute
   - Read endpoints: 100 requests/minute
   - Batch analysis: 1 request/hour

2. **Implementation Options:**
   - SlowAPI (FastAPI-compatible rate limiter)
   - Redis-based rate limiting
   - Custom middleware

3. **Headers to Implement:**
   ```
   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 95
   X-RateLimit-Reset: 1637187245
   ```

---

## Endpoints

### Complaints

Manage complaints scraped from Reclame Aqui.

#### List Complaints

```http
GET /complaints/
```

**Description:** List all complaints with optional filtering

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip (pagination) |
| limit | integer | 100 | Maximum number of records to return (max 1000) |
| sentiment | string | null | Filter by sentiment: Negativo, Neutro, Positivo |
| status | string | null | Filter by status: Respondida, NÃ£o respondida, Resolvida |

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Produto com defeito",
    "text": "Comprei um produto que chegou com defeito...",
    "user_name": "JoÃ£o Silva",
    "complaint_date": "2024-01-15T10:30:00",
    "status": "NÃ£o respondida",
    "category": "Qualidade do Produto",
    "location": "SÃ£o Paulo",
    "external_id": "reclame-aqui-12345",
    "sentiment": "Negativo",
    "sentiment_score": 8.5,
    "urgency_score": 7.2,
    "classification": ["Produto Defeituoso", "Atendimento"],
    "entities": {
      "product": "Camiseta",
      "issue": "Rasgada"
    },
    "response_generated": null,
    "coupon_code": null,
    "coupon_discount": null,
    "response_sent": false,
    "scraped_at": "2024-01-15T11:00:00",
    "analyzed_at": null,
    "created_at": "2024-01-15T11:00:00",
    "updated_at": null
  }
]
```

**Error Responses:**

- `400 Bad Request` - Invalid pagination parameters

---

#### Get Complaint Statistics

```http
GET /complaints/stats
```

**Description:** Get aggregated statistics about complaints

**Response:** `200 OK`

```json
{
  "total": 150,
  "by_sentiment": {
    "Negativo": 95,
    "Neutro": 35,
    "Positivo": 20
  },
  "by_status": {
    "NÃ£o respondida": 60,
    "Respondida": 70,
    "Resolvida": 20
  },
  "by_category": {
    "Qualidade do Produto": 45,
    "Atendimento": 35,
    "Entrega": 30,
    "Outro": 40
  },
  "avg_urgency": 6.8
}
```

---

#### Get Complaint Detail

```http
GET /complaints/{complaint_id}
```

**Description:** Get detailed information about a specific complaint

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Response:** `200 OK`

```json
{
  "id": 1,
  "title": "Produto com defeito",
  "text": "Comprei um produto que chegou com defeito...",
  "user_name": "JoÃ£o Silva",
  "complaint_date": "2024-01-15T10:30:00",
  "status": "NÃ£o respondida",
  "category": "Qualidade do Produto",
  "location": "SÃ£o Paulo",
  "external_id": "reclame-aqui-12345",
  "sentiment": "Negativo",
  "sentiment_score": 8.5,
  "urgency_score": 7.2,
  "classification": ["Produto Defeituoso", "Atendimento"],
  "entities": {
    "product": "Camiseta",
    "issue": "Rasgada"
  },
  "response_generated": null,
  "coupon_code": null,
  "coupon_discount": null,
  "response_sent": false,
  "scraped_at": "2024-01-15T11:00:00",
  "analyzed_at": null,
  "created_at": "2024-01-15T11:00:00",
  "updated_at": null
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist

---

#### Create Complaint

```http
POST /complaints/
```

**Description:** Create a new complaint manually (primarily for testing purposes; in production, complaints are created by the scraper)

**Request Body:**

```json
{
  "title": "Produto com defeito",
  "text": "Comprei um produto que chegou com defeito e não funciona corretamente.",
  "user_name": "JoÃ£o Silva",
  "complaint_date": "2024-01-15T10:30:00",
  "status": "NÃ£o respondida",
  "category": "Qualidade do Produto",
  "location": "SÃ£o Paulo",
  "external_id": "reclame-aqui-12345"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "title": "Produto com defeito",
  "text": "Comprei um produto que chegou com defeito...",
  "user_name": "JoÃ£o Silva",
  "complaint_date": "2024-01-15T10:30:00",
  "status": "NÃ£o respondida",
  "category": "Qualidade do Produto",
  "location": "SÃ£o Paulo",
  "external_id": "reclame-aqui-12345",
  "sentiment": null,
  "sentiment_score": null,
  "urgency_score": null,
  "classification": null,
  "entities": null,
  "response_generated": null,
  "coupon_code": null,
  "coupon_discount": null,
  "response_sent": false,
  "scraped_at": "2024-01-15T11:00:00",
  "analyzed_at": null,
  "created_at": "2024-01-15T11:00:00",
  "updated_at": null
}
```

---

#### Update Complaint Analysis

```http
PATCH /complaints/{complaint_id}/analysis
```

**Description:** Update complaint with AI analysis data (used by Chat B)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| sentiment | string | Sentiment classification: Negativo, Neutro, Positivo |
| sentiment_score | number | Sentiment score (0-10) |
| urgency_score | number | Urgency score (0-10) |
| classification | array | List of categories |
| entities | object | Extracted entities |

**Request Example (form parameters):**

```
PATCH /complaints/1/analysis?sentiment=Negativo&sentiment_score=8.5&urgency_score=7.2&classification=["Produto Defeituoso","Atendimento"]&entities={"product":"Camiseta","issue":"Rasgada"}
```

**Response:** `200 OK`

```json
{
  "message": "Analysis updated",
  "complaint_id": 1
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist

---

#### Update Complaint Response

```http
PATCH /complaints/{complaint_id}/response
```

**Description:** Update complaint with response data (used by Chat C)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| response_generated | string | AI-generated response |
| response_edited | string | Manually edited response |
| coupon_code | string | Generated coupon code |
| coupon_discount | integer | Discount percentage (0-100) |

**Request Example:**

```
PATCH /complaints/1/response?response_generated=Sentimos muito...&coupon_code=PROMO10&coupon_discount=10
```

**Response:** `200 OK`

```json
{
  "message": "Response updated",
  "complaint_id": 1
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist

---

### Analytics

Get insights and statistics about complaints.

#### Analyze Single Complaint

```http
POST /analytics/analyze/{complaint_id}
```

**Description:** Analyze a specific complaint with full AI pipeline (sentiment analysis, classification, entity extraction, urgency scoring)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint to analyze |

**Response:** `200 OK`

```json
{
  "complaint_id": 1,
  "sentiment": "Negativo",
  "sentiment_score": 8.5,
  "classification": ["Produto Defeituoso", "Atendimento"],
  "entities": {
    "product": "Camiseta",
    "issue": "Rasgada"
  },
  "urgency_score": 7.2,
  "analysis_timestamp": "2024-01-15T12:00:00"
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist
- `500 Internal Server Error` - AI service failure

---

#### Analyze Batch

```http
POST /analytics/analyze/batch
```

**Description:** Analyze all unanalyzed complaints (or up to specified limit)

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Maximum number of complaints to analyze (optional) |

**Response:** `200 OK`

```json
{
  "total_analyzed": 45,
  "successful": 45,
  "failed": 0,
  "skipped": 0,
  "average_processing_time_seconds": 2.3,
  "timestamp": "2024-01-15T12:30:00"
}
```

**Error Responses:**

- `500 Internal Server Error` - Batch analysis failure

---

#### Sentiment Statistics

```http
GET /analytics/stats/sentiment
```

**Description:** Get sentiment distribution statistics

**Response:** `200 OK`

```json
{
  "total_analyzed": 150,
  "by_sentiment": [
    {
      "sentiment": "Negativo",
      "count": 95,
      "percentage": 63.33,
      "avg_score": 8.2,
      "min_score": 6.5,
      "max_score": 10.0
    },
    {
      "sentiment": "Neutro",
      "count": 35,
      "percentage": 23.33,
      "avg_score": 5.1,
      "min_score": 4.0,
      "max_score": 6.5
    },
    {
      "sentiment": "Positivo",
      "count": 20,
      "percentage": 13.33,
      "avg_score": 2.3,
      "min_score": 0.5,
      "max_score": 3.8
    }
  ]
}
```

---

#### Category Statistics

```http
GET /analytics/stats/categories
```

**Description:** Get complaint distribution by categories

**Response:** `200 OK`

```json
{
  "total_classified": 150,
  "categories": [
    {
      "category": "Qualidade do Produto",
      "count": 45,
      "percentage": 30.0
    },
    {
      "category": "Atendimento",
      "count": 35,
      "percentage": 23.33
    },
    {
      "category": "Entrega",
      "count": 30,
      "percentage": 20.0
    },
    {
      "category": "Outro",
      "count": 40,
      "percentage": 26.67
    }
  ],
  "top_5": [
    {
      "category": "Qualidade do Produto",
      "count": 45,
      "percentage": 30.0
    },
    {
      "category": "Atendimento",
      "count": 35,
      "percentage": 23.33
    },
    {
      "category": "Entrega",
      "count": 30,
      "percentage": 20.0
    },
    {
      "category": "Outro",
      "count": 40,
      "percentage": 26.67
    },
    {
      "category": "Frete",
      "count": 20,
      "percentage": 13.33
    }
  ]
}
```

---

#### Urgency Statistics

```http
GET /analytics/stats/urgency
```

**Description:** Get urgent complaints (high urgency score)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| min_score | number | 7.0 | Minimum urgency score threshold |
| limit | integer | 10 | Maximum number of urgent complaints to return |

**Response:** `200 OK`

```json
{
  "avg_urgency_score": 6.8,
  "total_urgent": 45,
  "total_analyzed": 150,
  "urgent_percentage": 30.0,
  "urgent_complaints": [
    {
      "id": 5,
      "title": "Produto nÃ£o chegou",
      "urgency_score": 9.8,
      "sentiment": "Negativo",
      "sentiment_score": 9.2,
      "categories": ["Entrega"],
      "complaint_date": "2024-01-14T15:30:00"
    },
    {
      "id": 12,
      "title": "Cliente muito insatisfeito",
      "urgency_score": 9.5,
      "sentiment": "Negativo",
      "sentiment_score": 8.9,
      "categories": ["Atendimento"],
      "complaint_date": "2024-01-15T09:00:00"
    }
  ]
}
```

---

#### Statistics Overview

```http
GET /analytics/stats/overview
```

**Description:** Get comprehensive overview of all statistics

**Response:** `200 OK`

```json
{
  "totals": {
    "total_complaints": 200,
    "analyzed": 150,
    "not_analyzed": 50,
    "analysis_rate": 75.0
  },
  "averages": {
    "sentiment_score": 6.8,
    "urgency_score": 6.5
  },
  "sentiment_distribution": {
    "Negativo": 95,
    "Neutro": 35,
    "Positivo": 20
  }
}
```

---

### Responses

Generate and manage complaint responses.

#### Generate Response

```http
POST /responses/generate/{complaint_id}
```

**Description:** Generate AI response for a specific complaint

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Response:** `200 OK`

```json
{
  "complaint_id": 1,
  "response_generated": "Sentimos muito pelas dificuldades que enfrentou. Gostaremos de resolver isso para você...",
  "coupon_code": "PROMO10",
  "coupon_discount": 10,
  "timestamp": "2024-01-15T12:00:00"
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist
- `500 Internal Server Error` - Response generation failure

---

#### Get Response

```http
GET /responses/{complaint_id}
```

**Description:** Get generated and edited responses for a complaint

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Response:** `200 OK`

```json
{
  "complaint_id": 1,
  "response_generated": "Sentimos muito pelas dificuldades que enfrentou...",
  "response_edited": "Sentimos muito pelas dificuldades que enfrentou. Estamos preparando uma solução especial para você...",
  "coupon_code": "PROMO10",
  "coupon_discount": 10,
  "response_sent": false
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist

---

#### Edit Response

```http
PUT /responses/{complaint_id}
```

**Description:** Manually edit a generated response before sending

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Request Body:**

```json
{
  "edited_response": "Sentimos muito pelas dificuldades que enfrentou. Gostaria de oferecer um desconto especial de 20% para você compensar..."
}
```

**Response:** `200 OK`

```json
{
  "message": "Resposta editada com sucesso"
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist

---

#### Mark Response as Sent

```http
POST /responses/{complaint_id}/send
```

**Description:** Mark a response as sent (MOCK endpoint for testing)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| complaint_id | integer | The ID of the complaint |

**Response:** `200 OK`

```json
{
  "message": "Resposta marcada como enviada"
}
```

**Error Responses:**

- `404 Not Found` - Complaint does not exist

---

### Scraper

Manage background scraping tasks.

#### Manually Trigger Scraper

```http
POST /scrape/run
```

**Description:** Manually trigger a scraping job to run in the background (for testing purposes)

**Response:** `200 OK`

```json
{
  "message": "Scraping job started in background",
  "note": "Check logs for progress"
}
```

**Notes:**
- The scraper runs asynchronously in the background
- Monitor logs for progress and any errors
- In production, scraping runs automatically every 6 hours

---

### Health & Status

#### Root Endpoint

```http
GET /
```

**Description:** Get API information

**Response:** `200 OK`

```json
{
  "message": "VenÃ¢ncio RPA API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

#### Health Check

```http
GET /health
```

**Description:** Check API health status

**Response:** `200 OK`

```json
{
  "status": "ok"
}
```

---

## Data Models

### Complaint

Complete complaint object with all fields:

```json
{
  "id": 1,
  "title": "string (up to 500 characters)",
  "text": "string (complaint text)",
  "user_name": "string",
  "complaint_date": "datetime",
  "status": "string (Respondida | NÃ£o respondida | Resolvida)",
  "category": "string",
  "location": "string",
  "external_id": "string (unique Reclame Aqui ID)",
  "sentiment": "string (Negativo | Neutro | Positivo)",
  "sentiment_score": "number (0-10)",
  "urgency_score": "number (0-10)",
  "classification": ["string"],
  "entities": {
    "string": "string"
  },
  "response_generated": "string",
  "response_edited": "string",
  "coupon_code": "string",
  "coupon_discount": "integer (0-100)",
  "response_sent": "boolean",
  "scraped_at": "datetime",
  "analyzed_at": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Complaint Statistics

Aggregated statistics about complaints:

```json
{
  "total": "integer",
  "by_sentiment": {
    "string": "integer"
  },
  "by_status": {
    "string": "integer"
  },
  "by_category": {
    "string": "integer"
  },
  "avg_urgency": "number"
}
```

---

## Integration Examples

### Example 1: Fetch and Analyze a Complaint

```bash
# Get a complaint
curl -X GET http://localhost:8000/complaints/1

# Analyze it
curl -X POST http://localhost:8000/analytics/analyze/1

# Generate a response
curl -X POST http://localhost:8000/responses/generate/1

# Get the generated response
curl -X GET http://localhost:8000/responses/1

# Edit the response
curl -X PUT http://localhost:8000/responses/1 \
  -H "Content-Type: application/json" \
  -d '{"edited_response": "Your edited response here..."}'

# Mark as sent
curl -X POST http://localhost:8000/responses/1/send
```

### Example 2: Get Analytics Overview

```bash
curl -X GET http://localhost:8000/analytics/stats/overview

curl -X GET http://localhost:8000/analytics/stats/sentiment

curl -X GET http://localhost:8000/analytics/stats/categories

curl -X GET http://localhost:8000/analytics/stats/urgency?min_score=7.0&limit=10
```

### Example 3: Batch Analysis

```bash
# Analyze all unanalyzed complaints
curl -X POST http://localhost:8000/analytics/analyze/batch

# Analyze up to 50 complaints
curl -X POST http://localhost:8000/analytics/analyze/batch?limit=50
```

---

## Database Schema Overview

### Complaints Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | No | Primary key |
| title | VARCHAR(500) | No | Complaint title |
| text | TEXT | No | Complaint full text |
| user_name | VARCHAR(200) | Yes | Complaint author |
| complaint_date | DATETIME | Yes | When complaint was made |
| status | VARCHAR(100) | Yes | Current status |
| category | VARCHAR(200) | Yes | Category classification |
| location | VARCHAR(200) | Yes | Location |
| external_id | VARCHAR(100) | Yes | Reclame Aqui ID |
| sentiment | VARCHAR(50) | Yes | Sentiment classification |
| sentiment_score | FLOAT | Yes | Sentiment score (0-10) |
| classification | JSON | Yes | Array of categories |
| entities | JSON | Yes | Extracted entities |
| urgency_score | FLOAT | Yes | Urgency score (0-10) |
| response_generated | TEXT | Yes | AI-generated response |
| response_edited | TEXT | Yes | Manually edited response |
| coupon_code | VARCHAR(50) | Yes | Discount coupon code |
| coupon_discount | INTEGER | Yes | Discount percentage |
| response_sent | BOOLEAN | No (default: false) | Response sent flag |
| response_sent_at | DATETIME | Yes | When response was sent |
| scraped_at | DATETIME | No | When scraped |
| analyzed_at | DATETIME | Yes | When analyzed |
| created_at | DATETIME | No | Record creation time |
| updated_at | DATETIME | Yes | Record update time |

### Coupons Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | No | Primary key |
| code | VARCHAR(50) | No | Unique coupon code |
| discount_percent | INTEGER | No | Discount percentage |
| complaint_id | INTEGER | Yes | Foreign key to complaint |
| valid_from | DATETIME | No | Validity start date |
| valid_until | DATETIME | No | Validity end date |
| is_used | BOOLEAN | No (default: false) | Usage status |
| used_at | DATETIME | Yes | When coupon was used |
| created_at | DATETIME | No | Creation timestamp |

---

## Best Practices

### 1. Pagination

When fetching large lists of complaints, use pagination:

```bash
curl -X GET "http://localhost:8000/complaints/?skip=0&limit=50"
curl -X GET "http://localhost:8000/complaints/?skip=50&limit=50"
```

### 2. Filtering

Combine filters to narrow results:

```bash
# Get unresponded negative complaints
curl -X GET "http://localhost:8000/complaints/?status=NÃ£o%20respondida&sentiment=Negativo"

# Get responded complaints (limit 25)
curl -X GET "http://localhost:8000/complaints/?status=Respondida&limit=25"
```

### 3. Batch Analysis

For large datasets, use batch analysis:

```bash
# Analyze all unanalyzed complaints
curl -X POST http://localhost:8000/analytics/analyze/batch
```

### 4. Error Handling

Always check response status codes and error messages:

```bash
if [ $? -ne 0 ]; then
  echo "API call failed"
  # Handle error appropriately
fi
```

### 5. Logging

Enable logging to monitor API activity:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Configuration

Key environment variables (from `.env` file):

```
DATABASE_URL=sqlite:///./venancio.db
GEMINI_API_KEY=your_api_key_here
RECLAME_AQUI_COMPANY_URL=https://www.reclameaqui.com.br/empresa/venancio/
SCRAPER_POLLING_INTERVAL_HOURS=6
SCRAPER_MAX_PAGES=10
API_PORT=8000
```

---

## Support & Troubleshooting

### Common Issues

1. **Complaints not being scraped**
   - Check scheduler is running in logs
   - Verify Reclame Aqui URL is correct
   - Check internet connection

2. **Analysis failing**
   - Verify GEMINI_API_KEY is set
   - Check API quota/usage
   - Review error logs

3. **Response generation errors**
   - Ensure complaint exists and has analyzed data
   - Check Gemini API availability
   - Review generated response in logs

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Issues

Reset database:

```bash
# Delete and recreate
rm venancio.db
# Restart API to recreate tables
```

---

## Future Enhancements

1. **Authentication & Authorization**
   - Implement JWT-based authentication
   - Role-based access control (RBAC)

2. **Rate Limiting**
   - Per-endpoint rate limits
   - API key-based quotas

3. **Advanced Analytics**
   - Time-series analysis
   - Trend detection
   - Predictive analytics

4. **Webhook Support**
   - Event notifications
   - Real-time updates

5. **Multi-language Support**
   - Sentiment analysis in multiple languages
   - Translation features

---

## API Changelog

### Version 1.0.0 (Initial Release)

- Complaint management (CRUD)
- AI-powered sentiment analysis
- Category classification
- Entity extraction
- Urgency scoring
- Response generation
- Batch analysis
- Comprehensive analytics
- Automatic scraping

---

**Last Updated:** January 2024
**Documentation Version:** 1.0
