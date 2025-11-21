# Venâncio RPA - End-User Manual

A comprehensive guide for using the Venâncio RPA Dashboard to manage, analyze, and respond to customer complaints from Reclame Aqui.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Accessing the Dashboard](#accessing-the-dashboard)
3. [Dashboard Overview](#dashboard-overview)
4. [Understanding KPIs](#understanding-kpis)
5. [Reading Charts](#reading-charts)
6. [Viewing Complaints](#viewing-complaints)
7. [Generating AI Responses](#generating-ai-responses)
8. [Using Filters](#using-filters)
9. [Common Tasks](#common-tasks)
10. [FAQ](#faq)

---

## Getting Started

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Screen resolution: 1024x768 or higher

### First Login

1. Navigate to your dashboard URL (provided by administrator)
2. The dashboard loads automatically if properly configured
3. You should see the main dashboard with KPI cards and charts

### Initial Data Loading

- First load may take a few seconds
- Real-time data updates every 60 seconds
- Historical data persists in the database

---

## Accessing the Dashboard

### Web Browser Access

**Local Development:**
```
http://localhost:3000
```

**Production:**
```
https://yourdomain.com
```

### Dashboard URL Structure

- **Home/Dashboard:** `/` or `/dashboard`
- **Complaints List:** `/reclamacoes`
- **Analytics:** Built into dashboard

### Browser Compatibility

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 90+ | Full |
| Firefox | 88+ | Full |
| Safari | 14+ | Full |
| Edge | 90+ | Full |

---

## Dashboard Overview

### Main Dashboard Page (/)

The home page displays key performance indicators and analytics at a glance.

```
┌────────────────────────────────────────────────────────────────┐
│                    VENÂNCIO RPA DASHBOARD                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Total de         │  │ Reclamações      │  │ Urgência     │ │
│  │ Reclamações      │  │ Negativas        │  │ Média        │ │
│  │      245         │  │      89          │  │    7.2       │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│  ┌──────────────────┐                                          │
│  │ Reclamações      │                                          │
│  │ Pendentes        │                                          │
│  │      34          │                                          │
│  └──────────────────┘                                          │
│                                                                │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │ SENTIMENTO DAS            │  │ CATEGORIAS DE            │    │
│  │ RECLAMAÇÕES (PIE)         │  │ RECLAMAÇÕES (BAR)       │    │
│  │                           │  │                        │    │
│  │  Positivo  10%            │  │ Produto      45        │    │
│  │  Neutro    30%            │  │ Serviço      87        │    │
│  │  Negativo  60%            │  │ Atendimento  52        │    │
│  │                           │  │ Entrega      61        │    │
│  └──────────────────────────┘  └──────────────────────────┘    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Navigation Menu

Located at the top of the page:

- **Dashboard** - Main KPI view
- **Reclamações** - Full list of complaints with filters
- **Docs** - Links to documentation

---

## Understanding KPIs

KPIs (Key Performance Indicators) are the four main cards on the dashboard showing high-level metrics.

### 1. Total de Reclamações (Total Complaints)

**What it shows:** Total number of complaints scraped from Reclame Aqui

**Interpretation:**
- High number = increased customer dissatisfaction
- Trending up = deteriorating customer experience
- Use as baseline metric

**Example:**
```
245 Total Complaints
↑ Up 12% from last week
```

### 2. Reclamações Negativas (Negative Complaints)

**What it shows:** Complaints classified as negative sentiment by AI analysis

**Interpretation:**
- Represents percentage of unhappy customers
- Priority for response generation
- Indicates areas needing improvement

**Example:**
```
89 Negative Complaints
36% of total complaints
```

**Action:** Generate responses for these complaints first

### 3. Urgência Média (Average Urgency)

**What it shows:** Average urgency score across all complaints (0-10 scale)

**Interpretation:**
- 0-3: Low urgency, routine issues
- 4-6: Medium urgency, needs attention
- 7-10: High urgency, requires immediate action

**Example:**
```
Average Urgency: 7.2 / 10
High priority action needed
```

**Action:** Focus on complaints with urgency > 7

### 4. Reclamações Pendentes (Pending Responses)

**What it shows:** Complaints without an AI-generated response

**Interpretation:**
- Indicates backlog of unanswered complaints
- Directly impacts customer satisfaction
- Target should be close to zero

**Example:**
```
34 Pending Responses
14% of total complaints
```

**Action:** Generate responses to reduce this number

---

## Reading Charts

### Sentiment Chart (Pie Chart)

**Location:** Bottom left of dashboard

**Shows:** Distribution of complaint sentiments

**Segments:**
- **Negativo (Red):** Unhappy customers
- **Neutro (Yellow):** Neutral/Mixed feelings
- **Positivo (Green):** Happy customers

**How to Read:**

```
Pie Chart Example:
┌─────────────────┐
│     Positivo    │  Label: Positivo (Green)
│      10%        │  Percentage shown inside
├─────────────────┤
│     Neutro      │  Label: Neutro (Yellow)
│      30%        │  Percentage shown inside
├─────────────────┤
│    Negativo     │  Label: Negativo (Red)
│      60%        │  Percentage shown inside
└─────────────────┘
```

**Interpretation:**

- **High Negativo %:** Many dissatisfied customers, need priority response
- **High Positivo %:** Good customer satisfaction, maintain approach
- **High Neutro %:** Need better communication or clearer expectations

**Example Analysis:**
```
Current: Negativo 60%, Neutro 30%, Positivo 10%

This indicates:
- 6 out of 10 customers are unhappy
- 3 out of 10 have neutral feelings
- 1 out of 10 are satisfied

Recommendation: Focus on negative sentiment complaints
```

### Category Chart (Bar Chart)

**Location:** Bottom right of dashboard

**Shows:** Complaints grouped by category with counts

**Bar Segments:**
- **Produto:** Product-related issues
- **Serviço:** Service-related issues
- **Atendimento:** Customer service complaints
- **Entrega:** Delivery/Logistics issues
- *Other custom categories*

**How to Read:**

```
Bar Chart Example:
Complaints by Category

Entrega      ████████████████ 61
Serviço      ███████████████████████ 87
Atendimento  ██████████████ 52
Produto      ████████████████ 45
             0   20   40   60   80  100
```

**Interpretation:**

- **Tallest bar:** Most common complaint type
- **Shortest bar:** Least common complaint type
- **Height comparison:** Relative problem severity

**Example Analysis:**
```
Current data:
- Service (87): Highest complaints - needs training/process review
- Delivery (61): Second highest - logistics issues
- Customer Service (52): Third - staff training needed
- Product (45): Lowest - product quality acceptable

Action Plan:
1. Priority: Service issues (87) - implement service training
2. Secondary: Delivery (61) - review logistics partners
3. Tertiary: Customer Service (52) - improve response times
```

---

## Viewing Complaints

### Accessing Complaints List

1. Click **"Reclamações"** in the navigation menu
2. Page loads showing all complaints
3. Each complaint appears as a card

### Complaint Card Layout

```
┌────────────────────────────────────────────────────────┐
│ Título da Reclamação                                   │
│ Lorem ipsum dolor sit amet, consectetur adipiscing...  │
│                                                         │
│ Sentimento Badge: [Negativo]  Urgência: [8/10]        │
│ Usuário: João Silva | 2 dias atrás                    │
│                                                         │
│                    [Gerar Resposta]                    │
└────────────────────────────────────────────────────────┘
```

### Complaint Card Information

| Field | Meaning |
|-------|---------|
| **Título** | Main complaint subject |
| **Text** | Full complaint description |
| **Sentimento** | Sentiment badge (Negativo/Neutro/Positivo) |
| **Urgência** | Score 0-10, higher = more urgent |
| **Usuário** | Name of complaining customer |
| **Time** | How long ago complaint was posted |

### Understanding Sentiment Badges

- **Negativo (Red):** Unhappy customer, high priority
- **Neutro (Yellow):** Mixed or unclear sentiment
- **Positivo (Green):** Satisfied customer, low priority

### Understanding Urgency Scores

| Score | Level | Action Required |
|-------|-------|-----------------|
| 7-10 | High | Immediate response (today) |
| 4-6 | Medium | Response within 24-48 hours |
| 0-3 | Low | Response within a week |

---

## Generating AI Responses

### Starting Response Generation

1. Find the complaint in the Reclamações list
2. Click **"Gerar Resposta"** (Generate Response) button on the card
3. Response Generator dialog opens

### Response Generator Dialog

```
┌────────────────────────────────────────────────┐
│  GERADOR DE RESPOSTA                      [×]  │
├────────────────────────────────────────────────┤
│                                                │
│  Reclamação Original:                         │
│  ┌──────────────────────────────────────────┐ │
│  │ Título: Produto chegou com defeito       │ │
│  │ Texto: O produto não funciona e...       │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  Resposta Gerada:                             │
│  ┌──────────────────────────────────────────┐ │
│  │ Agradecemos pelo contato...              │ │
│  │ Lamentamos pelo inconveniente...          │ │
│  │ Oferecemos cupom de desconto...           │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  Cupom: DESCONTO20  |  Desconto: 20%          │
│                                                │
│  [Editar]  [Enviar]  [Cancelar]              │
└────────────────────────────────────────────────┘
```

### Response Generation Steps

#### Step 1: AI Generates Response

- Click "Gerar Resposta"
- AI analyzes complaint sentiment and category
- Generates appropriate response automatically
- Shows generated response in the dialog

#### Step 2: Review Generated Response

Read the generated response:
- Ensure it addresses the customer's concern
- Verify tone is appropriate (empathetic, professional)
- Check if discount/coupon is relevant

#### Step 3: (Optional) Edit Response

1. Click **"Editar"** button
2. Response text becomes editable
3. Modify text as needed
4. Click Save to confirm edits

#### Step 4: View Coupon Details

- **Coupon Code:** Discount code offered
- **Discount %:** Percentage off
- **Expiration:** When coupon expires

#### Step 5: Send Response

1. Review final response once more
2. Click **"Enviar"** (Send) button
3. Response sent to customer
4. Success notification appears

### Example Response Generation

**Original Complaint:**
```
Título: Produto deficiente
Texto: Comprei um fone de ouvido ontem e não funciona.
Está na caixa, unopened, and defective.
Quero um reembolso ou troca urgentemente!
```

**AI Generated Response:**
```
Olá [Customer Name],

Agradecemos sinceramente por nos informar sobre o problema
com seu fone de ouvido. Entendemos sua frustração com um
produto defeituoso.

Como solução, oferecemos:
1. Troca imediata do produto (sem custos)
2. Cupom de desconto 20% para sua próxima compra
3. Atendimento prioritário para agilizar o processo

Use o cupom DESCONTO20 em sua próxima compra.

Sentimentos atenciosos,
Equipe Venâncio
```

---

## Using Filters

### Filter Location

Located at the top of the Reclamações page

### Available Filters

#### 1. Filter by Sentiment

**Options:**
- All (default, shows all complaints)
- Negativo (negative only)
- Neutro (neutral only)
- Positivo (positive only)

**How to use:**
1. Click sentiment filter dropdown
2. Select desired sentiment
3. List automatically updates

**Example Use Cases:**
- Filter "Negativo" to focus on unhappy customers
- Filter "Positivo" to identify satisfied customers
- Filter "Neutro" to clarify ambiguous complaints

#### 2. Filter by Urgency (Future Feature)

When implemented, will allow filtering by urgency score ranges:
- High (7-10)
- Medium (4-6)
- Low (0-3)

#### 3. Filter by Category (Future Feature)

When implemented, will allow filtering by complaint category:
- Produto
- Serviço
- Atendimento
- Entrega

### Combining Filters

Filters work together:

```
Example: Show me negative complaints about Delivery
1. Sentiment Filter: Select "Negativo"
2. Category Filter: Select "Entrega"
3. Result: Only negative delivery complaints display
```

### Clearing Filters

- Click "Reset" or "Clear" button to show all complaints
- All filters return to default state

### Search Functionality

Search by complaint text (if implemented):
1. Enter search term in search box
2. Results update in real-time
3. Searches titles and descriptions

---

## Common Tasks

### Task 1: Check Daily Status

**Time:** 5 minutes | **Frequency:** Daily (morning)

1. Navigate to Dashboard
2. Review KPI cards:
   - Total Complaints (any new?)
   - Negative Complaints (urgent issues?)
   - Average Urgency (overall trend?)
   - Pending Responses (backlog?)
3. Review Sentiment pie chart (satisfaction trend?)
4. Review Category bar chart (problem areas?)

**Decision Points:**
- If negative complaints > 20%: Plan urgent responses
- If pending responses > 10%: Allocate more resources
- If average urgency > 7: Schedule emergency meeting

### Task 2: Respond to High-Urgency Complaints

**Time:** 2-3 minutes per complaint | **Frequency:** As needed

1. Navigate to Reclamações
2. Filter by Sentiment: "Negativo"
3. Look for complaints with Urgência 7+
4. Click "Gerar Resposta" on each
5. Review and send generated response
6. Verify response sent (success notification)

**Goal:** Respond to all urgent negative complaints within 2 hours

### Task 3: Monitor Customer Satisfaction

**Time:** 10 minutes | **Frequency:** Weekly

1. Go to Dashboard
2. Track Sentiment pie chart over time
3. Note percentage of Negativo and Positivo
4. Compare to previous week
5. Document trends in log

**Targets:**
- Negativo < 50%
- Positivo > 20%

### Task 4: Identify Problem Categories

**Time:** 5 minutes | **Frequency:** Weekly

1. View Dashboard Category chart
2. Identify tallest bar (most complaints)
3. Navigate to Reclamações
4. Filter by that category (when available)
5. Review complaints in detail
6. Report findings to relevant department

### Task 5: Generate Batch Responses

**Time:** 15-30 minutes | **Frequency:** Daily

1. Navigate to Reclamações
2. Filter by "Pendentes" (pending responses)
3. For each complaint:
   - Click "Gerar Resposta"
   - Review generated response (15 seconds)
   - Edit if needed (optional)
   - Click "Enviar"
4. Repeat until all pending are addressed

**Target:** Zero pending complaints by end of day

---

## FAQ

### General Questions

**Q: How often is the data updated?**
A: The dashboard updates every 60 seconds with new data. The backend scraper runs every hour to fetch new complaints from Reclame Aqui.

**Q: What is Reclame Aqui?**
A: Reclame Aqui is the largest Brazilian website for customer complaints and reviews. The system automatically monitors your company's complaints there.

**Q: Can I edit a complaint's sentiment?**
A: Not directly. The sentiment is calculated by AI analysis. If you believe it's incorrect, contact your administrator.

### KPI Questions

**Q: What's the difference between "Urgência Média" and the individual complaint urgency?**
A: "Urgência Média" on the dashboard is the average urgency across all complaints. Individual complaints have their own urgency score (0-10).

**Q: Why did my negative complaint count suddenly increase?**
A: Either the scraper found new complaints, or existing complaints were re-analyzed and reclassified as negative.

### Response Questions

**Q: Can I use the same response for multiple complaints?**
A: Currently, each complaint requires its own response generation. You can edit generated responses to reuse text.

**Q: What if I make a mistake in the response?**
A: Currently, responses cannot be recalled once sent. Be careful with the review step.

**Q: How is the coupon discount determined?**
A: The backend AI calculates appropriate discount based on:
- Complaint severity
- Urgency level
- Type of issue (defective product gets higher discount)

### Technical Questions

**Q: What browser should I use?**
A: Any modern browser works. Chrome, Firefox, Safari, and Edge all supported.

**Q: What if I get a connection error?**
A: Check your internet connection. If the backend is down, contact your IT administrator.

**Q: Can I access the dashboard on my phone?**
A: Yes, the dashboard is responsive and works on mobile devices. However, generating responses is easier on desktop.

### Data Questions

**Q: How long is complaint data stored?**
A: Data is stored indefinitely in the database unless manually deleted.

**Q: Can I export complaint data?**
A: Currently, there's no direct export feature. Contact your administrator for data exports.

**Q: How is sentiment analysis performed?**
A: The system uses Google Gemini AI to analyze complaint text and classify as Negativo (negative), Neutro (neutral), or Positivo (positive).

### Troubleshooting

**Q: The dashboard is blank or shows no data**

A:
1. Check your internet connection
2. Try refreshing the page (Ctrl+R or Cmd+R)
3. Check if the backend API is running
4. Wait 5 minutes - first scrape may take time

**Q: Charts look weird or incomplete**

A:
1. Try zooming out (Ctrl+Minus)
2. Refresh the page
3. Try a different browser

**Q: "Gerar Resposta" button doesn't work**

A:
1. Check your internet connection
2. Try again in a few seconds
3. Check browser console for errors (F12)
4. Refresh page and try again

**Q: Response says "Envio Falhou" (Send Failed)**

A:
1. Check internet connection
2. Try sending again
3. Check if backend is running
4. Contact administrator if problem persists

---

## Best Practices

### For Daily Operations

1. **Check dashboard first thing each morning**
   - Sets tone for the day
   - Identifies urgent issues

2. **Respond to negative complaints same day**
   - Improves customer satisfaction
   - Prevents escalation

3. **Monitor urgency scores**
   - High (7-10) = respond within 2 hours
   - Medium (4-6) = respond within 24 hours
   - Low (0-3) = respond within 48 hours

4. **Review generated responses carefully**
   - Ensure appropriate tone
   - Verify information accuracy
   - Don't send without review

5. **Document issues**
   - Note recurring problems
   - Share with product/service teams
   - Use for continuous improvement

### For Performance Optimization

1. **Focus on high-impact areas**
   - Target high-urgency complaints first
   - Address top complaint categories
   - Focus on negative sentiment complaints

2. **Track your metrics**
   - Note pending complaint reduction rate
   - Track sentiment trend
   - Measure response time improvement

3. **Collaborate with teams**
   - Share Category chart with relevant departments
   - Use insights for training
   - Implement root cause fixes

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-17
**For Support:** Contact your system administrator

---

*Venâncio RPA - Intelligent Complaint Management System*
