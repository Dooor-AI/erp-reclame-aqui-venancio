# 📋 Order for Chat B - Round 3 (Refactor to Google Gemini)

**From:** Commander
**To:** Chat B (Backend Intelligence - AI Analysis)
**Priority:** 🔴 Critical
**Estimated Time:** 1-2h
**Dependencies:** Round 1 complete ✅
**Date:** 2025-11-17

---

## 📊 Context

**Decision:** Switch from Anthropic Claude to **Google Gemini** for AI analysis.

**Reasons:**
- ✅ **FREE tier:** 15 requests/minute (generous for testing + early production)
- ✅ **Very low cost:** ~10-20x cheaper than Claude after free tier
- ✅ **Same quality:** 85-95% accuracy (comparable to Claude)
- ✅ **Great Portuguese support:** Excellent for Brazilian Portuguese
- ✅ **Fast refactor:** Only 1-2h work (similar API structure)

**Cost Analysis:**
- Testing (20 complaints): **$0** (free tier)
- Production (100 complaints/day): **$0-2/month**
- vs Claude: **$9-30/month**

---

## 🎯 Mission

Refactor all AI modules to use **Google Gemini 1.5 Flash** instead of Anthropic Claude, maintaining the same functionality and prompt quality from Round 1.

---

## 📋 Tasks

### Task 1: Setup Google Gemini (15 min)

**Step 1: Get API Key (5 min)**

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (format: `AIza...`)

**Step 2: Install SDK (5 min)**

```bash
cd backend

# Add to requirements.txt
echo "google-generativeai==0.3.2" >> requirements.txt

# Install
pip install google-generativeai==0.3.2
```

**Step 3: Update Configuration (5 min)**

