# Credit Approval System

A fully-featured REST API for an automated credit approval and loan management system built with Django REST Framework, PostgreSQL, Celery, and Docker.

## Tech Stack
- **Framework**: Django 6.0 + Django REST Framework
- **Database**: PostgreSQL 15
- **Message Broker**: Redis
- **Background Tasks**: Celery
- **Documentation**: OpenAPI (Swagger UI) via `drf-spectacular`
- **Environment**: Docker & Docker Compose

## Features
- **Data Ingestion**: Safely ingest Excel files containing historical customer and loan records via background workers. Idempotent and reliable.
- **REST APIs**:
  - `POST /api/register` - Create a new customer and auto-calculate their approved limit.
  - `POST /api/check-eligibility` - Calculate credit score dynamically and determine eligibility and interest rate slabs for a new loan.
  - `POST /api/create-loan` - Create and process new loans with EMI calculated using compound interest.
  - `GET /api/view-loan/<loan_id>` - Fetch comprehensive details regarding a single loan and its holder.
  - `GET /api/view-loans/<customer_id>` - Fetch all active loans held by a specific customer.
- **Credit Engine**: Multi-component credit scoring system factoring in past EMIs paid on time, history volume, active loans, and dynamic salary bounds.
- **Auto-Documentation**: Explore APIs visually using the built-in Swagger UI.

## Local Setup & Installation

### Requirements
- Docker
- Docker Compose

### Running the App

1. Ensure Docker daemon is running on your system.
2. In the root directory (where `docker-compose.yml` is located), simply execute:
```bash
docker compose up -d --build
```

**What this does automatically:**
- Builds the `web` container (Django).
- Pulls `postgres:15` and `redis:7-alpine`.
- Sets up the `celery_worker` container.
- **Startup Script**: The web container will automatically run database migrations and execute the custom `python manage.py ingest_data` script to parse the `customer_data.xlsx` and `loan_data.xlsx` files and populate your database safely. 

### Exploring the APIs

1. Wait a moment for all containers to fully start and ingest data (you can check with `docker compose logs web`).
2. Visit the OpenAPI Swagger UI portal and experiment with endpoints directly from the browser:
   * **Swagger Docs:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
   * *(Pre-filled example payloads are included in the documentation!)*

### Useful Commands

**View container logs:**
```bash
docker compose logs -f
```

**Access Django Shell:**
```bash
docker compose exec web python manage.py shell
```

**Restart Web Server:**
```bash
docker compose restart web
```

**Tear Down Environment:**
```bash
docker compose down -v
```

## Internal Credit Logic Reference

**Score out of 100 based on:**
1. **Past Loans Paid** (30 pts) — Derived from ratio of historically completed EMIs versus required tenures.
2. **History Volume** (20 pts) — Penalty for number of loans historically taken. Returns 0 if >= 8 loans.
3. **Current Year Activity** (20 pts) — Penalty for recently opened loans. Returns 0 if >= 5 loans.
4. **Loan Approved Volume** (30 pts) — Volume of previous approved loans mapped dynamically against the customer's safe limit bounds.

**Approval Rules**:
- Score > 50: Approved at requested rate.
- 50 >= Score > 30: Approved, rate forced to >= 12%.
- 30 >= Score > 10: Approved, rate forced to >= 16%.
- Score <= 10 or current EMIs exceed 50% salary: Automatically Rejected.
# assignment01
