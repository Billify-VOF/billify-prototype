from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models.yuki_invoice import YukiInvoice


class YukiInvoiceRepository(ABC):
    """ Abstract repository interface for Yuki invoices. """

    @abstractmethod
    def save(self, invoice: YukiInvoice) -> YukiInvoice:
        """ Save a Yuki invoice to the database. """
        pass

    @abstractmethod
    def get_by_yuki_id(self, yuki_id: str) -> Optional[YukiInvoice]:
        """ Get invoice by Yuki ID. """
        pass

    @abstractmethod
    def list_all(self) -> List[YukiInvoice]:
        """ Retrieve all Yuki invoices. """
        pass
