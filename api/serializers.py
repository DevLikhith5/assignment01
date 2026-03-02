from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Customer, Loan

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid Registration',
            summary='Example registration request',
            description='Registers a new customer and auto-calculates approved_limit',
            value={
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "monthly_income": 50000,
                "phone_number": 9876543210
            },
            request_only=True
        )
    ]
)
class RegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary')
    name = serializers.SerializerMethodField()
    customer_id = serializers.IntegerField(read_only=True)
    approved_limit = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'phone_number', 'name', 'approved_limit']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        monthly_salary = validated_data.get('monthly_salary')
        # approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        limit = round((36 * monthly_salary) / 100000) * 100000
        validated_data['approved_limit'] = limit
        return super().create(validated_data)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Check Loan Eligibility',
            summary='Example eligibility check request',
            value={
                "customer_id": 301,
                "loan_amount": 50000,
                "interest_rate": 10.5,
                "tenure": 12
            },
            request_only=True
        )
    ]
)
class LoanEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()


class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.FloatField()


class CustomerBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']


class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerBasicSerializer()

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure']


class CustomerLoanSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'repayments_left']

    def get_repayments_left(self, obj):
        # Difference between tenure and paid EMIs
        return max(0, obj.tenure - obj.emis_paid_on_time)
