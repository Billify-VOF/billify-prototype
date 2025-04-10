import threading
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from django.conf import settings

from zeep import Client, Settings
from zeep.transports import Transport
import requests


from config.settings.base import YUKI_AUTHENTICATION_URL, YUKI_API_KEY, YUKI_ADMIN_ID

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SingletonMeta(type):
    """A thread-safe singleton metaclass."""

    _instances: Dict = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                logger.debug(f"Creating a new instance of {cls.__name__}")
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class YukiClient(metaclass=SingletonMeta):
    """
    YukiClient handles all interactions with the Yuki SOAP API.
    """

    _wsdl_url = YUKI_AUTHENTICATION_URL
    _api_key = YUKI_API_KEY

    _session_id: Optional[str] = None
    _session_expiry: Optional[datetime] = None

    @classmethod
    def _initialize_client(cls):
        """
        Initialize the Zeep client with the WSDL URL and API key from settings.
        """
        if not hasattr(cls, "_client"):
            session = requests.Session()
            settings = Settings(strict=False, xml_huge_tree=True)
            cls._client = Client(
                wsdl=cls._wsdl_url, transport=Transport(session=session, timeout=30), settings=settings
            )
            logger.info("YukiClient initialized")

    @classmethod
    def _is_session_valid(cls) -> bool:
        """
        Check if the current session is still valid (not expired).
        """
        return cls._session_id is not None and cls._session_expiry and datetime.utcnow() < cls._session_expiry

    @classmethod
    def _authenticate(cls):
        """
        Authenticate with Yuki API using API key to retrieve a session_id.
        """
        logger.debug("Authenticating with Yuki API...")
        try:
            cls._session_id = cls._client.service.Authenticate(cls._api_key)
            cls._session_expiry = datetime.utcnow() + timedelta(seconds=10)
            logger.info("Successfully authenticated with Yuki API.")
        except Exception as e:
            logger.exception("Failed to authenticate with Yuki API.")
            raise RuntimeError(f"Authentication failed: {e}")

    @classmethod
    def _ensure_session(cls):
        """
        Ensure the session is valid, else re-authenticate.
        """
        if not cls._is_session_valid():
            cls._authenticate()

    @classmethod
    def get_sales_invoices(cls, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve sales invoices from Yuki within a date range.
        """
        cls._initialize_client()
        cls._ensure_session()
        # try:
        #     result = cls._client.service.GetSalesInvoices(cls._session_id, YUKI_ADMIN_ID, start_date, end_date)
        #     logger.debug(f"Fetched sales invoices: {result}")
        #     return result or []
        # except Exception as e:
        #     logger.exception("Error fetching sales invoices.")
        #     raise RuntimeError(f"Failed to fetch sales invoices: {e}")

    @classmethod
    def get_purchase_invoices(cls, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve purchase invoices from Yuki within a date range.
        """
        cls._initialize_client()
        cls._ensure_session()
        try:
            result = cls._client.service.GetPurchaseInvoices(
                cls._session_id, YUKI_ADMIN_ID, start_date, end_date
            )
            logger.debug(f"Fetched purchase invoices: {result}")
            return result or []
        except Exception as e:
            logger.exception("Error fetching purchase invoices.")
            raise RuntimeError(f"Failed to fetch purchase invoices: {e}")

    @classmethod
    def upload_invoice(cls, document_bytes: bytes, file_name: str, description: str = "") -> str:
        """
        Upload a new invoice document to Yuki.
        """
        cls._initialize_client()
        cls._ensure_session()
        try:
            result = cls._client.service.UploadInvoice(
                cls._session_id, YUKI_ADMIN_ID, document_bytes, file_name, description
            )
            logger.info(f"Uploaded invoice, received result: {result}")
            return result
        except Exception as e:
            logger.exception("Error uploading invoice.")
            raise RuntimeError(f"Failed to upload invoice: {e}")


# from zeep import Client, Settings
# from zeep.transports import Transport
# from requests import Session
# from typing import Optional
# import time

# from config.settings.base import (
# YUKI_AUTHENTICATION_URL,
# YUKI_API_KEY,
# )

# class YukiClient:
#     SESSION_EXPIRY = 24 * 60 * 60  # 24 hours
#     _instance = None  # Class variable to hold the instance

#     def __new__(cls, *args, **kwargs):
#         """
#         Ensure only one instance of YukiClient is created.
#         """
#         if not cls._instance:
#             cls._instance = super(YukiClient, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if hasattr(self, 'initialized') and self.initialized:  # Prevent reinitialization
#             return
#         self.initialized = True

#         # Load values from environment variables (can be set in .env file)
#         self.wsdl_url = YUKI_AUTHENTICATION_URL
#         self.api_key = YUKI_API_KEY

#         if not self.wsdl_url or not self.api_key:
#             raise ValueError("Missing Yuki WSDL URL or API Key in environment variables.")

#         self._session_id: Optional[str] = None
#         self._session_created_at: Optional[float] = None

#         settings = Settings(strict=False, xml_huge_tree=True)
#         transport = Transport(session=Session())
#         self.client = Client(wsdl=self.wsdl_url, transport=transport, settings=settings)

#     def _authenticate(self):
#         """
#         Call Yuki's AuthenticateByAPIKey method to get a session ID.
#         """
#         session_id = self.client.service.Authenticate( self.api_key )

#         self._session_id = session_id
#         self._session_created_at = time.time()

#     def _get_session_id(self) -> str:
#         """
#         Return valid session ID, refreshing it if needed.
#         """
#         if (
#             self._session_id is None or
#             self._session_created_at is None or
#             (time.time() - self._session_created_at) >= self.SESSION_EXPIRY
#         ):
#             self._authenticate()
#         return self._session_id

#     def get_sales_invoices(self):
#         session_id = self._get_session_id()
#         return self.client.service.GetSalesInvoices(session_id)

#     def get_purchase_invoices(self):
#         pass

#     def upload_invoice(self, invoice_data):
#         pass
