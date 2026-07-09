# db.py

import sqlite3

DB_NAME = "restaurant.db"


def get_connection():
  return sqlite3.connect(DB_NAME)


def get_available_table(category):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    """
    SELECT table_id
    FROM restaurant_tables
    WHERE category = ?
    AND is_available = 1
    LIMIT 1
    """,
    (category,)
  )

  row = cur.fetchone()
  conn.close()
  return row[0] if row else None


def mark_table_unavailable(table_id):
  conn = get_connection()
  cur = conn.cursor()
  cur.execute(
    "UPDATE restaurant_tables SET is_available = 0 WHERE table_id = ?",
    (table_id,)
  )
  conn.commit()
  conn.close()


def add_customer(name, phone):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    "INSERT INTO customers (name, phone) VALUES (?, ?)",
    (name, phone)
  )
  customer_id = cur.lastrowid

  conn.commit()
  conn.close()
  return customer_id


def create_order(customer_id, table_id):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    """
    INSERT INTO orders (customer_id, table_id, status)
    VALUES (?, ?, 'IN_PROGRESS')
    """,
    (customer_id, table_id)
  )

  order_id = cur.lastrowid
  conn.commit()
  conn.close()
  return order_id

def get_menu_items():
  conn = get_connection()
  cur = conn.cursor()

  cur.execute("""
    SELECT item_id, item_name, category, price
    FROM menu
  """)

  rows = cur.fetchall()
  conn.close()
  return rows


def add_order_item(order_id, item_id, quantity):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    """
    INSERT INTO order_items (order_id, item_id, quantity)
    VALUES (?, ?, ?)
    """,
    (order_id, item_id, quantity)
  )

  conn.commit()
  conn.close()

def get_all_orders():
  conn = get_connection()
  cur = conn.cursor()

  cur.execute("""
    SELECT
      o.order_id,
      o.customer_id,
      o.table_id,
      rt.category,
      o.status
    FROM orders o
    JOIN restaurant_tables rt ON o.table_id = rt.table_id
    WHERE o.visible = 1
    ORDER BY o.order_id DESC
  """)

  rows = cur.fetchall()
  conn.close()
  return rows

def get_order_items(order_id):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute("""
    SELECT
      m.item_name,
      m.price,
      oi.quantity,
      (m.price * oi.quantity) AS subtotal
    FROM order_items oi
    JOIN menu m ON oi.item_id = m.item_id
    WHERE oi.order_id = ?
  """, (order_id,))

  rows = cur.fetchall()
  conn.close()
  return rows

def complete_order(order_id):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    "UPDATE orders SET status = 'COMPLETED' WHERE order_id = ?",
    (order_id,)
  )

  conn.commit()
  conn.close()

def release_table(table_id):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    "UPDATE restaurant_tables SET is_available = 1 WHERE table_id = ?",
    (table_id,)
  )

  conn.commit()
  conn.close()

def get_total_revenue():
  conn = get_connection()
  cur = conn.cursor()

  cur.execute("""
    SELECT SUM(m.price * oi.quantity)
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu m ON oi.item_id = m.item_id
    WHERE o.status = 'COMPLETED'
  """)

  result = cur.fetchone()[0]
  conn.close()
  return result or 0

def get_item_sales():
  conn = get_connection()
  cur = conn.cursor()

  cur.execute("""
    SELECT
      m.item_name,
      SUM(oi.quantity) as total_qty
    FROM order_items oi
    JOIN menu m ON oi.item_id = m.item_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'COMPLETED'
    GROUP BY m.item_name
  """)

  rows = cur.fetchall()
  conn.close()
  return rows

def hide_order(order_id):
  conn = get_connection()
  cur = conn.cursor()

  cur.execute(
    "UPDATE orders SET visible = 0 WHERE order_id = ?",
    (order_id,)
  )

  conn.commit()
  conn.close()


def reset_database():
  conn = get_connection()
  cur = conn.cursor()

  cur.execute("DELETE FROM order_items")
  cur.execute("DELETE FROM orders")
  cur.execute("DELETE FROM customers")

  cur.execute("""
    UPDATE restaurant_tables
    SET is_available = 1
  """)

  conn.commit()
  conn.close()

