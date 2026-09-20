# Sales Analytics Platform

A learning project that mirrors a real enterprise analytics stack:

```
PostgreSQL  --->  FastAPI backend (Python)  --->  React dashboard
(local)            reads DB, computes metrics,     fetches API, renders charts
                   exposes JSON API
```

Each layer is an independently runnable piece, matching how real companies
split systems into services.

## Project layout

```
sales-analytics-platform/
├── database/
│   ├── init/01_schema.sql   # table definitions, auto-run on first DB start
│   └── seed/seed_data.py    # generates realistic fake sales data
├── backend/
│   ├── database.py          # opens a connection to Postgres using .env
│   └── main.py               # FastAPI app: routes + analytics queries
├── frontend/                 # React app (Vite) — fetches the API, renders charts
├── docker-compose.yml       # optional: alternative way to run Postgres in a container
├── .env.example             # template for required environment variables
└── .env                     # your real local config (gitignored, not committed)
```

## Data model

Four tables model a simple sales business:

- **customers** — who buys
- **products** — what's sold
- **orders** — one purchase event (header info: date, status, customer)
- **order_items** — the line items within an order (product, quantity, price)

`orders` and `order_items` are split because one order can contain multiple
products — a standard "header/detail" pattern used in virtually every
real-world sales/e-commerce schema.

## Stage 1: Database setup ✅

Uses a local Postgres install (via [Postgres.app](https://postgresapp.com/)) rather
than Docker, to keep one less new tool in play while learning.

1. Make sure Postgres is running locally (Postgres.app or otherwise) and create
   a database:
   ```
   createdb sales_analytics
   ```
2. Create the tables:
   ```
   psql -d sales_analytics -f database/init/01_schema.sql
   ```
3. Copy `.env.example` to `.env` and fill in your local connection details
   (host, port, user, database — password can be blank if your local Postgres
   uses trust auth).
4. Seed it with fake data:
   ```
   cd database/seed
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python seed_data.py
   ```
5. Verify the data landed:
   ```
   psql -d sales_analytics -c "SELECT COUNT(*) FROM orders;"
   ```

> `docker-compose.yml` is still in the repo as an alternative way to run
> Postgres in a container, if you'd rather use Docker later.

## Stage 2: FastAPI backend ✅

A FastAPI app that connects to the database and exposes analytics as JSON.

1. Set up its own virtual environment:
   ```
   cd backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install fastapi uvicorn "psycopg[binary]" python-dotenv
   ```
2. Run the server:
   ```
   uvicorn main:app --reload
   ```
3. Explore it:
   - `http://127.0.0.1:8000/` — basic health check
   - `http://127.0.0.1:8000/docs` — interactive API explorer (auto-generated)
   - `http://127.0.0.1:8000/health/db` — confirms the DB connection works
   - `http://127.0.0.1:8000/customers?limit=&offset=` — paginated customer list
   - `http://127.0.0.1:8000/analytics/revenue-by-month` — total revenue grouped by month
   - `http://127.0.0.1:8000/analytics/top-products?limit=` — highest-revenue products

## Stage 3: React frontend ✅

A Vite + React app that fetches the backend's analytics endpoints and renders
them as charts (using [Recharts](https://recharts.org/)), plus a plain table
view of the same data.

1. Set up and run it:
   ```
   cd frontend
   npm install
   npm run dev
   ```
2. Open `http://localhost:5173` — you should see a revenue-by-month line
   chart, a table view of the same data, and a top-products bar chart.

Note: the backend has CORS enabled specifically for `http://localhost:5173`
(see `backend/main.py`), which is what lets the browser call the API across
ports during local development.

Both the backend (`uvicorn main:app --reload`) and frontend (`npm run dev`)
need to be running at the same time for the dashboard to load data.

## Coming next

- **Stage 4:** Deploy the whole stack to a free cloud host.
