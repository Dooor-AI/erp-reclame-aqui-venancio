# Venâncio RPA - Frontend

Modern Next.js 15 dashboard for the Venâncio RPA complaint management system.

## 🚀 Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **UI Components:** Shadcn/ui
- **State Management:** React Query (TanStack Query)
- **Charts:** Recharts
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Date Formatting:** date-fns
- **Notifications:** Sonner

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Dashboard page
│   ├── reclamacoes/
│   │   └── page.tsx         # Complaints listing page
│   └── globals.css          # Global styles
├── components/
│   ├── ui/                  # Shadcn/ui components
│   ├── layout/
│   │   └── header.tsx       # Header component
│   ├── dashboard/
│   │   ├── stats-card.tsx
│   │   ├── sentiment-chart.tsx
│   │   └── category-chart.tsx
│   ├── reclamacoes/
│   │   └── reclamacao-card.tsx
│   └── respostas/
│       └── response-generator-dialog.tsx
├── lib/
│   ├── api.ts               # API client
│   ├── utils.ts             # Utility functions
│   └── types.ts             # TypeScript types
├── hooks/
│   ├── use-complaints.ts    # Complaints hooks
│   └── use-analytics.ts     # Analytics hooks
└── package.json
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## 📦 Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## 🎨 Features

### Dashboard (/)
- **KPI Cards:**
  - Total de Reclamações
  - Reclamações Negativas
  - Urgência Média
  - Reclamações Pendentes

- **Charts:**
  - Pie chart: Sentimento das Reclamações
  - Bar chart: Categorias de Reclamações

### Reclamações (/reclamacoes)
- List all complaints with:
  - Sentiment badges (Negativo, Neutro, Positivo)
  - Urgency score badges
  - User information
  - Time since complaint

- **Filters:**
  - Filter by sentiment

- **Actions:**
  - Generate AI response for each complaint

### Response Generator
- Dialog-based UI for generating responses
- View original complaint
- Generate response using AI
- Edit generated response
- View coupon code (discount details)
- Mock send functionality

## 🔌 API Integration

The frontend connects to the backend API using the following endpoints:

### Complaints
- `GET /complaints` - List complaints (with optional filters)
- `GET /complaints/{id}` - Get single complaint
- `GET /complaints/stats` - Get complaint statistics

### Analytics
- `POST /analytics/analyze/{id}` - Analyze complaint sentiment
- `GET /analytics/stats/sentiment` - Get sentiment statistics
- `GET /analytics/stats/categories` - Get category statistics
- `GET /analytics/stats/urgency` - Get urgency statistics

### Responses
- `POST /responses/generate/{id}` - Generate AI response
- `GET /responses/{id}` - Get response details
- `PUT /responses/{id}` - Edit response
- `POST /responses/{id}/send` - Mark response as sent

## 🎯 Component Details

### StatsCard
Displays a single KPI metric with title, value, and optional description.

### SentimentChart
Pie chart showing distribution of complaint sentiments using Recharts.

### CategoryChart
Bar chart showing complaint counts by category using Recharts.

### ReclamacaoCard
Card component displaying complaint details with:
- Title and text
- Sentiment and urgency badges
- User name and timestamp
- Generate response button

### ResponseGeneratorDialog
Modal dialog for:
- Viewing complaint details
- Generating AI responses
- Editing responses
- Viewing coupon information
- Sending responses (mock)

## 🔧 Configuration

### Environment Variables
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)

### Tailwind CSS
Configured with Tailwind CSS v4 and custom theme colors from Shadcn/ui.

### React Query
Default configuration:
- `staleTime`: 60 seconds
- `retry`: 1 attempt
- `refetchOnWindowFocus`: false

## 🚦 Development Workflow

1. **Start the backend first** (ensure it's running on port 8000)
2. **Start the frontend** (`npm run dev`)
3. **Navigate to Dashboard** to view statistics
4. **Navigate to Reclamações** to view and manage complaints
5. **Click "Gerar Resposta"** to test the AI response generator

## 📱 Responsive Design

The application is fully responsive with breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

Grid layouts automatically adjust:
- Mobile: 1 column
- Tablet: 2 columns
- Desktop: 3-4 columns

## 🎨 Color Scheme

### Sentiment Colors
- **Negativo:** Red (`#ef4444`)
- **Neutro:** Yellow (`#eab308`)
- **Positivo:** Green (`#22c55e`)

### Urgency Colors
- **High (7-10):** Destructive (red)
- **Medium (4-6):** Outline (yellow)
- **Low (0-3):** Default (blue)

## 🔄 State Management

- **Server State:** React Query (TanStack Query)
- **Local State:** React useState
- **Form State:** React controlled components

No Zustand store implemented yet (can be added for global client state if needed).

## 🐛 Troubleshooting

### Build Errors
If you encounter TypeScript errors during build:
```bash
npm run build
```
All type errors have been resolved in the current version.

### API Connection Issues
1. Ensure backend is running on `http://localhost:8000`
2. Check `.env.local` file exists and has correct API URL
3. Check browser console for CORS errors

### Missing Data
If dashboard shows no data:
1. Ensure backend has scraped data
2. Check API endpoints are accessible
3. Verify database has complaint records

## 📝 Notes

- Response sending is currently **mocked** (shows toast notification only)
- Coupon generation depends on backend implementation
- Sentiment analysis requires backend ML model
- Date formatting uses Portuguese (pt-BR) locale

## 🚀 Production Deployment

1. Build the application:
```bash
npm run build
```

2. Start production server:
```bash
npm start
```

3. Or deploy to Vercel:
```bash
vercel deploy
```

## 📄 License

Part of the Venâncio RPA project.

---

**Built with ❤️ using Next.js 15 and Shadcn/ui**
