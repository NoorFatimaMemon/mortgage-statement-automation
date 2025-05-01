# Mortgage Statement Automation

This script automates the retrieval of the most recent mortgage statement from a specified servicing website and uploads it to a designated Google Drive folder.

## Workflow Overview
1. Log in to the mortgage servicing portal.
2. Handle 2FA via a messaging platform.
3. Locate the most recent statement for a specified account.
4. Download the statement as a PDF.
5. Rename the file using the format: `StatementDate - LenderName - AccountNumber.pdf`.
6. Upload the file to a shared Google Drive folder.

## Authentication
- Credentials and phone numbers are required for the servicing website and the messaging service.
- The following sensitive variables are required:
  - `MORTGAGE_USERNAME`
  - `MORTGAGE_PASSWORD`
  - `2FA_PHONE_NUMBER`
  - `MESSAGING_USERNAME`
  - `MESSAGING_PASSWORD`
  - `GOOGLE_DRIVE_FOLDER_URL`
  - `ACCOUNT_NUMBER`
