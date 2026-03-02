from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from datetime import datetime
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import Customer, Loan
from .serializers import (
    RegisterSerializer,
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    CreateLoanResponseSerializer,
    LoanDetailSerializer,
    CustomerLoanSerializer,
)
from .utils import check_credit_score_and_eligibility, calculate_emi


class RegisterView(APIView):
    @extend_schema(
        summary="Register a new customer",
        description="Registers a new customer and returns their auto-calculated approved credit limit.",
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckEligibilityView(APIView):
    @extend_schema(
        summary="Check loan eligibility",
        description="Calculates credit score based on historical data and checks if a new loan can be approved. Returns the corrected interest rate if applicable.",
        request=LoanEligibilityRequestSerializer,
        responses={200: LoanEligibilityResponseSerializer},
    )
    def post(self, request):
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        customer = get_object_or_404(Customer, pk=data['customer_id'])
        
        score, is_approved, corrected_rate = check_credit_score_and_eligibility(
            customer, 
            data['loan_amount'], 
            data['interest_rate'], 
            data['tenure']
        )
        
        emi = 0
        if is_approved:
            emi = calculate_emi(data['loan_amount'], corrected_rate, data['tenure'])
            
        response_data = {
            "customer_id": customer.customer_id,
            "approval": is_approved,
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": corrected_rate,
            "tenure": data['tenure'],
            "monthly_installment": emi
        }
        res_serializer = LoanEligibilityResponseSerializer(response_data)
        return Response(res_serializer.data, status=status.HTTP_200_OK)


class CreateLoanView(APIView):
    @extend_schema(
        summary="Create a new loan",
        description="Processes a new loan request based on eligibility. If approved, creates a new Loan record in the database.",
        request=LoanEligibilityRequestSerializer,
        responses={200: CreateLoanResponseSerializer},
    )
    def post(self, request):
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        customer = get_object_or_404(Customer, pk=data['customer_id'])
        
        score, is_approved, corrected_rate = check_credit_score_and_eligibility(
            customer, 
            data['loan_amount'], 
            data['interest_rate'], 
            data['tenure']
        )
        
        loan_id = None
        message = "Loan not approved"
        emi = 0
        
        if is_approved:
            emi = calculate_emi(data['loan_amount'], corrected_rate, data['tenure'])
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data['loan_amount'],
                tenure=data['tenure'],
                interest_rate=corrected_rate,
                monthly_repayment=emi,
                start_date=datetime.now().date(),
                approved=True
            )
            loan_id = loan.loan_id
            message = "Loan approved"
            
        response_data = {
            "loan_id": loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": is_approved,
            "message": message,
            "monthly_installment": emi
        }
        res_serializer = CreateLoanResponseSerializer(response_data)
        return Response(res_serializer.data, status=status.HTTP_200_OK)


class ViewLoanView(APIView):
    @extend_schema(
        summary="View specific loan details",
        description="Fetches details of a specific loan along with nested customer information.",
        responses={200: LoanDetailSerializer},
    )
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, pk=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewLoansView(APIView):
    @extend_schema(
        summary="View all loans for a customer",
        description="Returns a list of all active/approved loans belonging to a specific customer.",
        responses={200: CustomerLoanSerializer(many=True)},
    )
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id)
        loans = customer.loans.filter(approved=True)
        serializer = CustomerLoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
