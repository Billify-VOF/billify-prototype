from decimal import Decimal
from datetime import date
from typing import Optional
from domain.models.value_objects import InvoiceStatus


class YukiInvoice:
    """ Domain model representing a Yuki invoice. """

    def __init__(
            self,
            invoice_number: str,
            invoice_type: str,  # 'purchase' or 'sales'
            issue_date: date,
            due_date: date,
            total_amount: Decimal,
            payment_status: InvoiceStatus,
            yuki_invoice_id: str,
            invoice_id: Optional[int] = None
    ):
        self.id = invoice_id
        self.invoice_number = invoice_number
        self.invoice_type = invoice_type
        self.issue_date = issue_date
        self.due_date = due_date
        self.total_amount = total_amount
        self.payment_status = payment_status
        self.yuki_invoice_id = yuki_invoice_id
        self.validate()

    def validate(self) -> None:
        """ Validate invoice attributes. """
        if self.total_amount <= 0:
            raise ValueError("Invoice amount must be positive")

    def mark_as_paid(self) -> None:
        """ Mark the invoice as paid. """
        self.payment_status = InvoiceStatus.PAID
