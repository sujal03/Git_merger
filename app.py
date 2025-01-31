from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Helper functions for calculations
def calculate_max_loan(income, debts, interest_rate, tenure_years):
    # Apply TDSR (Total Debt Servicing Ratio - 55%)
    max_monthly_repayment = income * 0.55 - debts

    # Monthly interest rate and number of payments
    monthly_interest_rate = interest_rate / 12 / 100
    num_payments = tenure_years * 12

    # Loan calculation formula: P = [r * (1 + r)^n] / [(1 + r)^n - 1]
    if monthly_interest_rate > 0:
        max_loan = (
            max_monthly_repayment
            * (1 - (1 + monthly_interest_rate) ** -num_payments)
            / monthly_interest_rate
        )
    else:
        max_loan = max_monthly_repayment * num_payments

    return max(0, max_loan)

def calculate_property_price(max_loan, ltv_ratio, cpf, cash):
    # Total funds available
    total_funds = cpf + cash
    # Property price = Loan / LTV Ratio + Funds
    max_property_price = max_loan / ltv_ratio + total_funds
    return max_property_price

# Routes
@app.route("/")
def index():
    return render_template("calculator.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json

    # Inputs
    income = float(data.get("income", 0))
    variable_income = float(data.get("variable_income", 0)) * 0.7  # 30% haircut
    total_income = income + variable_income

    debts = (
        float(data.get("credit_card_debt", 0))
        + float(data.get("car_loans", 0))
        + float(data.get("home_loans", 0))
        + float(data.get("other_loans", 0))
    )

    cpf = float(data.get("cpf", 0))
    cash = float(data.get("cash", 0))

    interest_rate = float(data.get("interest_rate", 4))
    tenure_years = int(data.get("tenure_years", 30))
    ltv_ratio = 0.75  # Default LTV ratio

    # Calculate maximum loan and property price
    max_loan = calculate_max_loan(total_income, debts, interest_rate, tenure_years)
    max_property_price = calculate_property_price(max_loan, ltv_ratio, cpf, cash)

    response = {
        "max_loan": round(max_loan, 2),
        "max_property_price": round(max_property_price, 2),
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
