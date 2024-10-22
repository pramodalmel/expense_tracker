from flask import Flask, render_template, request, session
import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# File to store expenses permanently
EXPENSES_FILE = 'expenses.json'

# Function to load expenses from the file
def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, 'r') as file:
            return json.load(file)
    return {}

# Function to save expenses to the file
def save_expenses(expenses):
    with open(EXPENSES_FILE, 'w') as file:
        json.dump(expenses, file)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Load all expenses from file for permanence
    all_expenses = load_expenses()
    total = None
    error = None

    # Initialize session-based temporary display list
    if 'session_expenses' not in session:
        session['session_expenses'] = []

    if request.method == 'POST':
        if 'date' in request.form:
            # Adding an expense
            date_str = request.form['date']
            description = request.form['description']
            amount = request.form['amount']

            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                amount = float(amount)
                date_str = str(date)  # Convert date to string for JSON compatibility

                # Add expense to file storage
                if date_str not in all_expenses:
                    all_expenses[date_str] = []
                all_expenses[date_str].append({'description': description, 'amount': amount})
                save_expenses(all_expenses)

                # Add to session expenses for immediate display
                session['session_expenses'].append({'date': date_str, 'description': description, 'amount': amount})
            except ValueError:
                error = "Invalid date or amount format."
            except Exception as e:
                error = f"An error occurred while adding the expense: {e}"

        elif 'date_total' in request.form:
            # Calculate total for a specific date
            date_str = request.form['date_total']
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                total = sum(expense['amount'] for expense in all_expenses.get(str(date), []))
            except ValueError:
                error = "Invalid date format."
            except Exception as e:
                error = f"An error occurred while calculating the total: {e}"

    # Render the template, passing the current session expenses, total, and error message
    return render_template('index.html', 
                           expenses=session.get('session_expenses', []), 
                           total=total, 
                           error=error)

@app.before_request
def clear_session_expenses_on_refresh():
    # Clear session expenses on refresh
    session.pop('session_expenses', None)

if __name__ == "__main__":
    app.run(debug=True)
