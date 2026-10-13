import csv
import sqlite3

input_file = "data/sales.csv"

valid_records = []
rejected_records = []

# STEP 1: EXTRACT and TRANSFORM
with open(input_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if not row["customer"].strip():
            row["rejection_reason"] = "Missing customer name"
            rejected_records.append(row)
            continue

        try:
            quantity = int(row["quantity"])
            price = float(row["price"])

            if quantity <= 0 or price <= 0:
                raise ValueError("Values must be positive")

        except ValueError:
            row["rejection_reason"] = "Invalid quantity or price"
            rejected_records.append(row)
            continue

        row["quantity"] = quantity
        row["price"] = price
        row["total"] = quantity * price

        valid_records.append(row)

# STEP 2: LOAD into SQLite
connection = sqlite3.connect("sales.db")
cursor = connection.cursor()

# Create the table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        order_id INTEGER PRIMARY KEY,
        customer TEXT NOT NULL,
        product TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total REAL NOT NULL
    )
""")

# Refresh the demo table on each run
cursor.execute("DELETE FROM sales")

# Insert the cleaned records
for record in valid_records:
    cursor.execute("""
        INSERT INTO sales
        (order_id, customer, product, quantity, price, total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        int(record["order_id"]),
        record["customer"],
        record["product"],
        record["quantity"],
        record["price"],
        record["total"]
    ))

connection.commit()

# Verify the number of loaded records
cursor.execute("SELECT COUNT(*) FROM sales")
loaded_count = cursor.fetchone()[0]

print("ETL PIPELINE SUMMARY")
print("Valid records:", len(valid_records))
print("Rejected records:", len(rejected_records))
print("Records loaded into database:", loaded_count)
# STEP 3: SQL ANALYTICS

# Query 1: Calculate total revenue
cursor.execute("""
    SELECT SUM(total)
    FROM sales
""")

revenue = cursor.fetchone()[0]
print("\nTOTAL REVENUE:", revenue)


# Query 2: Find revenue by product
cursor.execute("""
    SELECT product, SUM(total) AS revenue
    FROM sales
    GROUP BY product
    ORDER BY revenue DESC
""")

print("\nREVENUE BY PRODUCT")
for product, revenue in cursor.fetchall():
    print(product, ":", revenue)


# Query 3: Count orders for each customer
cursor.execute("""
    SELECT customer, COUNT(*) AS order_count
    FROM sales
    GROUP BY customer
    ORDER BY order_count DESC, customer ASC
""")

print("\nORDERS BY CUSTOMER")
for customer, count in cursor.fetchall():
    print(customer, ":", count)


# Query 4: Find the highest-value order
cursor.execute("""
    SELECT order_id, customer, product, total
    FROM sales
    ORDER BY total DESC
    LIMIT 1
""")

print("\nHIGHEST-VALUE ORDER")
print(cursor.fetchone())

connection.close()