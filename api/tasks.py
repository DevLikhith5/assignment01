import os
import openpyxl
from celery import shared_task
from django.conf import settings
from .models import Customer, Loan

@shared_task
def ingest_customer_data():
    file_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
    if not os.path.exists(file_path):
        return

    Customer.objects.all().delete()
    
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    
    customers = []
    for row in list(sheet.rows)[1:]:
        customer_id = row[0].value
        if not customer_id:
            continue
            
        customers.append(Customer(
            customer_id=customer_id,
            first_name=row[1].value,
            last_name=row[2].value,
            age=row[3].value,
            phone_number=row[4].value,
            monthly_salary=row[5].value,
            approved_limit=row[6].value,
            current_debt=0
        ))
    
    Customer.objects.bulk_create(customers, batch_size=1000)

@shared_task
def ingest_loan_data():
    file_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
    if not os.path.exists(file_path):
        return

    Loan.objects.all().delete()
    
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    
    loans = []
    seen_loan_ids = set()
    for row in list(sheet.rows)[1:]:
        customer_id = row[0].value
        loan_id = row[1].value
        if not loan_id or not customer_id or loan_id in seen_loan_ids:
            continue
            
        seen_loan_ids.add(loan_id)
        
        loans.append(Loan(
            loan_id=loan_id,
            customer_id=customer_id,
            loan_amount=row[2].value,
            tenure=row[3].value,
            interest_rate=row[4].value,
            monthly_repayment=row[5].value,
            emis_paid_on_time=row[6].value,
            start_date=row[7].value,
            end_date=row[8].value,
            approved=True
        ))
    
    Loan.objects.bulk_create(loans, batch_size=1000)
