import os
import sqlite3
from flask import Flask, request, jsonify, render_template

# Ensure the 'database' directory exists
os.makedirs('database', exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('database/company.db')  # Database will be created automatically
    conn.row_factory = sqlite3.Row
    return conn

# Create tables and insert sample data
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Department TEXT NOT NULL,
            Salary INTEGER NOT NULL,
            Hire_Date TEXT NOT NULL
        )
    ''')

    # Create Departments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departments (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Manager TEXT NOT NULL
        )
    ''')

    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO Employees VALUES (1, 'Alice', 'Sales', 50000, '2021-01-15')")
    cursor.execute("INSERT OR IGNORE INTO Employees VALUES (2, 'Bob', 'Engineering', 70000, '2020-06-10')")
    cursor.execute("INSERT OR IGNORE INTO Employees VALUES (3, 'Charlie', 'Marketing', 60000, '2022-03-20')")

    cursor.execute("INSERT OR IGNORE INTO Departments VALUES (1, 'Sales', 'Alice')")
    cursor.execute("INSERT OR IGNORE INTO Departments VALUES (2, 'Engineering', 'Bob')")
    cursor.execute("INSERT OR IGNORE INTO Departments VALUES (3, 'Marketing', 'Charlie')")

    conn.commit()
    conn.close()

# Query handler
def handle_query(query):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if "employees in the" in query.lower():
            department = query.split("in the ")[-1].replace(" department", "").strip()
            cursor.execute("SELECT * FROM Employees WHERE Department = ?", (department,))
            employees = cursor.fetchall()
            return [{'ID': emp['ID'], 'Name': emp['Name'], 'Department': emp['Department'], 'Salary': emp['Salary'], 'Hire_Date': emp['Hire_Date']} for emp in employees] or "No employees found in the specified department."

        elif "manager of the" in query.lower():
            department = query.split("of the ")[-1].replace(" department", "").strip()
            cursor.execute("SELECT Manager FROM Departments WHERE Name = ?", (department,))
            manager = cursor.fetchone()
            return f"The manager of the {department} department is {manager['Manager']}." if manager else "Department not found."

        elif "hired after" in query.lower():
            date = query.split("after ")[-1].strip()
            cursor.execute("SELECT * FROM Employees WHERE Hire_Date > ?", (date,))
            employees = cursor.fetchall()
            return [{'ID': emp['ID'], 'Name': emp['Name'], 'Department': emp['Department'], 'Salary': emp['Salary'], 'Hire_Date': emp['Hire_Date']} for emp in employees] or "No employees hired after the specified date."

        elif "total salary expense for the" in query.lower():
            department = query.split("for the ")[-1].replace(" department", "").strip()
            cursor.execute("SELECT SUM(Salary) as TotalSalary FROM Employees WHERE Department = ?", (department,))
            total_salary = cursor.fetchone()
            return f"The total salary expense for the {department} department is ${total_salary['TotalSalary']}." if total_salary and total_salary['TotalSalary'] else "Department not found or no salary data available."

        else:
            return "Sorry, I didn't understand your query. Please try again with a supported query."

    except Exception as e:
        return f"An error occurred: {str(e)}"

    finally:
        conn.close()

# Home route
@app.route('/')
def index():
    return render_template('index.html')  # Optional: Create index.html if needed

# API route
@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    response = handle_query(user_query)
    return jsonify({"response": response})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)