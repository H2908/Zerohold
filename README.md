# ZeroHold 📦

> AI-powered WhatsApp stock assistant for wholesalers. Customers get instant answers — no calls, no hold music.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![OpenAI](https://img.shields.io/badge/GPT--4o-powered-412991?style=flat&logo=openai)](https://openai.com)
[![Stripe](https://img.shields.io/badge/Stripe-billing-635BFF?style=flat&logo=stripe)](https://stripe.com)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

---

## The Problem

Every wholesaler drowns in the same repetitive calls:

> *"Do you have basmati in stock?"*  
> *"What's the price for 100kg of sunflower oil?"*  
> *"What's the minimum order for spices?"*

Staff waste hours answering questions the stock list already answers. Customers wait on hold. Everyone loses.

## The Solution

ZeroHold turns any wholesaler's price list into a 24/7 WhatsApp AI assistant. Customers message as normal — the bot replies instantly with accurate, live stock data.

**Upload a CSV. Connect WhatsApp. Done.**

---

## Demo

```
Customer: Do you have 100kg basmati available?

ZeroHold: ✅ Basmati Rice Premium (R-001) — 500kg in stock at £1.20/kg,
          MOQ 50kg. Also have Standard at £0.90/kg (MOQ 100kg).
          Which grade would you like?

Customer: Is sunflower oil in stock?

ZeroHold: ❌ Sunflower Oil is currently out of stock.
          ✅ We do have Vegetable Oil — 800L available at £1.60/L,
          MOQ 48 units. Would that work as an alternative?
```

---

## Features

- **Any file format** — Upload CSV, Excel, scanned PDF, or a photo of your price board. GPT-4o Vision reads all of it.
- **WhatsApp-first** — Integrates with Meta WhatsApp Cloud API. Works on your existing business number.
- **Image & invoice support** — Customers can send product photos or PDF order forms. Bot identifies the product and checks stock automatically.
- **Auto sync** — Connect Google Sheets or Shopify. Stock updates every 15 minutes with delta detection (only changed rows re-embedded).
- **Multi-tenant SaaS** — Every wholesaler gets their own isolated instance. Full data separation at the database level.
- **Stripe billing** — Starter / Pro / Enterprise plans with self-serve upgrades, downgrades, and cancellations.
- **RAG architecture** — Retrieval-Augmented Generation with pgvector. Answers are always grounded in real stock data — no hallucinations.
- **Confidence scoring** — Every answer includes a similarity score. Low-confidence queries escalate to a human.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python 3.12, asyncpg |
| **AI / LLM** | OpenAI GPT-4o, text-embedding-3-small |
| **Vector DB** | PostgreSQL 16 + pgvector |
| **Document AI** | GPT-4o Vision, pdf2image, pdfplumber |
| **Messaging** | Meta WhatsApp Cloud API |
| **Billing** | Stripe Subscriptions |
| **Stock Sync** | Google Sheets API, Shopify Admin API |
| **Auth** | JWT (PyJWT + bcrypt) |
| **Frontend** | React 18, Vite |
| **Deployment** | Docker, Railway (API), Vercel (frontend) |

---

## Architecture

```
Customer (WhatsApp)
        │
        ▼
Meta Cloud API ──► POST /webhook/whatsapp/{slug}
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
            text         image        PDF
               │           │           │
               │      Vision API   Vision API
               │           │       pdfplumber
               └───────────┼───────────┘
                           │
                    RAG Pipeline
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
          Embed query  pgvector    GPT-4o
          (OpenAI)     search      answer
                           │
                    WhatsApp reply
                           │
                        Customer

Wholesaler Dashboard
        │
        ├── Upload stock (CSV / PDF / JPG)
        ├── Connect WhatsApp credentials
        ├── Google Sheets / Shopify sync
        ├── View all conversations + analytics
        └── Stripe billing portal
```

---

## Project Structure

```
zerohold/
├── backend/
│   ├── app.py                     # FastAPI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── core/
│   │   └── rag.py                 # Embed → pgvector search → GPT-4o
│   ├── api/
│   │   ├── tenant.py              # JWT auth, signup/login, dashboard stats
│   │   ├── upload.py              # Universal file handler
│   │   ├── whatsapp.py            # Meta webhook (text/image/PDF/audio)
│   │   ├── billing.py             # Stripe checkout, portal, webhooks
│   │   └── sync_routes.py         # Sync sources + background scheduler
│   ├── services/
│   │   ├── document_processor.py  # GPT-4o Vision pipeline
│   │   └── sync.py                # Google Sheets + Shopify sync
│   └── db/
│       └── schema.sql             # Full PostgreSQL schema
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                # All UI screens
│       └── api.js                 # API client
├── docker-compose.yml             # Local dev (Postgres + Redis + API)
├── .env.example                   # All required environment variables
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker + Docker Compose
- [OpenAI API key](https://platform.openai.com/api-keys)

### Local Development

**1. Clone the repo**

```bash
git clone https://github.com/yourusername/zerohold.git
cd zerohold
```

**2. Set up environment variables**

```bash
cp .env.example .env
# Fill in your values — minimum required:
# DATABASE_URL, OPENAI_API_KEY, JWT_SECRET
```

**3. Start the database**

```bash
docker-compose up db -d
```

**4. Install backend dependencies**

```bash
cd backend
pip install -r requirements.txt
```

> **Note:** PDF processing requires poppler.
> - Linux: `apt-get install poppler-utils`
> - Mac: `brew install poppler`
> - Docker: already included in the Dockerfile

**5. Run the API**

```bash
uvicorn app:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

**6. Start the frontend**

```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

**7. Load sample data**

```bash
# Sign up a test account
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test Co","email":"test@test.com","password":"password123"}'

# Upload sample stock
curl -X POST http://localhost:8000/api/v1/stock/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@backend/db/sample_stock.csv"
```

---

## Deployment

Full step-by-step deployment guide is in [DEPLOYMENT.md](DEPLOYMENT.md).

**Quick summary — Railway + Supabase + Vercel:**

```bash
# 1. Run schema.sql in Supabase SQL editor

# 2. Deploy backend to Railway
cd backend
railway login && railway init
railway variables set DATABASE_URL="..." OPENAI_API_KEY="sk-..." JWT_SECRET="..."
railway up

# 3. Deploy frontend to Vercel
cd frontend
echo "VITE_API_URL=https://your-api.railway.app/api/v1" > .env.production
vercel --prod
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string (with pgvector) |
| `OPENAI_API_KEY` | ✅ | For GPT-4o and text-embedding-3-small |
| `JWT_SECRET` | ✅ | Random 32-char hex — `openssl rand -hex 32` |
| `META_APP_SECRET` | ✅ | Meta app secret for webhook signature verification |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook signing secret |
| `STRIPE_PRICE_STARTER` | ✅ | Stripe Price ID for Starter plan |
| `STRIPE_PRICE_PRO` | ✅ | Stripe Price ID for Pro plan |
| `STRIPE_PRICE_ENTERPRISE` | ✅ | Stripe Price ID for Enterprise plan |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated list of allowed frontend URLs |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ⬜ | Path to Google service account key (for Sheets sync) |
| `SHOPIFY_WEBHOOK_SECRET` | ⬜ | Shopify webhook HMAC secret |

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/signup` | — | Create wholesaler account |
| `POST` | `/api/v1/auth/login` | — | Get JWT token |
| `POST` | `/api/v1/stock/upload` | JWT | Upload CSV / PDF / JPG |
| `GET` | `/api/v1/stock/job/{id}` | JWT | Poll ingestion job status |
| `GET` | `/api/v1/dashboard/stats` | JWT | KPI metrics |
| `GET` | `/api/v1/dashboard/products` | JWT | Product catalogue |
| `POST` | `/api/v1/settings/whatsapp` | JWT | Save WhatsApp credentials |
| `POST` | `/api/v1/billing/checkout` | JWT | Create Stripe checkout session |
| `POST` | `/api/v1/billing/portal` | JWT | Open Stripe customer portal |
| `GET` | `/api/v1/billing/usage` | JWT | Current usage vs plan limits |
| `POST` | `/api/v1/sync/sources` | JWT | Add Google Sheets or Shopify source |
| `GET` | `/api/v1/sync/sources` | JWT | List sync sources |
| `POST` | `/api/v1/sync/run/{id}` | JWT | Trigger manual sync |
| `GET` | `/webhook/whatsapp/{slug}` | — | Meta webhook verification |
| `POST` | `/webhook/whatsapp/{slug}` | — | Receive WhatsApp messages |
| `GET` | `/health` | — | Health check |

Full interactive docs available at `/docs` when the API is running.

---

## Pricing Model

| Plan | Price | Messages/mo | Products | Users |
|---|---|---|---|---|
| Starter | £29/mo | 500 | 500 | 1 |
| Pro | £79/mo | 5,000 | 5,000 | 5 |
| Enterprise | £249/mo | Unlimited | Unlimited | Unlimited |

### Unit Economics at Scale

| Wholesalers | Revenue/mo | Running Cost | Gross Margin |
|---|---|---|---|
| 10 | £790 | ~£40 | 95% |
| 100 | £7,900 | ~£285 | 96% |
| 1,000 | £79,000 | ~£2,450 | 97% |

---

## How the RAG Pipeline Works

```
1. INGEST
   CSV / PDF / JPG
        │
        ▼
   Extract products
   (pandas / GPT-4o Vision)
        │
        ▼
   Generate text chunk per product:
   "Basmati Rice Premium | IN STOCK: 500kg | £1.20/kg | MOQ 50kg"
        │
        ▼
   Embed with text-embedding-3-small (1536 dims)
        │
        ▼
   Upsert into pgvector (scoped to tenant_id)

2. QUERY
   Customer message → embed → cosine similarity search
        │
        ▼
   Top 4 matching product chunks retrieved
        │
        ▼
   GPT-4o generates answer grounded in those chunks
        │
        ▼
   Confidence score returned (avg cosine similarity)
```

No fine-tuning. No retraining. Stock updates in under 60 seconds.

---

## WhatsApp Message Routing

```
Incoming message
       │
       ├── type: text     → RAG query → reply
       ├── type: image    → GPT-4o Vision identifies product → RAG query → reply
       ├── type: document → Extract order from PDF → stock check → reply
       └── type: audio    → "Please send a text message" (graceful decline)
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

```bash
# Run tests
cd backend
pytest

# Lint
ruff check .
```

---

## Roadmap

- [ ] SMS channel (Twilio)
- [ ] Embeddable website chat widget
- [ ] ERP integrations (Tally, Sage, Xero)
- [ ] Order placement via WhatsApp
- [ ] Stock reorder alerts
- [ ] Multi-language support
- [ ] Customer order history
- [ ] Bulk WhatsApp broadcast for back-in-stock notifications

---

## License

[MIT](LICENSE)

---

## Acknowledgements

Built with [FastAPI](https://fastapi.tiangolo.com), [pgvector](https://github.com/pgvector/pgvector), [OpenAI](https://openai.com), [Stripe](https://stripe.com), and the [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api).

---

*Built to solve a real problem. Every wholesaler has this problem. Now they don't have to.*

