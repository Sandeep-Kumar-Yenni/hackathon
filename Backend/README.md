# Vendor Onboarding API

This FastAPI service captures the four vendor onboarding sections described in the problem statement: business details, contact details, banking & payment, and compliance & certifications. Each vendor record stores all required form sections via one-to-one relationships, enabling straightforward CRUD access to every onboarding field.

## Setup

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
2. Set `SQLALCHEMY_DATABASE_URL` (defaults to the SQL Server host + credentials) before launching; e.g.
   ```bash
   set SQLALCHEMY_DATABASE_URL="mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+18+for+SQL+Server%7D%3BSERVER%3Devokehackathonsqlserver.database.windows.net%2C1433%3BDATABASE%3DNeoCodeNexusDB%3BUID%3Duser%3BPWD%3Dpass%3BEncrypt%3Dyes%3BTrustServerCertificate%3Dno%3BConnection+Timeout%3D30%3B"
   ```
   The application expects this env var to be defined for SQL Server access.

   Alternatively, you can leave `SQLALCHEMY_DATABASE_URL` unset and override individual elements via:
   ```bash
   set SQLSERVER_USERNAME=NeoCodeNexusSQLUser
   set SQLSERVER_PASSWORD=securePass
   set SQLSERVER_HOST=evokehackathonsqlserver.database.windows.net
   set SQLSERVER_DATABASE=NeoCodeNexusDB
   set SQLSERVER_PORT=1433
   set SQLSERVER_ODBC_DRIVER="ODBC Driver 18 for SQL Server"
   ```

3. When using the Groq-based PDF extractor, export `GROQ_API_KEY` (and optionally `GROQ_MODEL`) before running.


## Running

Launch the API locally with uvicorn:
```bash
uvicorn app.main:app --reload
```
The interactive docs are available at `http://127.0.0.1:8000/docs`.

## API Surface

- `GET /vendors` – list all vendors with nested onboarding sections.
- `POST /vendors` – publish a new vendor onboarding record. Requires nested payloads for every form section and validates registration numbers, emails, IBANs, and expiry dates.
- `POST /vendor-onboarding/business-details/extract` – upload a business-details PDF and return extracted fields (legal name, registration number, business type, year, address, industry, employees).
- `POST /vendor-onboarding/business-details/extract-llm` – send the business-details PDF to Groq via `langchain-groq` and return the parsed JSON payload (requires `GROQ_API_KEY`).
- `/business-details`, `/contact-details`, `/banking-details`, `/compliance-details` – standalone CRUD for each onboarding section.
- `/followups/draft` – supply `vendor_name`, `issue_type`, missing items, and tone to get an LLM-generated subject/body/signature for polite follow-up outreach (requires `GROQ_API_KEY`).
- `/followup-records` – CRUD the follow-up table that tracks issue types, statuses, and templates per vendor (supports filtering by `vendor_id` and soft deletes).
- `/vendors/comprehensive` – returns every vendor with their onboarding status and linked follow-up history so procurement sees requested/validated/denied/deleted states.
- `python -m pytest --cov=app tests` – run the backend unit tests and view coverage after installing pytest-related dependencies.
- `GET /vendors/{vendor_id}` – retrieve a single vendor’s full onboarding record.
- `PUT /vendors/{vendor_id}` – update any portion of a vendor, including nested section updates.
- `DELETE /vendors/{vendor_id}` – remove a vendor and all related sections via cascade.

## Schema Overview

- **Vendor**: global supplier metadata (name, email, contact, category, remarks).
- **BusinessDetail**: legal identifiers, address, industry, and uploaded business proof.
- **ContactDetail**: primary/secondary contacts, emails, phone, website, and contact proof.
- **BankingDetail**: bank info, account details, payment terms, currency, and banking proof.
- **ComplianceDetail**: tax/license/insurance details plus certifications and documented proof.

All models are defined under `app/models`, Pydantic validation lives in `app/schemas`, and routing logic sits in `app/routes`.

## Development Notes

- The database URL defaults to the SQL Server host from the problem statement. Provide actual credentials/corpus via `SQLALCHEMY_DATABASE_URL`.
- Validators enforce conformity to the problem statement (e.g., year range, future expiry dates, account number length).
- The API returns nested responses for every vendor so the full onboarding package can be rendered in a single call.

