# Goals and non-goals

## Goals

### 1. Easy to use and understand
* **Requirement:** Design an intuitive user experience with minimal technical jargon and straightforward workflows that don't require accounting expertise.
* **Impact:** Allows users without an accounting or finance background to use and understand the application.

### 2. Visually communicative and appealing
* **Requirement:** Implement a clean, modern interface with consistent colour coding (red for urgent payments, orange for upcoming, green for paid/safe), clear data visualisations, and interactive charts that present financial information in an easily digestible format.
* **Impact:** It enables users to grasp their financial situation at a glance, reducing time spent analysing data and improving decision-making through better data comprehension.

### 3. Real-time cash flow dashboard
* **Requirement:** Present a clear, real-time overview of the current cash flow position in a dashboard with visual representations of what is coming in and going out.
* **Impact:** Allows users to make better financial decisions by easily staying on top of their cash flow position and monitoring incoming and outgoing transactions.

### 4. Simple financial software integration
* **Requirement:** Ensure easy-to-use integration between Billify and the users' other financial software to synchronise data across systems.
* **Impact:** This allows users to trust that their Billify data is correct and up-to-date. They do not have to worry about their financial data being fragmented across multiple systems that are not in sync.

### 5. Manual upload of invoices and other financial data
* **Requirement:** Implement capabilities for users to upload invoices (photos or PDFs) and other financial data (spreadsheets). Use OCR to identify amounts, due dates, and status.
* **Impact:** It simplifies invoice management, reduces manual data entry, and allows users to include custom data not present or available through the linked and integrated systems.

### 6. A centralised platform containing all of the users' financial data
* **Requirement:** Create a unified database that aggregates and synchronizes financial data from multiple sources, including bank accounts, accounting software (Yuki, Billit, Exact, Silverfin), manually uploaded invoices, and spreadsheets. Maintain real-time data consistency across all integrated systems.
* **Impact:** Eliminates the need for users to switch between multiple systems, reduces errors from manual data transfer, and provides a single source of truth for all financial information.

### 7. Unified platform combining cash flow insights and invoice management
* **Requirement:** Develop an integration between invoice processing and cash flow analysis, automatically updating cash flow projections when new invoices are added or paid and providing contextual insights based on invoice patterns and payment history.
* **Impact:** Provides users with a comprehensive view of their financial position, enabling them to make informed decisions about invoice payment timing and cash flow management while reducing the time spent on financial administration.

### 8. Predictive cash flow analysis
* **Requirement:** Include analytic forecasts that predict future cash positions and provide recommendations for optimal payment and savings timing.
* **Impact:** Enables easier financial planning and strategic decision-making.

### 9. Payment notifications
* **Requirement:** Implement automatic alerts for upcoming payment deadlines for the user and the users' clients.
* **Impact:** Helps the user and their clients avoid missed deadlines, potentially preventing penalties and missed payments.

## Non-goals

1. **Complete financial accounting software**
   * Billify does not aim to replace comprehensive accounting software but will focus on simplified cash flow management and integration with existing systems.

2. **Performance optimisation**
   * Super fast performance and stability are not priorities in the development of the Billify MVP. Instead, the focus is on developing the most fundamental functionality that shows Billify's unique value proposition.

3. **Many different integrations**
   * The MVP does not aim to have many different integrations with external software systems. Each integration requires dedicated development and maintenance time, increases the system's complexity, and increases the risk of failure because of external dependencies.

4. **Advanced financial reporting**
   * Billify does not aim to provide comprehensive financial reports, such as profit and loss statements or balance sheets. Instead, it focuses on simplifying insights related to cash flow and invoice tracking without extensive financial statement generation.

5. **Tax preparation and filing**
   * The application is not intended to handle complex tax preparation or filing. While Billify can show VAT summaries and help track tax-related cash flow elements, users should rely on dedicated accounting software for complete tax compliance.

6. **Custom financial modelling**
   * Billify will not include advanced custom financial modelling capabilities (e.g., creating custom predictive financial models or detailed scenario analysis). The MVP will provide basic predictive cash flow forecasts using built-in algorithms to keep the platform accessible and easy to use.

7. **Detailed budgeting and expense tracking**
   * The focus will not be on offering detailed budgeting tools or granular expense tracking. While Billify will display general cash inflow and outflow data, users needing comprehensive budget management should use specialized tools for detailed budget breakdowns.

8. **Complex VAT management**
   * While Billify will show basic VAT amounts due, it will not handle complex VAT scenarios, multiple VAT rates, or international VAT compliance. Users should rely on their primary accounting software for detailed VAT management and reporting.

9. **Advanced AI-driven analytics**
   * Billify will include basic predictive analysis for cash flow, but it will not focus on developing sophisticated AI models or complex machine learning features for the MVP. The initial forecasting will use simple, reliable statistical models rather than advanced AI algorithms.

10. **Custom invoice generation**
    * Billify will focus on invoice management and tracking rather than invoice creation. The system will not include features for generating new invoices or creating invoice templates, as existing accounting software already serves these functions well.