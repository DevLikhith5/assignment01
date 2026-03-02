from django.core.management.base import BaseCommand
from api.tasks import ingest_customer_data, ingest_loan_data

class Command(BaseCommand):
    help = 'Ingests customer and loan data from Excel files'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data ingestion...")
        
        # Run synchronously to ensure completion
        self.stdout.write("Ingesting customers...")
        ingest_customer_data()
        
        self.stdout.write("Ingesting loans...")
        ingest_loan_data()
        
        self.stdout.write("Resetting PostgreSQL sequences...")
        from django.core.management import call_command
        from django.db import connection
        
        from io import StringIO
        out = StringIO()
        call_command('sqlsequencereset', 'api', stdout=out, no_color=True)
        sql = out.getvalue()
        
        if sql:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        
        self.stdout.write(self.style.SUCCESS("Data ingestion and sequence reset completed successfully!"))
