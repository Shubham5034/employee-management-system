from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request
import psycopg2

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn


@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/db-check")
def db_check():
    try:
        conn = get_db_connection()
        conn.close()

        return jsonify({
            "database": "connected"
        })

    except Exception as e:
        return jsonify({
            "database": "failed",
            "error": str(e)
        }), 500


@app.route("/employees", methods=["GET"])
def get_employees():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, department, salary, created_at FROM employees"
    )

    rows = cursor.fetchall()

    employees = []

    for row in rows:
        employees.append({
            "id": row[0],
            "name": row[1],
            "department": row[2],
            "salary": row[3],
            "created_at": str(row[4])
        })

    cursor.close()
    conn.close()

    return jsonify(employees)


@app.route("/employees", methods=["POST"])
def create_employee():

    data = request.json

    name = data["name"]
    department = data["department"]
    salary = data["salary"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO employees
        (name, department, salary)
        VALUES (%s,%s,%s)
        """,
        (name, department, salary)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Employee created"
    }), 201



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )


