# Testing Analytics API - Quick Reference

## Prerequisites

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set API key in `.env`:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

3. **Start the server:**
```bash
uvicorn app.main:main --reload
```

4. **Access API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### 1. Analyze Single Complaint
```bash
curl -X POST "http://localhost:8000/analytics/analyze/1"
```

**Response:**
```json
{
  "complaint_id": 1,
  "sentiment": {
    "sentiment": "Negativo",
    "sentiment_score": 2.5,
    "reasoning": "..."
  },
  "classification": {
    "categories": ["produto", "atendimento"],
    "primary_category": "produto",
    "confidence": 0.85
  },
  "entities": {
    "produto": "...",
    "loja": "...",
    "funcionario": null,
    "outros": []
  },
  "urgency_score": 7.8,
  "status": "completed"
}
```

---

### 2. Batch Analysis
```bash
# Analyze all unanalyzed complaints
curl -X POST "http://localhost:8000/analytics/analyze/batch"

# Analyze up to 10 complaints
curl -X POST "http://localhost:8000/analytics/analyze/batch?limit=10"
```

**Response:**
```json
{
  "total_processed": 10,
  "successful": 9,
  "failed": 1,
  "success_rate": 0.9,
  "results": [...],
  "errors": [...]
}
```

---

### 3. Sentiment Statistics
```bash
curl "http://localhost:8000/analytics/stats/sentiment"
```

**Response:**
```json
{
  "total_analyzed": 100,
  "by_sentiment": [
    {
      "sentiment": "Negativo",
      "count": 75,
      "percentage": 75.0,
      "avg_score": 2.3,
      "min_score": 0.5,
      "max_score": 4.8
    },
    ...
  ]
}
```

---

### 4. Category Statistics
```bash
curl "http://localhost:8000/analytics/stats/categories"
```

**Response:**
```json
{
  "total_classified": 100,
  "categories": [
    {
      "category": "produto",
      "count": 45,
      "percentage": 45.0
    },
    ...
  ],
  "top_5": [...]
}
```

---

### 5. Urgency Statistics
```bash
# Default: urgency >= 7.0, limit 10
curl "http://localhost:8000/analytics/stats/urgency"

# Custom threshold and limit
curl "http://localhost:8000/analytics/stats/urgency?min_score=8.0&limit=5"
```

**Response:**
```json
{
  "avg_urgency_score": 5.2,
  "total_urgent": 15,
  "total_analyzed": 100,
  "urgent_percentage": 15.0,
  "urgent_complaints": [
    {
      "id": 42,
      "title": "...",
      "urgency_score": 9.5,
      "sentiment": "Negativo",
      "sentiment_score": 1.2,
      "categories": ["produto", "atendimento"],
      "complaint_date": "2025-11-17T10:30:00"
    },
    ...
  ]
}
```

---

### 6. Overview Dashboard
```bash
curl "http://localhost:8000/analytics/stats/overview"
```

**Response:**
```json
{
  "totals": {
    "total_complaints": 150,
    "analyzed": 100,
    "not_analyzed": 50,
    "analysis_rate": 66.67
  },
  "averages": {
    "sentiment_score": 3.2,
    "urgency_score": 5.4
  },
  "sentiment_distribution": {
    "Negativo": 75,
    "Neutro": 20,
    "Positivo": 5
  }
}
```

---

## Python Testing Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Analyze a complaint
response = requests.post(f"{BASE_URL}/analytics/analyze/1")
print(response.json())

# 2. Get overview
response = requests.get(f"{BASE_URL}/analytics/stats/overview")
stats = response.json()
print(f"Analyzed: {stats['totals']['analyzed']}/{stats['totals']['total_complaints']}")

# 3. Get urgent complaints
response = requests.get(f"{BASE_URL}/analytics/stats/urgency?min_score=7.0")
urgent = response.json()
print(f"Urgent complaints: {urgent['total_urgent']}")
for complaint in urgent['urgent_complaints'][:5]:
    print(f"  - ID {complaint['id']}: {complaint['title']} (score: {complaint['urgency_score']})")
```

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
- Check `.env` file exists in `backend/` directory
- Verify `ANTHROPIC_API_KEY=sk-ant-...` is set
- Restart the server

### Error: "Complaint not found"
- Make sure complaints exist in database
- Run scraper first: `POST /scrape/run`
- Check database: `sqlite3 venancio.db "SELECT count(*) FROM complaints;"`

### Error: "API rate limit exceeded"
- Reduce batch size: `?limit=5`
- Wait and retry
- Check Anthropic console for quota

### JSON parsing errors
- Check logs for API responses
- Prompts might need adjustment
- Falls back to safe defaults

---

## Performance Notes

- **Single analysis:** ~2-3 seconds (3 API calls)
- **Batch 10:** ~20-30 seconds (sequential)
- **Batch 100:** ~3-5 minutes (sequential)

**Cost estimate:** $0.003-0.01 per complaint (depends on text length)

---

## Next Steps

1. Wait for Chat A to scrape complaints
2. Run batch analysis
3. Validate accuracy (target: 80%+)
4. Tune prompts if needed
5. Monitor API costs