Edit [backend/app/core/config.py](../../backend/app/core/config.py):

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # OLD: ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    # NEW:
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
```

Edit [backend/.env](../../backend/.env):

```bash
# OLD: ANTHROPIC_API_KEY=sk-ant-your-api-key-here
# NEW:
GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_KEY_HERE
```

Update [backend/.env.example](../../backend/.env.example):

```bash
# AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
```

**Deliverables:**
- ✅ Gemini SDK installed
- ✅ Configuration updated
- ✅ API key configured

---

### Task 2: Refactor Claude Client → Gemini Client (15 min)

**File:** [backend/app/ai/claude_client.py](../../backend/app/ai/claude_client.py) → Rename to `gemini_client.py`

**Current Code (Claude):**
```python
from anthropic import Anthropic
from app.core.config import settings

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def analyze_text(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

**New Code (Gemini):**
```python
import google.generativeai as genai
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_text(self, prompt: str) -> str:
        """
        Analyze text using Google Gemini.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            The response text from Gemini
        """
        response = self.model.generate_content(prompt)
        return response.text
```

**Steps:**
1. Rename file: `claude_client.py` → `gemini_client.py`
2. Replace class name: `ClaudeClient` → `GeminiClient`
3. Replace Anthropic imports with Gemini imports
4. Update `analyze_text` method
5. Keep the same interface (input/output unchanged)

**Deliverables:**
- ✅ [backend/app/ai/gemini_client.py](../../backend/app/ai/gemini_client.py) created
- ✅ Same interface as Claude client
- ✅ Works with existing code

---

### Task 3: Update Sentiment Analyzer (10 min)

**File:** [backend/app/ai/sentiment_analyzer.py](../../backend/app/ai/sentiment_analyzer.py)

**Change 1: Import**
```python
# OLD:
from app.ai.claude_client import ClaudeClient

# NEW:
from app.ai.gemini_client import GeminiClient
```

**Change 2: Client Initialization**
```python
# OLD:
self.client = ClaudeClient()

# NEW:
self.client = GeminiClient()
```

**Keep the same:**
- ✅ SENTIMENT_PROMPT (already well-designed)
- ✅ analyze() method logic
- ✅ JSON parsing
- ✅ Error handling

**Deliverables:**
- ✅ sentiment_analyzer.py updated
- ✅ Uses GeminiClient
- ✅ Prompts unchanged (already good)

---

### Task 4: Update Classifier (10 min)

**File:** [backend/app/ai/classifier.py](../../backend/app/ai/classifier.py)

**Same changes as Task 3:**

```python
# OLD:
from app.ai.claude_client import ClaudeClient
self.client = ClaudeClient()

# NEW:
from app.ai.gemini_client import GeminiClient
self.client = GeminiClient()
```

**Keep the same:**
- ✅ CLASSIFICATION_PROMPT
- ✅ classify() method
- ✅ JSON parsing

**Deliverables:**
- ✅ classifier.py updated

---

### Task 5: Update Entity Extractor (10 min)

**File:** [backend/app/ai/entity_extractor.py](../../backend/app/ai/entity_extractor.py)

**Same changes:**

```python
# OLD:
from app.ai.claude_client import ClaudeClient
self.client = ClaudeClient()

# NEW:
from app.ai.gemini_client import GeminiClient
self.client = GeminiClient()
```

**Deliverables:**
- ✅ entity_extractor.py updated

---

### Task 6: Update Response Personalizer (10 min)

**File:** [backend/app/ai/response_personalizer.py](../../backend/app/ai/response_personalizer.py)

**Same changes:**

```python
# OLD:
from app.ai.claude_client import ClaudeClient
self.client = ClaudeClient()

# NEW:
from app.ai.gemini_client import GeminiClient
self.client = GeminiClient()
```

**Deliverables:**
- ✅ response_personalizer.py updated

---

### Task 7: Update Analysis Service (5 min)

**File:** [backend/app/services/analysis_service.py](../../backend/app/services/analysis_service.py)

**Check imports:**
- Should already work (imports the analyzer/classifier classes, not the client directly)
- No changes needed if properly abstracted

**Verify:**
```python
from app.ai.sentiment_analyzer import SentimentAnalyzer
from app.ai.classifier import Classifier
from app.ai.entity_extractor import EntityExtractor
```

These classes now use GeminiClient internally - no changes needed here!

**Deliverables:**
- ✅ Verified analysis_service.py works with refactored modules

---

### Task 8: Clean Up Old Files (5 min)

```bash
# Delete old Claude client
rm backend/app/ai/claude_client.py

# Remove from requirements.txt
# Delete line: anthropic==0.8.1
```

Update [backend/requirements.txt](../../backend/requirements.txt):
```diff
- anthropic==0.8.1
+ google-generativeai==0.3.2
```

**Deliverables:**
- ✅ Old files removed
- ✅ Requirements updated

---

### Task 9: Testing (15 min)

**Test 1: Gemini Client Standalone**

Create test script: `backend/test_gemini.py`

```python
import asyncio
from app.ai.gemini_client import GeminiClient

async def test_gemini():
    client = GeminiClient()

    prompt = "Analise o sentimento desta frase: 'Produto péssimo, quebrou em 2 dias!'"

    response = await client.analyze_text(prompt)
    print("Gemini Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(test_gemini())
```

Run:
```bash
cd backend
python test_gemini.py
```

**Expected:** Gemini returns sentiment analysis in Portuguese

---

**Test 2: Full Pipeline**

Use existing validation script from Round 2:

```bash
cd backend
python validate_analysis.py
```

**Expected:**
- ✅ Analyzes 20 complaints
- ✅ Returns sentiment, classification, entities
- ✅ No errors
- ✅ Results look reasonable

---

**Test 3: API Endpoints**

```bash
# Start server
uvicorn app.main:app --reload

# In another terminal:
# Test sentiment analysis
curl -X POST "http://localhost:8000/analytics/analyze/1"

# Test batch
curl -X POST "http://localhost:8000/analytics/analyze/batch?limit=5"
```

**Expected:**
- ✅ API works
- ✅ Gemini processes requests
- ✅ Results returned correctly

**Deliverables:**
- ✅ Standalone test passes
- ✅ Validation script works
- ✅ API endpoints functional

---

### Task 10: Documentation (10 min)

**Update [backend/README.md](../../backend/README.md):**

```markdown
## AI Configuration

This system uses **Google Gemini 1.5 Flash** for AI-powered analysis.

### Setup

1. Get free API key: https://makersuite.google.com/app/apikey
2. Add to `.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```

### Cost

- **Free tier:** 15 requests/minute (900/hour)
- **After free tier:** ~$0.000075 per 1K characters
- **Estimated cost:** $0-2/month for typical usage

### API Limits

- Free tier: 15 requests/minute
- 1,500 requests/day
- 1.5M tokens/minute

For higher limits, see: https://ai.google.dev/pricing
```

**Update answer file:**

Create [coordination/answers/answer_chat_B_3.md](../../coordination/answers/answer_chat_B_3.md):

```markdown
# 📋 Answer for Chat B - Round 3 (Gemini Refactor)

**Status:** ✅ Complete
**Duration:** ~Xh
**Date:** 2025-11-17

## Summary

Successfully refactored all AI modules from Anthropic Claude to Google Gemini 1.5 Flash.

## Changes Made

### Files Modified (6):
1. `backend/app/core/config.py` - Updated API key config
2. `backend/app/ai/gemini_client.py` - Created (replaced claude_client.py)
3. `backend/app/ai/sentiment_analyzer.py` - Updated to use GeminiClient
4. `backend/app/ai/classifier.py` - Updated to use GeminiClient
5. `backend/app/ai/entity_extractor.py` - Updated to use GeminiClient
6. `backend/app/ai/response_personalizer.py` - Updated to use GeminiClient

### Files Deleted (1):
- `backend/app/ai/claude_client.py`

### Dependencies Updated:
- Removed: `anthropic==0.8.1`
- Added: `google-generativeai==0.3.2`

## Testing Results

- ✅ Gemini client works
- ✅ All 4 AI modules functional
- ✅ Validation script passes
- ✅ API endpoints working
- ✅ No errors in testing

## Cost Savings

| Metric | Claude | Gemini | Savings |
|--------|--------|--------|---------|
| Testing (20 complaints) | $0.20 | **$0 (free)** | 100% |
| Monthly (100/day) | $9-30 | **$0-2** | 85-95% |

## Next Steps

Now ready for Chat B Round 2 validation:
- Run `python validate_analysis.py`
- Complete accuracy testing
- Create validation report
```

**Deliverables:**
- ✅ README updated
- ✅ answer_chat_B_3.md created

---

## 📊 Success Criteria

- ✅ Gemini SDK installed and configured
- ✅ All 4 AI modules refactored (sentiment, classifier, entity, response)
- ✅ Old Claude code removed
- ✅ Testing passes (standalone + validation + API)
- ✅ Documentation updated
- ✅ Same functionality as Claude version
- ✅ Ready for validation testing

---

## ⏱️ Time Breakdown

| Task | Estimated | Description |
|------|-----------|-------------|
| Task 1: Setup | 15 min | API key, SDK install, config |
| Task 2: Gemini Client | 15 min | Create new client class |
| Task 3: Sentiment | 10 min | Update analyzer |
| Task 4: Classifier | 10 min | Update classifier |
| Task 5: Entity Extractor | 10 min | Update extractor |
| Task 6: Response Gen | 10 min | Update personalizer |
| Task 7: Service Check | 5 min | Verify service layer |
| Task 8: Cleanup | 5 min | Remove old files |
| Task 9: Testing | 15 min | Full testing |
| Task 10: Docs | 10 min | Update documentation |
| **TOTAL** | **~1.5h** | |

---

## 🎯 What Doesn't Change

**Keep exactly the same:**
- ✅ All prompts (already well-designed for Portuguese)
- ✅ JSON parsing logic
- ✅ Error handling
- ✅ API endpoints
- ✅ Database operations
- ✅ Frontend integration
- ✅ Response templates

**Only changing:**
- ❌ AI provider (Claude → Gemini)
- ❌ API client class
- ❌ Import statements

---

## 💡 Gemini-Specific Tips

### Rate Limits (Free Tier)
- 15 requests/minute = 900/hour
- For validation (20 complaints): Takes ~2 minutes at max speed
- No issues for testing or early production

### If You Hit Rate Limit:
```python
import time

# Add small delay between requests
for complaint in complaints:
    result = await analyze(complaint)
    time.sleep(0.1)  # 100ms delay = safe margin
```

### Quality Tips:
- Gemini responds well to clear, structured prompts (✅ already have this)
- Request JSON-only output (✅ already doing this)
- Portuguese works excellently (✅ all prompts in PT-BR)

---

## 🚀 How to Execute

```bash
# 1. Get Gemini API key (5 min)
# Go to: https://makersuite.google.com/app/apikey

# 2. Start refactoring (1-2h)
cd backend

# Install Gemini SDK
pip install google-generativeai==0.3.2

# Update .env
echo "GEMINI_API_KEY=your-key" >> .env

# Refactor files (follow tasks 2-8)

# 3. Test everything
python test_gemini.py
python validate_analysis.py
uvicorn app.main:app --reload

# 4. Verify API works
curl -X POST "http://localhost:8000/analytics/analyze/batch?limit=5"

# 5. Create answer file
# coordination/answers/answer_chat_B_3.md
```

---

## 📞 Support

### Gemini Documentation:
- API Reference: https://ai.google.dev/api/python
- Quickstart: https://ai.google.dev/tutorials/python_quickstart
- Pricing: https://ai.google.dev/pricing

### Troubleshooting:

**Issue: "API key invalid"**
```bash
# Verify key format
# Should start with: AIza...
# Check: https://makersuite.google.com/app/apikey
```

**Issue: "Rate limit exceeded"**
```python
# Add delay between requests
import time
time.sleep(0.1)  # 100ms between calls
```

**Issue: "Response not JSON"**
```python
# Gemini might add markdown formatting
# Clean response:
text = response.text.strip()
if text.startswith("```json"):
    text = text.replace("```json", "").replace("```", "").strip()
```

---

**Prepared by:** Commander
**Date:** 2025-11-17
**Priority:** 🔴 Critical
**Estimated:** 1-2h

✅ **This is a straightforward refactor - same functionality, better cost!**
