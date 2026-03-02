import os
import openpyxl

customer_file = 'customer_data.xlsx'
loan_file = 'loan_data.xlsx'

if os.path.exists(customer_file):
    wb = openpyxl.load_workbook(customer_file)
    sheet = wb.active
    headers = [cell.value for cell in list(sheet.rows)[0]]
    print(f"Customer Headers: {headers}")

if os.path.exists(loan_file):
    wb = openpyxl.load_workbook(loan_file)
    sheet = wb.active
    headers = [cell.value for cell in list(sheet.rows)[0]]
    print(f"Loan Headers: {headers}")
