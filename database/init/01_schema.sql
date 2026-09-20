-- Sales Analytics schema
-- Runs automatically when the Postgres container first initializes.

CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    region        VARCHAR(50)  NOT NULL,   -- e.g. 'North America', 'Europe'
    segment       VARCHAR(50)  NOT NULL,   -- e.g. 'Enterprise', 'SMB', 'Consumer'
    signup_date   DATE         NOT NULL
);

CREATE TABLE products (
    product_id    SERIAL PRIMARY KEY,
    product_name  VARCHAR(150) NOT NULL,
    category      VARCHAR(50)  NOT NULL,   -- e.g. 'Electronics', 'Office Supplies'
    unit_price    NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date    DATE    NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'completed'
                  CHECK (status IN ('completed', 'refunded', 'cancelled'))
);

-- An order can contain multiple products, and a product can appear in many
-- orders — that's a many-to-many relationship, which relational databases
-- model with a "join table" like order_items sitting between them.
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    -- Price is captured here at the moment of sale, not looked up from
    -- products.unit_price. Product prices change over time; if we didn't
    -- snapshot it, an old order's revenue would silently change whenever
    -- today's price changes. This is a common real-world data modeling trap.
    unit_price    NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- Indexes speed up the lookups our analytics queries will do constantly:
-- "revenue per month" scans order_date, "sales by customer" joins on
-- customer_id, etc. Without these, Postgres has to scan the whole table.
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date  ON orders(order_date);
CREATE INDEX idx_order_items_order_id   ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
