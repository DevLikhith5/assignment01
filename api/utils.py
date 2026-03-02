from datetime import datetime
from .models import Loan

def calculate_emi(principal, annual_interest_rate, tenure_months):
    """Calculate EMI using compound interest formula."""
    if annual_interest_rate == 0:
        return principal / tenure_months
        
    monthly_rate = (annual_interest_rate / 100) / 12
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1
    return round(numerator / denominator, 2)

def check_credit_score_and_eligibility(customer, requested_amount, requested_interest_rate, requested_tenure):
    """Check loan eligibility and return (credit_score, is_approved, corrected_interest_rate)."""
    loans = customer.loans.all()
    current_year = datetime.now().year
    
    total_emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    total_emis_expected = sum(loan.tenure for loan in loans if loan.end_date and loan.end_date.year <= current_year) 
    
    if len(loans) == 0:
        score_component_1 = 30
    else:
        total_tenure = sum(loan.tenure for loan in loans)
        score_component_1 = (total_emis_paid_on_time / total_tenure) * 30 if total_tenure > 0 else 0
        
    num_loans = len(loans)
    if num_loans >= 8:
        score_component_2 = 0
    elif num_loans == 0:
        score_component_2 = 20
    else:
        score_component_2 = 20 - (num_loans * 2.5)
        
    current_year_loans = sum(1 for loan in loans if loan.start_date and loan.start_date.year == current_year)
    if current_year_loans >= 5:
        score_component_3 = 0
    else:
        score_component_3 = 20 - (current_year_loans * 4)
        
    total_approved_volume = sum(loan.loan_amount for loan in loans if loan.approved)
    limit = customer.approved_limit
    if limit > 0:
        volume_ratio = total_approved_volume / limit
        score_component_4 = max(0, 30 - (volume_ratio * 30))
    else:
        score_component_4 = 0 if total_approved_volume > 0 else 30
        
    credit_score = score_component_1 + score_component_2 + score_component_3 + score_component_4
    
    current_active_loans = sum(loan.loan_amount for loan in loans if not loan.end_date or loan.end_date.year >= current_year)
    if current_active_loans > limit:
        credit_score = 0
        
    is_approved = False
    corrected_interest_rate = requested_interest_rate
    
    if credit_score > 50:
        is_approved = True
    elif 30 < credit_score <= 50:
        is_approved = True
        corrected_interest_rate = max(12.0, requested_interest_rate)
    elif 10 < credit_score <= 30:
        is_approved = True
        corrected_interest_rate = max(16.0, requested_interest_rate)
    else:
        is_approved = False
        
    current_total_emi = sum(loan.monthly_repayment for loan in loans if not loan.end_date or loan.end_date.year >= current_year)
    new_emi = calculate_emi(requested_amount, corrected_interest_rate, requested_tenure)
    if (current_total_emi + new_emi) > (0.5 * customer.monthly_salary):
        is_approved = False
        
    return credit_score, is_approved, corrected_interest_rate
