# Functional requirements

## User management

### 1. User authentication
* Users must log in using a secure username and password to use Billify.

### 2. User logout
* Users should be able to log out securely from any session.

## Integration with external systems

### 1. Banking
* Users can connect and sync their bank accounts to automatically update transactions in the app.

### 2. Accounting
Users can connect and sync with the following accounting systems:
* Exact online
* Odoo accounting module
* Yuki by Visma
* Billit

### 3. Other third-party financial systems
Users can connect and sync with the following other systems:
* Silverfin
* TBD

## Invoice management

### 1. Upload invoices
* Users can upload invoices in PDF or image format, and OCR automatically extracts amounts, due dates, and statuses.

### 2. Upload spreadsheets
* Users can upload spreadsheets in XLSX, ODS, or CSV format, and Billify will automatically extract the relevant financial data.

### 3. Manual entry
* Users should have the option to enter invoice data manually.

### 4. Invoice tracking and updating
* Track changes in invoice status as payments are made, adjusting the cash flow balance accordingly.
* Mark invoices as "paid" and automatically remove them from the pending list.

### 5. Automatic invoice payment alerts
* Notify users of upcoming payments that are due to avoid late fees or missed payments.

### 6. Invoice categorisation
* Invoices should be automatically categorised by the due date (e.g., due within 7, 30 days) with corresponding colour codes (e.g., red for urgent, orange for near due, green for not soon owing).

## Cash flow

### 1. Real-time cash flow dashboard
* Display the user's current cash flow position in a dashboard based on all the data collected from external systems, uploaded invoices, and spreadsheets.
* The dashboard should show visual representations of funds coming in/going, VAT, and outstanding and upcoming invoices.
* Consult the wireframes for how the dashboard user interface should look like.

### 2. Predictive cash flow analysis
* Generate and show the user analytic forecasts that predict future cash position.
* Provide recommendations for optimal timing of payment and savings.
* Calculate and display burn rate and break-even point.