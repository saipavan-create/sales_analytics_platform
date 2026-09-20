from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection

app = FastAPI(title="Sales Analytics API")

# Browsers block a webpage on one origin (localhost:5173, the React dev
# server) from calling an API on a different origin (localhost:8000) unless
# the API explicitly allows it. This is that permission.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Sales Analytics API is running"}


@app.get("/health/db")
def health_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM customers")
    (customer_count,) = cur.fetchone()
    cur.close()
    conn.close()
    return {"status": "connected", "customer_count": customer_count}


@app.get("/customers")
def list_customers(limit: int = 20, offset: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT customer_id, first_name, last_name, email, region, segment, signup_date
        FROM customers
        ORDER BY customer_id
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    # zip each row's values with the column names so the JSON has readable
    # keys (e.g. "first_name") instead of a bare list of values.
    return [dict(zip(columns, row)) for row in rows]


@app.get("/analytics/revenue-by-month")
def revenue_by_month():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            date_trunc('month', o.order_date) AS month,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY month
        ORDER BY month
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"month": month.strftime("%Y-%m"), "revenue": float(revenue)}
        for month, revenue in rows
    ]


@app.get("/analytics/top-products")
def top_products(limit: int = 10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            p.product_name,
            p.category,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT %s
        """,
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"product_name": name, "category": category, "revenue": float(revenue)}
        for name, category, revenue in rows
    ]
