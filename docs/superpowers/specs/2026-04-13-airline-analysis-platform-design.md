# Airline Market Demand Analysis Platform - Design Spec

## Overview
Production-grade full-stack SaaS platform for Australian hostel operators to track airline booking trends, price movements, and demand patterns.

## Architecture
- **Backend:** Python 3.11+ / Flask 3.x (app factory pattern)
- **Frontend:** React 18 + TypeScript + Vite
- **Database:** PostgreSQL (prod) / SQLite (dev) via Flask-SQLAlchemy
- **Cache/Broker:** Redis (Flask-Caching, Flask-Limiter, Celery)
- **AI:** Anthropic Claude API (streaming SSE)
- **ML:** scikit-learn + statsmodels (price forecasting, anomaly detection)
- **3D:** Three.js + @react-three/fiber + framer-motion-3d
- **Deployment:** Docker Compose + Nginx + GitHub Actions CI

## Data Model
- User (UUID PK, bcrypt auth, org membership, watched routes, encrypted API keys)
- Organization (plan: free/pro)
- Flight (200/run, computed demand_score, anomaly flags)
- Route (aggregated stats: avg_price_7d/30d, demand_trend)
- PriceSnapshot (time-series per route per airline)
- AlertRule / AlertFired (user-defined price/demand alerts)
- Notification (alert, digest, system types)
- ForecastSnapshot (14-day forward predictions)

## Core Data Flow
1. DataScraper generates 200 synthetic flights using route base prices + airline multipliers + demand formula
2. DemandScoreEngine computes scores: 30% route popularity + 25% seasonality + 20% days-until + 15% day-of-week + 10% holiday proximity
3. Price = base * airline_multiplier * (1 + demand * 0.6) * gaussian noise
4. DataProcessor runs anomaly detection (2-sigma on 7-day rolling stats)
5. ForecastEngine produces 14-day predictions (LinearRegression baseline, ARIMA for routes with 30+ days history)
6. AIInsightGenerator streams market analysis via Claude API
7. Celery tasks: refresh every 6h, check alerts after refresh, weekly digest Monday 8am AEST

## API Design
- REST API at /api/v1/ with Flask-RESTX (Swagger at /api/docs)
- JWT Bearer for API, session cookies for web
- Rate limits: 1000/hr authenticated, 100/hr unauth, 10/min login, 5/min register
- SSE endpoint for streaming AI insights
- CRUD alerts, paginated routes/prices, export CSV/Excel/PDF

## Security
- bcrypt cost 12, JWT 15min access / 7d refresh
- Email verification, account lockout (5 failures, 30min)
- AES-256-GCM encryption for stored third-party API keys
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- HMAC-SHA256 signed webhooks
- Input validation via marshmallow, XSS prevention via bleach
- No raw SQL, no hardcoded secrets

## Frontend Pages
- Landing (3D Australia globe hero)
- Dashboard (KPI cards with 3D spheres, route arc map, AI briefing, charts)
- Routes (filterable table, detail drawer)
- Forecast (historical + prediction cone chart)
- Alerts (CRUD rules, fired history)
- Reports (date picker, PDF/CSV/Excel export)
- Settings (profile, API keys, notifications, security)
- Auth (login/register with animated tab switch)
- AI Chat Panel (floating, SSE streaming, prompt chips)

## Build Order (20 steps)
1. Backend foundation (app factory, extensions, config, models, migrations)
2. Data generator + demand engine (with tests)
3. SQLAlchemy persistence + Route aggregates
4. REST API endpoints (data, no auth)
5. Auth system (register, login, JWT, email verify, password reset)
6. Security hardening (rate limiting, headers, validation, encryption)
7. Background tasks (APScheduler + Celery + Redis)
8. Forecast engine + anomaly detection
9. AI insights with Claude API (streaming SSE)
10. Email notifications + webhook delivery
11. Export endpoints (CSV, Excel, async PDF)
12. Frontend scaffold (Vite + React + TS, router, auth pages)
13. Design system (Tailwind, shadcn/ui)
14. 21st.dev component integration
15. Framer Motion animations
16. 3D components (globe, route arcs, KPI spheres)
17. Pages wired to backend via React Query
18. AI chat panel with SSE
19. Docker Compose full stack
20. GitHub Actions CI

## Source Spec
Full detailed spec in `airline-analysis-claude-code-prompt.md` at project root.
