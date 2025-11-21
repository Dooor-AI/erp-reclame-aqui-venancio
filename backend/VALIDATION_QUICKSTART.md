# 🚀 Validation Quick Start Guide - Chat B Round 2

## Prerequisites Checklist

- [x] Python 3.14+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Database created with 20 test complaints
- [ ] **Valid ANTHROPIC_API_KEY in `.env` file** ← YOU NEED THIS!

---

## Step 1: Get Your API Key (5 minutes)

1. Go to: https://console.anthropic.com/
2. Sign in (or create free account)
3. Click "API Keys" in left menu
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

---

## Step 2: Update Configuration (1 minute)

Edit `backend/.env`:

```bash
# Replace this line:
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# With your actual key:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save the file.

---

## Step 3: Run Validation (2 minutes)

### Option A: Automated Script (Recommended)

```bash
cd backend
python validate_analysis.py
```

This will:
- Analyze all 20 test complaints
- Display results in real-time
- Save detailed JSON output
- Show success rate

### Option B: Via API

```bash
# Terminal 1: Start server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Run analysis
curl -X POST "http://localhost:8000/analytics/analyze/batch?limit=20"

# View results
curl "http://localhost:8000/analytics/stats/overview"
```

---

## Step 4: Manual Validation (30-45 minutes)

For each of the 20 complaints, assess:

### Sentiment Analysis ✓
- [ ] Is sentiment label correct? (Negativo/Neutro/Positivo)
- [ ] Is score reasonable? (0=very negative, 10=very positive)
- [ ] Does reasoning make sense?

**Example:**
```
Complaint: "Produto quebrou em 3 dias. Péssimo!"
✓ CORRECT: Negativo, score: 2.0
✗ WRONG: Neutro, score: 5.0
```

### Classification ✓
- [ ] Is primary category correct?
- [ ] Are all relevant categories included?

**Categories:**
- produto: product issues
- atendimento: service/staff issues
- entrega: delivery issues
- preco: price/billing issues
- outros: other

### Entity Extraction ✓
- [ ] Are key entities identified?
  - Product names
  - Store locations
  - Employee names (if mentioned)

### Urgency Scoring ✓
- [ ] Does urgency score match complaint severity?
  - 0-3: Low (minor issues)
  - 4-6: Medium (standard complaints)
  - 7-10: High (legal threats, safety issues)

---

## Step 5: Calculate Metrics (10 minutes)

### Sentiment Accuracy
```
Accuracy = (Correct Sentiments / 20) * 100%
Target: >= 80%

Example:
- 18 correct out of 20
- Accuracy = (18/20) * 100 = 90% ✓
```

### Sentiment Score MAE
```
MAE = Average of |AI_Score - Your_Score|
Target: < 1.5

Example:
- Complaint 1: |2.5 - 3.0| = 0.5
- Complaint 2: |7.0 - 8.0| = 1.0
- Average: 0.75 ✓
```

### Category Accuracy
```
Accuracy = (Correct Primary Categories / 20) * 100%
Target: >= 75%
```

### Entity Recall
```
Recall = (Entities Found / Entities Present) * 100%
Target: >= 70%
```

---

## Step 6: Document Results (15 minutes)

Create: `coordination/answers/validation_report_B_2.md`

**Template:**
```markdown
# Validation Report - Chat B Round 2

## Test Date
2025-11-17

## Sample Size
20 complaints (diverse sentiment & categories)

## Results

### Sentiment Analysis
- Accuracy: 85%  (17/20 correct)
- Score MAE: 1.2
- Status: ✓ PASS (>= 80%)

### Classification
- Primary category accuracy: 80% (16/20)
- Status: ✓ PASS (>= 75%)

### Entity Extraction
- Key entity recall: 75% (15/20)
- Status: ✓ PASS (>= 70%)

### Urgency Scoring
- Correlation: 0.82
- Status: ✓ PASS (>= 0.7)

## Overall
- Production Ready: YES ✓
- All metrics meet targets
- No optimization needed

## Failed Cases
[List any complaints where AI was wrong]

## Recommendations
[Any suggestions for improvement]
```

---

## What to Do Based on Results

### ✅ All Metrics >= Target (Best Case)
**You're done!**

1. Create `coordination/alerts/checkpoint_B_100.md`:
```markdown
# Checkpoint: Chat B 100% Complete

Date: 2025-11-17
Status: ✅ Complete
Validation: PASSED

All AI analysis modules validated:
- Sentiment: 85% (target: 80%)
- Classification: 80% (target: 75%)
- Entity extraction: 75% (target: 70%)
- Urgency: 0.82 (target: 0.70)

Ready for Chat C (Response Generator) to start.
```

2. Proceed to next phase!

---

### ⚠️ Some Metrics Below Target (Minor Issues)

**Fix and re-test:**

See `answer_chat_B_2.md` section "Optimization Ready" for solutions:
- Low sentiment accuracy → Add few-shot examples
- Wrong categories → Enhance definitions
- Missing entities → Add extraction examples
- Urgency off → Adjust formula

After fixes, re-run validation on failed cases only.

---

### ❌ Multiple Metrics Well Below Target (Major Issues)

**Escalate:**

1. Document all failures
2. Create `coordination/questions/question_B_to_Commander_2.md`
3. Request Round 3 for comprehensive fixes

---

## Expected Performance

Based on prompt quality from Round 1:

| Metric | Expected | If This Happens | Fix |
|--------|----------|----------------|-----|
| Sentiment | 85-95% | < 80% | Add examples |
| Category | 80-90% | < 75% | Clarify definitions |
| Entities | 75-85% | < 70% | Add context |
| Urgency | 0.75-0.85 | < 0.70 | Adjust formula |

---

## Cost Tracking

As you run validation, track:

```
API Calls Made: 60 (20 complaints × 3 calls each)
Estimated Cost: $0.15 - $0.60
(depends on text length)

Monthly Projection:
- Daily volume: X complaints
- Monthly: X * 30 complaints
- Monthly cost: (X * 30) * $0.005 ≈ $XX
```

---

## Troubleshooting

### "anthropic.APIError: Invalid API key"
→ Check key format (must start with `sk-ant-`)
→ Verify on console.anthropic.com

### "Rate limit exceeded"
→ Free tier: 50 requests/min
→ Wait 1 minute, then continue
→ Or reduce batch size

### "JSON parse error"
→ Claude didn't return valid JSON
→ Check error logs
→ May need to adjust prompts

### Very slow performance
→ Normal: ~3-5 sec per complaint
→ Slow API response from Anthropic
→ Check internet connection

---

## Need Help?

**Reference Files:**
- Full answer: `coordination/answers/answer_chat_B_2.md`
- Round 1 details: `coordination/answers/answer_chat_B_1.md`
- Testing guide: `backend/TESTING_ANALYTICS.md`

**Anthropic Docs:**
- API reference: https://docs.anthropic.com/
- Rate limits: https://docs.anthropic.com/rate-limits

---

## Quick Commands Reference

```bash
# Create database + test data
cd backend
python create_test_data.py

# Run validation
python validate_analysis.py

# Check results via API
curl http://localhost:8000/analytics/stats/overview

# View single complaint analysis
curl http://localhost:8000/analytics/analyze/1

# Re-analyze failed cases
curl -X POST "http://localhost:8000/analytics/analyze/5"
```

---

**Estimated Total Time:** 1-2 hours

**Questions?** Check `answer_chat_B_2.md` for detailed guidance!

🚀 **Good luck with validation!**
