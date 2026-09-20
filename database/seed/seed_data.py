"""
Fills the sales_analytics database with realistic fake data so we have
something to build analytics and dashboards against.

Run this ONCE after the database container is up and the schema exists:
    python seed_data.py

Why fake data with Faker instead of typing rows by hand? Real projects
almost never start with real production data available on day one — you
build and test against realistic-looking synthetic data first.
"""

import os
import random
from datetime import date, timedelta
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from faker import Faker

# Load variables from the project's .env file (DATABASE_URL, etc.). Resolved
# from this file's own location (not a relative path) so it works no matter
# which directory you run the script from.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

fake = Faker()
random.seed(42)  # fixed seed = same "random" data every run, easier to debug

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America"]
SEGMENTS = ["Enterprise", "SMB", "Consumer"]

# category -> (price_min, price_max)
CATEGORIES = {
    "Electronics": (50, 1200),
    "Office Supplies": (5, 150),
    "Furniture": (80, 900),
    "Software Licenses": (20, 500),
    "Accessories": (10, 200),
}


def get_connection():
    return psycopg.connect(os.environ["DATABASE_URL"])


def seed_products(cur, count=40):
    """Insert `count` products and return their (id, price) pairs."""
    products = []
    for _ in range(count):
        category = random.choice(list(CATEGORIES.keys()))
        low, high = CATEGORIES[category]
        price = round(random.uniform(low, high), 2)
        name = f"{fake.word().capitalize()} {category[:-1] if category.endswith('s') else category}"
        products.append((name, category, price))

    # executemany + a parameterized query (the %s placeholders) is how you
    # safely insert data in bulk. Never build SQL with f-strings/concatenation
    # from user input — that's how SQL injection vulnerabilities happen.
    cur.executemany(
        """
        INSERT INTO products (product_name, category, unit_price)
        VALUES (%s, %s, %s)
        """,
        products,
    )
    return products


def seed_customers(cur, count=250):
    for _ in range(count):
        signup_date = fake.date_between(start_date="-3y", end_date="today")
        cur.execute(
            """
            INSERT INTO customers (first_name, last_name, email, region, segment, signup_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                fake.first_name(),
                fake.last_name(),
                fake.unique.email(),
                random.choice(REGIONS),
                random.choice(SEGMENTS),
                signup_date,
            ),
        )


def seed_orders_and_items(cur, num_orders=3000):
    cur.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT product_id, unit_price FROM products")
    products = cur.fetchall()  # list of (product_id, unit_price)

    today = date.today()
    two_years_ago = today - timedelta(days=730)

    for _ in range(num_orders):
        order_date = fake.date_between(start_date=two_years_ago, end_date=today)
        # Slightly favor "completed" so the data looks realistic.
        status = random.choices(
            ["completed", "refunded", "cancelled"], weights=[0.9, 0.06, 0.04]
        )[0]

        cur.execute(
            """
            INSERT INTO orders (customer_id, order_date, status)
            VALUES (%s, %s, %s)
            RETURNING order_id
            """,
            (random.choice(customer_ids), order_date, status),
        )
        order_id = cur.fetchone()[0]

        # Each order has 1-4 line items (order_items).
        for _ in range(random.randint(1, 4)):
            product_id, base_price = random.choice(products)
            quantity = random.randint(1, 5)
            cur.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, product_id, quantity, base_price),
            )


def main():
    conn = get_connection()
    conn.autocommit = False  # we control the transaction explicitly
    cur = conn.cursor()

    try:
        print("Seeding products...")
        seed_products(cur)

        print("Seeding customers...")
        seed_customers(cur)

        print("Seeding orders and order items (this takes a few seconds)...")
        seed_orders_and_items(cur)

        conn.commit()  # only save changes if everything above succeeded
        print("Done. Data committed.")
    except Exception:
        conn.rollback()  # undo everything on any error, leaving a clean state
        print("Something went wrong — rolled back all changes.")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
