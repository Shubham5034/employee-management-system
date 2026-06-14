from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request
import psycopg2

load_dotenv()

app = Flask(__name__)


# ---------------- DB CONNECTION ----------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )


# ---------------- HEALTH ----------------
@app.route("/health")
def health():
    return jsonify({"status": "UP"})


# ---------------- GET ALL EMPLOYEES ----------------
@app.route("/employees", methods=["GET"])
def get_employees():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM employees ORDER BY id")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "name": r[1],
            "department": r[2],
            "salary": r[3],
            "created_at": str(r[4])
        }
        for r in rows
    ])

# ---------------- SEARCH API   ----------------
@app.route("/employees/search", methods=["GET"])
def search_employees():
    query = request.args.get("q", "").strip()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, department, salary, created_at
        FROM employees
        WHERE name ILIKE %s
           OR department ILIKE %s
        ORDER BY id
    """, (f"%{query}%", f"%{query}%"))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "name": r[1],
            "department": r[2],
            "salary": r[3],
            "created_at": str(r[4])
        }
        for r in rows
    ])

# ---------------- ADD EMPLOYEE ----------------
@app.route("/employees", methods=["POST"])
def add_employee():
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO employees (name, department, salary) VALUES (%s, %s, %s) RETURNING id",
        (data["name"], data["department"], data["salary"])
    )

    emp_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Employee added", "id": emp_id})

# ---------------- UPDATE EMPLOYEE ----------------
@app.route("/employees/<int:emp_id>", methods=["PUT"])
def update_employee(emp_id):
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE employees
        SET name = %s,
            department = %s,
            salary = %s
        WHERE id = %s
    """, (
        data["name"],
        data["department"],
        data["salary"],
        emp_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Employee updated"})

# ---------------- DELETE EMPLOYEE ----------------
@app.route("/employees/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM employees WHERE id = %s", (emp_id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Employee deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
