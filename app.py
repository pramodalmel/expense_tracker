from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
EXPENSES_FILE = 'expenses.json'

# Load all expenses from the file
def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save expenses to the file
def save_expenses(expenses):
    with open(EXPENSES_FILE, 'w') as file:
        json.dump(expenses, file)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Retrieve session-based expenses for this session only
    session_expenses = session.get('session_expenses', [])
    error = None
    total = None

    if request.method == 'POST':
        if 'date' in request.form:
            # Adding an expense
            date = request.form['date']
            description = request.form['description']
            amount = float(request.form['amount'])

            # Store only the last expense in the session
            session['session_expenses'] = [{'date': date, 'description': description, 'amount': amount}]

            # Save it to file for permanence
            expenses = load_expenses()
            if date not in expenses:
                expenses[date] = []
            expenses[date].append({'description': description, 'amount': amount})
            save_expenses(expenses)

        elif 'date_total' in request.form:
            # Calculate total for a specific date
            date = request.form['date_total']
            expenses = load_expenses()
            total = sum(exp['amount'] for exp in expenses.get(date, []))

    # Clear the session expenses upon page load (after adding)
    if request.method == 'GET':
        session.pop('session_expenses', None)  # Clear session expenses

    return render_template('index.html', expenses=session.get('session_expenses', []), total=total, error=error)

@app.route('/fetch_expenses_for_delete', methods=['POST'])
def fetch_expenses_for_delete():
    date = request.form['delete_date']
    expenses = load_expenses()
    delete_expenses = expenses.get(date, [])
    session['delete_expenses'] = delete_expenses  # Save fetched data in session
    return render_template('index.html', delete_expenses=delete_expenses, delete_date=date, expenses=session.get('session_expenses', []))

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    date = request.form['date']
    description = request.form['description']
    amount = float(request.form['amount'])

    # Load and delete from file storage
    expenses = load_expenses()
    if date in expenses:
        expenses[date] = [exp for exp in expenses[date] if not (exp['description'] == description and exp['amount'] == amount)]
        if not expenses[date]:  # Remove date if empty
            del expenses[date]
        save_expenses(expenses)

    # Clear delete session after the operation
    session.pop('delete_expenses', None)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
