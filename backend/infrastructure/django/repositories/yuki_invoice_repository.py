from typing import Optional, List

from domain.repositories.interfaces.yuki_invoice_repository import YukiInvoiceRepository
from domain.models.yuki_invoice import YukiInvoice
from infrastructure.django.models.invoice import Invoice


class DjangoYukiInvoiceRepository(YukiInvoiceRepository):
    """ Repository implementation using Django ORM """

    def save(self, invoice: YukiInvoice) -> YukiInvoice:
        obj, created = Invoice.objects.update_or_create(
            yuki_invoice_id=invoice.yuki_invoice_id,
            defaults={
                "invoice_number": invoice.invoice_number,
                "invoice_type": invoice.invoice_type,
                "issue_date": invoice.issue_date,
                "due_date": invoice.due_date,
                "total_amount": invoice.total_amount,
                "payment_status": invoice.payment_status.value,
            },
        )
        return invoice

    def get_by_yuki_id(self, yuki_id: str) -> Optional[YukiInvoice]:
        obj = Invoice.objects.filter(yuki_invoice_id=yuki_id).first()
        if obj:
            return YukiInvoice(
                invoice_number=obj.invoice_number,
                invoice_type=obj.invoice_type,
                issue_date=obj.issue_date,
                due_date=obj.due_date,
                total_amount=obj.total_amount,
                payment_status=obj.payment_status,
                yuki_invoice_id=obj.yuki_invoice_id,
                invoice_id=obj.id,
            )
        return None

    def list_all(self) -> List[YukiInvoice]:
        return [
            self.get_by_yuki_id(obj.yuki_invoice_id)
            for obj in Invoice.objects.all()
        ]
