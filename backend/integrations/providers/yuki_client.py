from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from typing import Optional
import time


class YukiClient:
    SESSION_EXPIRY_SECONDS = 24 * 60 * 60  # 24 hours

    def __init__(self, wsdl_url: str, username: str, password: str):
        self.wsdl_url = wsdl_url
        self.username = username
        self.password = password
        self._session_id: Optional[str] = None
        self._session_created_at: Optional[float] = None

        settings = Settings(strict=False, xml_huge_tree=True)
        transport = Transport(session=Session())
        self.client = Client(wsdl=wsdl_url, transport=transport, settings=settings)

    def _authenticate(self):
        """
        Call Yuki's AuthenticateByUsername method to get a session ID.
        """
        session_id = self.client.service.AuthenticateByUsername(self.username, self.password)
        self._session_id = session_id
        self._session_created_at = time.time()

    def _get_session_id(self) -> str:
        """
        Return valid session ID, refreshing it if needed.
        """
        if (
            self._session_id is None or
            self._session_created_at is None or
            (time.time() - self._session_created_at) >= self.SESSION_EXPIRY_SECONDS
        ):
            self._authenticate()
        return self._session_id

    def get_sales_invoices(self):
        session_id = self._get_session_id()
        return self.client.service.GetSalesInvoices(session_id)

    def get_purchase_invoices(self):
        pass

    def upload_invoice(self, invoice_data):
        pass
