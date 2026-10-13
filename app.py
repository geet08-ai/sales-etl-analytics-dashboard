from flask import Flask, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "sales.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@app.route("/")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/analytics")
def analytics():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS total_orders FROM sales")
    total_orders = cursor.fetchone()["total_orders"]

    cursor.execute("SELECT COALESCE(SUM(total), 0) AS revenue FROM sales")
    total_revenue = cursor.fetchone()["revenue"]

    cursor.execute("""
        SELECT product, SUM(total) AS revenue
        FROM sales
        GROUP BY product
        ORDER BY revenue DESC
    """)
    product_revenue = [
        dict(row) for row in cursor.fetchall()
    ]

    cursor.execute("""
        SELECT customer, COUNT(*) AS order_count
        FROM sales
        GROUP BY customer
        ORDER BY order_count DESC, customer ASC
    """)
    customer_orders = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return jsonify({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "product_revenue": product_revenue,
        "customer_orders": customer_orders
    })


if __name__ == "__main__":
    app.run(debug=False)