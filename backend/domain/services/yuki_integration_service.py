from domain.repositories.interfaces.yuki_invoice_repository import YukiInvoiceRepository
from integrations.providers.yuki import YukiClient
from domain.models.yuki_invoice import YukiInvoice


class YukiIntegrationService:
    """ Service to handle Yuki invoice integration. """

    def __init__(self, invoice_repository: YukiInvoiceRepository, yuki_client: YukiClient):
        self.invoice_repository = invoice_repository
        self.yuki_client = yuki_client

    def sync_yuki_invoices(self):
        """ Fetch invoices from Yuki API and store them in the database. """
        invoices = self.yuki_client.fetch_all_invoices()
        for invoice_data in invoices:
            invoice = YukiInvoice(
                invoice_number=invoice_data["id"],
                invoice_type="sales" if invoice_data["type_description"] == "Sales invoice" else "purchase",
                issue_date=invoice_data["document_date"],
                due_date=invoice_data["document_date"],  # No due date in response, so keeping same as issue date
                total_amount=float(invoice_data["amount"]),
                payment_status="PAID",  # Placeholder, adjust based on actual status
                yuki_invoice_id=invoice_data["id"]
            )
            self.invoice_repository.save(invoice)
