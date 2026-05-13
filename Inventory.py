#!/usr/bin/env python3
"""
CLI Inventory Manager
Terminal-only app using Docker + MySQL
Compatible with Killercoda and Google Cloud Console
"""

import sys
import argparse
import mysql.connector
from mysql.connector import Error

# ─────────────────────────────────────────
#  DB Connection
# ─────────────────────────────────────────

def get_connection():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='inventorydb'
        )
        return conn
    except Error as e:
        print(f"\n[ERROR] Cannot connect to MySQL: {e}")
        print("Make sure the container is running: docker ps")
        sys.exit(1)


# ─────────────────────────────────────────
#  Commands
# ─────────────────────────────────────────

def cmd_add(name, category, quantity, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (name, category, quantity, price) VALUES (%s, %s, %s, %s)",
        (name, category, quantity, price)
    )
    item_id = cur.lastrowid
    cur.execute(
        "INSERT INTO transactions (item_id, type, quantity, note) VALUES (%s, 'IN', %s, 'Initial stock')",
        (item_id, quantity)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n[ADDED] ID:{item_id}  {name}  ({category})  Qty:{quantity}  ${price:.2f}\n")


def cmd_list(category=None):
    conn = get_connection()
    cur = conn.cursor()
    if category:
        cur.execute(
            "SELECT id, name, category, quantity, price FROM items WHERE category=%s ORDER BY id",
            (category,)
        )
    else:
        cur.execute("SELECT id, name, category, quantity, price FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("\nNo items found.\n")
        return

    print(f"\n{'ID':<5} {'Name':<22} {'Category':<15} {'Qty':<8} {'Price'}")
    print("─" * 60)
    for r in rows:
        stock_warn = " ⚠ LOW" if r[3] < 5 else ""
        print(f"{r[0]:<5} {r[1]:<22} {r[2]:<15} {r[3]:<8} ${r[4]:.2f}{stock_warn}")
    print()


def cmd_restock(item_id, quantity, note="Restocked"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, quantity FROM items WHERE id=%s", (item_id,))
    row = cur.fetchone()
    if not row:
        print(f"\n[ERROR] No item with ID {item_id}\n")
        cur.close()
        conn.close()
        return
    new_qty = row[1] + quantity
    cur.execute("UPDATE items SET quantity=%s WHERE id=%s", (new_qty, item_id))
    cur.execute(
        "INSERT INTO transactions (item_id, type, quantity, note) VALUES (%s, 'IN', %s, %s)",
        (item_id, quantity, note)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n[RESTOCKED] {row[0]}  +{quantity}  →  New qty: {new_qty}\n")


def cmd_sell(item_id, quantity, note="Sold"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, quantity FROM items WHERE id=%s", (item_id,))
    row = cur.fetchone()
    if not row:
        print(f"\n[ERROR] No item with ID {item_id}\n")
        cur.close()
        conn.close()
        return
    if row[1] < quantity:
        print(f"\n[ERROR] Not enough stock. Available: {row[1]}\n")
        cur.close()
        conn.close()
        return
    new_qty = row[1] - quantity
    cur.execute("UPDATE items SET quantity=%s WHERE id=%s", (new_qty, item_id))
    cur.execute(
        "INSERT INTO transactions (item_id, type, quantity, note) VALUES (%s, 'OUT', %s, %s)",
        (item_id, quantity, note)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n[SOLD] {row[0]}  -{quantity}  →  Remaining: {new_qty}\n")


def cmd_delete(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM items WHERE id=%s", (item_id,))
    row = cur.fetchone()
    if not row:
        print(f"\n[ERROR] No item with ID {item_id}\n")
        cur.close()
        conn.close()
        return
    cur.execute("DELETE FROM transactions WHERE item_id=%s", (item_id,))
    cur.execute("DELETE FROM items WHERE id=%s", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n[DELETED] Removed '{row[0]}' (ID:{item_id})\n")


def cmd_history(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM items WHERE id=%s", (item_id,))
    row = cur.fetchone()
    if not row:
        print(f"\n[ERROR] No item with ID {item_id}\n")
        cur.close()
        conn.close()
        return
    cur.execute(
        "SELECT type, quantity, note, done_at FROM transactions WHERE item_id=%s ORDER BY done_at",
        (item_id,)
    )
    logs = cur.fetchall()
    cur.close()
    conn.close()

    print(f"\n Transaction History — {row[0]} (ID:{item_id})")
    print("─" * 55)
    print(f"{'Type':<6} {'Qty':<6} {'Note':<25} {'Time'}")
    print("─" * 55)
    for l in logs:
        direction = "+" if l[0] == "IN" else "-"
        print(f"{l[0]:<6} {direction}{l[1]:<5} {l[2]:<25} {l[3]}")
    print()


def cmd_report():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), SUM(quantity), SUM(quantity * price) FROM items")
    totals = cur.fetchone()

    cur.execute("""
        SELECT category, COUNT(*) as c, SUM(quantity) as qty, SUM(quantity * price) as val
        FROM items
        GROUP BY category
        ORDER BY val DESC
    """)
    by_cat = cur.fetchall()

    cur.execute("SELECT name, quantity FROM items WHERE quantity < 5 ORDER BY quantity")
    low_stock = cur.fetchall()

    cur.execute("""
        SELECT i.name, SUM(t.quantity) as sold
        FROM transactions t
        JOIN items i ON i.id = t.item_id
        WHERE t.type = 'OUT'
        GROUP BY i.name
        ORDER BY sold DESC
        LIMIT 3
    """)
    top_sold = cur.fetchall()

    cur.close()
    conn.close()

    print("\n" + "═" * 45)
    print("          INVENTORY REPORT")
    print("═" * 45)
    print(f"  Total unique items : {totals[0]}")
    print(f"  Total units        : {totals[1] or 0}")
    print(f"  Total stock value  : ${totals[2] or 0:.2f}")

    print("\n  By Category:")
    print(f"  {'Category':<15} {'Items':<7} {'Units':<7} {'Value'}")
    print("  " + "─" * 40)
    for c in by_cat:
        print(f"  {c[0]:<15} {c[1]:<7} {c[2]:<7} ${c[3]:.2f}")

    if low_stock:
        print("\n  ⚠  Low Stock Alerts (< 5 units):")
        for item in low_stock:
            print(f"     - {item[0]}: {item[1]} left")

    if top_sold:
        print("\n  Top Sold Items:")
        for item in top_sold:
            print(f"     - {item[0]}: {item[1]} units sold")

    print("═" * 45 + "\n")


# ─────────────────────────────────────────
#  Argument Parser
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="inventory.py",
        description="CLI Inventory Manager — Docker + MySQL, no UI needed"
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # add
    p_add = sub.add_parser("add", help="Add a new item to inventory")
    p_add.add_argument("name",     type=str,   help="Item name")
    p_add.add_argument("quantity", type=int,   help="Initial stock quantity")
    p_add.add_argument("price",    type=float, help="Unit price")
    p_add.add_argument("--category", "-c", type=str, default="General", help="Category (default: General)")

    # list
    p_list = sub.add_parser("list", help="List all items")
    p_list.add_argument("--category", "-c", type=str, help="Filter by category")

    # restock
    p_restock = sub.add_parser("restock", help="Add stock to an existing item")
    p_restock.add_argument("id",       type=int, help="Item ID")
    p_restock.add_argument("quantity", type=int, help="Units to add")
    p_restock.add_argument("--note",   type=str, default="Restocked")

    # sell
    p_sell = sub.add_parser("sell", help="Reduce stock (record a sale)")
    p_sell.add_argument("id",       type=int, help="Item ID")
    p_sell.add_argument("quantity", type=int, help="Units sold")
    p_sell.add_argument("--note",   type=str, default="Sold")

    # delete
    p_del = sub.add_parser("delete", help="Remove an item from inventory")
    p_del.add_argument("id", type=int, help="Item ID")

    # history
    p_hist = sub.add_parser("history", help="Show transaction history for an item")
    p_hist.add_argument("id", type=int, help="Item ID")

    # report
    sub.add_parser("report", help="Show full inventory summary report")

    args = parser.parse_args()

    if   args.command == "add":     cmd_add(args.name, args.category, args.quantity, args.price)
    elif args.command == "list":    cmd_list(args.category)
    elif args.command == "restock": cmd_restock(args.id, args.quantity, args.note)
    elif args.command == "sell":    cmd_sell(args.id, args.quantity, args.note)
    elif args.command == "delete":  cmd_delete(args.id)
    elif args.command == "history": cmd_history(args.id)
    elif args.command == "report":  cmd_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
