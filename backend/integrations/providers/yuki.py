import requests
from typing import Dict, List
from xml.etree import ElementTree
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YukiClient:
    """
    Handles authentication and data retrieval from Yuki API.
    """
    BASE_URL = "https://api.yukiworks.be/ws/"
    SALES_SERVICE = "Sales.asmx"
    PURCHASE_SERVICE = "Purchase.asmx"
    ACCOUNTING_SERVICE = "Accounting.asmx"
    ADMINISTRATION_SERVICE = "Sales.asmx"
    DOCUMENT_SERVICE = "Archive.asmx"
    ARCHIVE_SERVICE = "Archive.asmx"  # Updated to Archive.asmx

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_id = None

    def authenticate(self) -> None:
        """Authenticates with Yuki API and retrieves a session ID."""
        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
        xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:Authenticate>
                 <they:accessKey>{self.api_key}</they:accessKey>
              </they:Authenticate>
           </soapenv:Body>
        </soapenv:Envelope>
        '''
        headers = {'Content-Type': 'text/xml'}  # No SOAPAction header
        response = requests.post(f"{self.BASE_URL}{self.SALES_SERVICE}", headers=headers, data=xml_payload)

        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            session_id_element = root.find(".//{http://www.theyukicompany.com/}AuthenticateResult")
            self.session_id = session_id_element.text if session_id_element is not None else None
            print("Authenticated successfully. Session ID:", self.session_id)
        else:
            raise Exception(f"Yuki API Authentication Failed: {response.text}")

    def fetch_administrations(self) -> List[Dict]:
        """Fetches administration names and IDs for the authenticated user."""
        if not self.session_id:
            self.authenticate()

        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:Administrations>
                 <they:sessionID>{self.session_id}</they:sessionID>
              </they:Administrations>
           </soapenv:Body>
        </soapenv:Envelope>
        '''

        headers = {'Content-Type': 'text/xml'}  # No SOAPAction header
        response = requests.post(f"{self.BASE_URL}{self.ADMINISTRATION_SERVICE}", headers=headers, data=xml_payload)
        if response.status_code == 200:
            return self._parse_administrations(response.content)
        return []

    def fetch_outstanding_creditor_items(self, administration_id: str) -> List[Dict]:
        """
        Fetches outstanding creditor items (e.g., unpaid purchase invoices) for a given administration ID.
        """
        if not self.session_id:
            self.authenticate()

        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:OutstandingCreditorItems>
                 <they:sessionID>{self.session_id}</they:sessionID>
                 <they:administrationID>{administration_id}</they:administrationID>
                 <they:includeBankTransactions>true</they:includeBankTransactions>
                 <they:sortOrder>DateAsc</they:sortOrder>
              </they:OutstandingCreditorItems>
           </soapenv:Body>
        </soapenv:Envelope>
        '''

        headers = {'Content-Type': 'text/xml'}  # No SOAPAction header
        response = requests.post(f"{self.BASE_URL}{self.ACCOUNTING_SERVICE}", headers=headers, data=xml_payload)
        if response.status_code == 200:
            return self._parse_outstanding_items(response.content, "OutstandingCreditorItems")
        return []

    def fetch_outstanding_debtor_items(self, administration_id: str) -> List[Dict]:
        """
        Fetches outstanding debtor items (e.g., unpaid sales invoices) for a given administration ID.
        """
        if not self.session_id:
            self.authenticate()

        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:OutstandingDebtorItems>
                 <they:sessionID>{self.session_id}</they:sessionID>
                 <they:administrationID>{administration_id}</they:administrationID>
                 <they:includeBankTransactions>true</they:includeBankTransactions>
                 <they:sortOrder>DateAsc</they:sortOrder>
              </they:OutstandingDebtorItems>
           </soapenv:Body>
        </soapenv:Envelope>
        '''

        headers = {'Content-Type': 'text/xml'}  # No SOAPAction header
        response = requests.post(f"{self.BASE_URL}{self.ACCOUNTING_SERVICE}", headers=headers, data=xml_payload)
        if response.status_code == 200:
            return self._parse_outstanding_items(response.content, "OutstandingDebtorItems")
        return []

    def _parse_administrations(self, xml_response: str) -> List[Dict]:
        """Parses XML response into a list of administrations."""
        administrations = []
        root = ElementTree.fromstring(xml_response)
        # Define the namespaces
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://www.theyukicompany.com/',
            'default': ''  # The empty namespace for the Administrations element
        }

        # Find the Administrations element
        administrations_result = root.find('.//soap:Body/ns:AdministrationsResponse/ns:AdministrationsResult',
                                           namespaces)

        if administrations_result is not None:
            # Find all Administration elements within the Administrations element
            for admin in administrations_result.findall('.//default:Administrations/default:Administration',
                                                        namespaces):
                administrations.append({
                    "id": admin.attrib.get("ID"),
                    "name": admin.find(f"default:Name", namespaces).text,
                })

        return administrations

    def _parse_outstanding_items(self, xml_response: str, item_type: str) -> List[Dict]:
        """
        Parses XML response into a list of outstanding items (creditor or debtor).
        """
        items = []
        root = ElementTree.fromstring(xml_response)
        # Define the namespaces
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://www.theyukicompany.com/',
            'default': ''  # The empty namespace for the Items element
        }

        # Find the Items element
        items_result = root.find(f'.//soap:Body/ns:{item_type}Response/ns:{item_type}Result', namespaces)

        if items_result is not None:
            # Find all Item elements within the Items element
            for item in items_result.findall(f'.//default:{item_type}/default:Item', namespaces):
                items.append({
                    "id": item.attrib.get("ID"),
                    "date": item.find("default:Date", namespaces).text,
                    "description": item.find("default:Description", namespaces).text,
                    "contact": item.find("default:Contact", namespaces).text,
                    "contact_id": item.find("default:ContactID", namespaces).text,
                    "open_amount": float(item.find("default:OpenAmount", namespaces).text),
                    "original_amount": float(item.find("default:OriginalAmount", namespaces).text),
                    "type": item.find("default:Type", namespaces).text,
                    "reference": item.find("default:Reference", namespaces).text,
                    "due_date": item.find("default:DueDate", namespaces).text,
                    "payment_method": item.find("default:PaymentMethod", namespaces).text,
                    "document_id": item.find("default:DocumentID", namespaces).text,
                })

        return items

    def fetch_documents(self, start_date: str, end_date: str, number_of_records: int = 10, start_record: int = 0) -> \
            List[Dict]:
        """
        Fetches documents (e.g., invoices) from the Yuki Archive API.
        :param start_date: The start date for the document search (format: YYYY-MM-DD).
        :param end_date: The end date for the document search (format: YYYY-MM-DD).
        :param number_of_records: The number of records to retrieve (default: 10).
        :param start_record: The starting record index (default: 0).
        :return: A list of documents with relevant details.
        """
        if not self.session_id:
            self.authenticate()

        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:Documents>
                 <they:sessionID>{self.session_id}</they:sessionID>
                 <they:sortOrder>CreatedAsc</they:sortOrder>
                 <they:startDate>{start_date}</they:startDate>
                 <they:endDate>{end_date}</they:endDate>
                 <they:numberOfRecords>{number_of_records}</they:numberOfRecords>
                 <they:startRecord>{start_record}</they:startRecord>
              </they:Documents>
           </soapenv:Body>
        </soapenv:Envelope>
        '''
        headers = {'Content-Type': 'text/xml'}  # No SOAPAction header
        logger.debug("Sending Documents request...")
        logger.debug("XML Payload: %s", xml_payload)
        response = requests.post(f"{self.BASE_URL}{self.ARCHIVE_SERVICE}", headers=headers, data=xml_payload)

        if response.status_code == 200:
            logger.debug("Documents response: %s", response.text)
            return self._parse_documents(response.content)
        else:
            logger.error("Failed to fetch documents. Status code: %s, Response: %s", response.status_code,
                         response.text)
            return []

    def _parse_documents(self, xml_response: str) -> List[Dict]:
        """
        Parses XML response into a list of documents.
        """
        documents = []
        root = ElementTree.fromstring(xml_response)
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://www.theyukicompany.com/',
            'default': ''  # The empty namespace for the Documents element
        }

        # Find the Documents element
        documents_result = root.find('.//soap:Body/ns:DocumentsResponse/ns:DocumentsResult', namespaces)

        if documents_result is not None:
            # Find all Document elements within the Documents element
            for doc in documents_result.findall('.//default:Documents/default:Document', namespaces):
                document_data = {
                    "id": doc.attrib.get("ID"),
                    "subject": doc.find("default:Subject", namespaces).text,
                    "document_date": doc.find("default:DocumentDate", namespaces).text,
                    "amount": float(doc.find("default:Amount", namespaces).text),
                    "folder": doc.find("default:Folder", namespaces).attrib.get("ID"),
                    "tab": doc.find("default:Tab", namespaces).attrib.get("ID"),
                    "type": doc.find("default:Type", namespaces).text,
                    "type_description": doc.find("default:TypeDescription", namespaces).text,
                    "file_name": doc.find("default:FileName", namespaces).text,
                    "content_type": doc.find("default:ContentType", namespaces).text,
                    "file_size": int(doc.find("default:FileSize", namespaces).text),
                    "contact_name": doc.find("default:ContactName", namespaces).text if doc.find("default:ContactName",
                                                                                                 namespaces) is not None else None,
                    "contact_id": doc.find("default:ContactId", namespaces).text if doc.find("default:ContactId",
                                                                                             namespaces) is not None else None,
                    "reference": doc.find("default:Reference", namespaces).text if doc.find("default:Reference",
                                                                                            namespaces) is not None else None,
                    "vat_amount": float(doc.find("default:VATAmount", namespaces).text) if doc.find("default:VATAmount",
                                                                                                    namespaces) is not None else None,
                    "created": doc.find("default:Created", namespaces).text,
                    "creator": doc.find("default:Creator", namespaces).text,
                    "modified": doc.find("default:Modified", namespaces).text,
                    "modifier": doc.find("default:Modifier", namespaces).text,
                }
                documents.append(document_data)

        print("total Documents:", len(documents))
        return documents

    def fetch_documents_by_type(self, document_type: int, start_date: str, end_date: str, number_of_records: int = 100,
                                start_record: int = 0) -> List[Dict]:
        """
        Fetches documents of a specific type (e.g., purchase or sales invoices) from the Yuki Archive API.
        :param document_type: The type of document to fetch (e.g., 2 for Purchase Invoice, 3 for Sales Invoice).
        :param start_date: The start date for the document search (format: YYYY-MM-DD).
        :param end_date: The end date for the document search (format: YYYY-MM-DD).
        :param number_of_records: The number of records to retrieve (default: 100).
        :param start_record: The starting record index (default: 0).
        :return: A list of documents with relevant details.
        """
        if not self.session_id:
            self.authenticate()

        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:DocumentsByType>
                 <they:sessionID>{self.session_id}</they:sessionID>
                 <they:documentType>{document_type}</they:documentType>
                 <they:sortOrder>DocumentDateAsc</they:sortOrder>
                 <they:startDate>{start_date}</they:startDate>
                 <they:endDate>{end_date}</they:endDate>
                 <they:numberOfRecords>{number_of_records}</they:numberOfRecords>
                 <they:startRecord>{start_record}</they:startRecord>
              </they:DocumentsByType>
           </soapenv:Body>
        </soapenv:Envelope>
        '''
        headers = {'Content-Type': 'text/xml'}  # No SOAPAction header
        logger.debug("Sending DocumentsByType request...")
        logger.debug("XML Payload: %s", xml_payload)
        response = requests.post(f"{self.BASE_URL}{self.ARCHIVE_SERVICE}", headers=headers, data=xml_payload)

        if response.status_code == 200:
            logger.debug("DocumentsByType response: %s", response.text)
            return self._parse_documents_by_type(response.content)
        else:
            logger.error("Failed to fetch documents. Status code: %s, Response: %s", response.status_code,
                         response.text)
            return []

    def _parse_documents_by_type(self, xml_response: str) -> List[Dict]:
        """
        Parses XML response into a list of documents for the DocumentsByType operation.
        """
        documents = []
        root = ElementTree.fromstring(xml_response)
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://www.theyukicompany.com/',
            'default': ''  # The empty namespace for the Documents element
        }

        # Find the Documents element
        documents_result = root.find('.//soap:Body/ns:DocumentsByTypeResponse/ns:DocumentsByTypeResult', namespaces)

        if documents_result is not None:
            # Find all Document elements within the Documents element
            for doc in documents_result.findall('.//default:Documents/default:Document', namespaces):
                document_data = {
                    "id": doc.attrib.get("ID"),
                    "subject": doc.find("default:Subject", namespaces).text,
                    "document_date": doc.find("default:DocumentDate", namespaces).text,
                    "amount": float(doc.find("default:Amount", namespaces).text),
                    "folder": doc.find("default:Folder", namespaces).attrib.get("ID"),
                    "tab": doc.find("default:Tab", namespaces).attrib.get("ID"),
                    "type": doc.find("default:Type", namespaces).text,
                    "type_description": doc.find("default:TypeDescription", namespaces).text,
                    "file_name": doc.find("default:FileName", namespaces).text,
                    "content_type": doc.find("default:ContentType", namespaces).text,
                    "file_size": int(doc.find("default:FileSize", namespaces).text),
                    "contact_name": doc.find("default:ContactName", namespaces).text if doc.find("default:ContactName",
                                                                                                 namespaces) is not None else None,
                    "contact_id": doc.find("default:ContactId", namespaces).text if doc.find("default:ContactId",
                                                                                             namespaces) is not None else None,
                    "reference": doc.find("default:Reference", namespaces).text if doc.find("default:Reference",
                                                                                            namespaces) is not None else None,
                    "vat_amount": float(doc.find("default:VATAmount", namespaces).text) if doc.find("default:VATAmount",
                                                                                                    namespaces) is not None else None,
                    "created": doc.find("default:Created", namespaces).text,
                    "creator": doc.find("default:Creator", namespaces).text,
                    "modified": doc.find("default:Modified", namespaces).text,
                    "modifier": doc.find("default:Modifier", namespaces).text,
                }
                documents.append(document_data)

        print("Total Documents:", len(documents))
        return documents

    def fetch_all_invoices(self, start_date: str, end_date: str) -> Dict[str, List[Dict]]:
        """
        Fetches all sales and purchase invoices and categorizes them.
        :param start_date: The start date for the document search (format: YYYY-MM-DD).
        :param end_date: The end date for the document search (format: YYYY-MM-DD).
        :return: A dictionary containing sales and purchase invoices.
        """
        sales_invoices = self.fetch_documents_by_type(document_type=3, start_date=start_date, end_date=end_date)
        purchase_invoices = self.fetch_documents_by_type(document_type=2, start_date=start_date, end_date=end_date)
        return {
            "sales_invoices": sales_invoices,
            "purchase_invoices": purchase_invoices,
        }

    def fetch_document_details(self, document_id: str) -> Dict:
        """
        Fetches complete details of a document using the DocumentXMLData API.
        :param document_id: The ID of the document to fetch.
        :return: A dictionary containing the complete details of the document.
        """
        if not self.session_id:
            self.authenticate()

        xml_payload = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
           <soapenv:Header/>
           <soapenv:Body>
              <they:DocumentXMLData>
                 <they:sessionID>{self.session_id}</they:sessionID>
                 <they:documentID>{document_id}</they:documentID>
              </they:DocumentXMLData>
           </soapenv:Body>
        </soapenv:Envelope>
        '''
        headers = {'Content-Type': 'text/xml'}
        response = requests.post(f"{self.BASE_URL}{self.ARCHIVE_SERVICE}", headers=headers, data=xml_payload)
        # import pdb;
        # pdb.set_trace()
        # print(response.text)
        if response.status_code == 200:
            return self._parse_document_details(response.content)
        else:
            logger.error(
                f"Failed to fetch document details. Status code: {response.status_code}, Response: {response.text}")
            return {}

    def _parse_document_details(self, xml_response: str) -> Dict:
        """
        Parses the XML response from DocumentXMLData into a dictionary for UBL format.
        :param xml_response: The XML response from the API.
        :return: A dictionary containing the document details.
        """
        document_details = {}
        root = ElementTree.fromstring(xml_response)
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://www.theyukicompany.com/',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
        }

        # Find the Invoice element
        invoice = root.find('.//soap:Body/ns:DocumentXMLDataResponse/ns:DocumentXMLDataResult/ubl:Invoice', namespaces)
        if invoice is None:
            logger.warning("No invoice details found in the response.")
            return document_details

        # Parse basic invoice details
        document_details = {
            "id": invoice.find("cbc:ID", namespaces).text,
            "uuid": invoice.find("cbc:UUID", namespaces).text,
            "issue_date": invoice.find("cbc:IssueDate", namespaces).text,
            "due_date": invoice.find("cbc:DueDate", namespaces).text,
            "invoice_type_code": invoice.find("cbc:InvoiceTypeCode", namespaces).text,
            "note": invoice.find("cbc:Note", namespaces).text if invoice.find("cbc:Note",
                                                                              namespaces) is not None else None,
            "currency": invoice.find("cbc:DocumentCurrencyCode", namespaces).text,
            "supplier": {
                "id": invoice.find("cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID",
                                   namespaces).text,
                "name": invoice.find("cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name", namespaces).text,
                "address": {
                    "street": invoice.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:StreetName",
                                           namespaces).text,
                    "city": invoice.find("cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:CityName",
                                         namespaces).text,
                    "postal_code": invoice.find(
                        "cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:PostalZone", namespaces).text,
                    "country": invoice.find(
                        "cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode",
                        namespaces).text,
                },
                "tax_scheme": {
                    "company_id": invoice.find("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID",
                                               namespaces).text,
                    "tax_scheme_id": invoice.find(
                        "cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID",
                        namespaces).text,
                },
                "contact": {
                    "phone": invoice.find("cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone",
                                          namespaces).text,
                }
            },
            "customer": {
                "id": invoice.find("cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID",
                                   namespaces).text,
                "name": invoice.find("cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name", namespaces).text,
                "address": {
                    "street": invoice.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:StreetName",
                                           namespaces).text,
                    "city": invoice.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CityName",
                                         namespaces).text,
                    "postal_code": invoice.find(
                        "cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:PostalZone", namespaces).text,
                    "country": invoice.find(
                        "cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode",
                        namespaces).text,
                },
                "tax_scheme": {
                    "company_id": invoice.find("cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID",
                                               namespaces).text,
                    "tax_scheme_id": invoice.find(
                        "cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID",
                        namespaces).text,
                },
                "contact": {
                    "email": invoice.find("cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail",
                                          namespaces).text,
                }
            },
            "payment_means": {
                "code": invoice.find("cac:PaymentMeans/cbc:PaymentMeansCode", namespaces).text,
                "due_date": invoice.find("cac:PaymentMeans/cbc:PaymentDueDate", namespaces).text,
                "payment_id": invoice.find("cac:PaymentMeans/cbc:PaymentID", namespaces).text,
                "financial_account": {
                    "iban": invoice.find("cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:ID", namespaces).text,
                    "name": invoice.find("cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:Name", namespaces).text,
                }
            },
            "tax_total": {
                "amount": float(invoice.find("cac:TaxTotal/cbc:TaxAmount", namespaces).text),
                "currency": invoice.find("cac:TaxTotal/cbc:TaxAmount", namespaces).attrib.get("currencyID"),
                "subtotal": {
                    "taxable_amount": float(
                        invoice.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount", namespaces).text),
                    "tax_amount": float(invoice.find("cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount", namespaces).text),
                    "percent": float(invoice.find("cac:TaxTotal/cac:TaxSubtotal/cbc:Percent", namespaces).text),
                    "tax_category": {
                        "id": invoice.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:ID", namespaces).text,
                        "name": invoice.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Name", namespaces).text,
                        "percent": float(
                            invoice.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent", namespaces).text),
                        "tax_scheme": invoice.find("cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID",
                                                   namespaces).text,
                    }
                }
            },
            "legal_monetary_total": {
                "line_extension_amount": float(
                    invoice.find("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces).text),
                "tax_exclusive_amount": float(
                    invoice.find("cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount", namespaces).text),
                "tax_inclusive_amount": float(
                    invoice.find("cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", namespaces).text),
                "payable_amount": float(invoice.find("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces).text),
            },
            "invoice_lines": []
        }

        # Parse invoice lines
        # for line in invoice.findall("cac:InvoiceLine", namespaces):
        #     invoice_line = {
        #         "id": line.find("cbc:ID", namespaces).text,
        #         "uuid": line.find("cbc:UUID", namespaces).text,
        #         "note": line.find("cbc:Note", namespaces).text if line.find("cbc:Note",
        #                                                                     namespaces) is not None else None,
        #         "quantity": float(line.find("cbc:InvoicedQuantity", namespaces).text),
        #         "line_amount": float(line.find("cbc:LineExtensionAmount", namespaces).text),
        #         "item": {
        #             "name": line.find("cac:Item/cbc:Name", namespaces).text,
        #         },
        #         "price": {
        #             "amount": float(line.find("cac:Price/cbc:PriceAmount", namespaces).text),
        #             "currency": line.find("cac:Price/cbc:PriceAmount", namespaces).attrib.get("currencyID"),
        #         }
        #     }
        #     document_details["invoice_lines"].append(invoice_line)

        return document_details

    def categorize_invoices(self, administration_id: str, start_date: str, end_date: str) -> Dict[str, List[Dict]]:
        """
        Categorizes invoices into paid and pending based on outstanding items.
        :param administration_id: The ID of the administration to fetch data for.
        :param start_date: The start date for the document search (format: YYYY-MM-DD).
        :param end_date: The end date for the document search (format: YYYY-MM-DD).
        :return: A dictionary containing categorized invoices.
        """
        # Fetch all invoices
        invoices = self.fetch_all_invoices(start_date=start_date, end_date=end_date)
        sales_invoices = invoices["sales_invoices"]
        purchase_invoices = invoices["purchase_invoices"]

        # Fetch outstanding items
        outstanding_creditor_items = self.fetch_outstanding_creditor_items(administration_id)
        outstanding_debtor_items = self.fetch_outstanding_debtor_items(administration_id)

        print(outstanding_creditor_items)
        # Extract DocumentIDs from outstanding items
        outstanding_creditor_ids = {item["document_id"] for item in outstanding_creditor_items}
        outstanding_debtor_ids = {item["document_id"] for item in outstanding_debtor_items}

        # Categorize purchase invoices (creditor items)
        categorized_purchase_invoices = []
        for invoice in purchase_invoices:
            if invoice["id"] in outstanding_creditor_ids:
                invoice["status"] = "pending"
            else:
                invoice["status"] = "paid"
            categorized_purchase_invoices.append(invoice)

        # Categorize sales invoices (debtor items)
        categorized_sales_invoices = []
        for invoice in sales_invoices:
            if invoice["id"] in outstanding_debtor_ids:
                invoice["status"] = "pending"
            else:
                invoice["status"] = "paid"
            categorized_sales_invoices.append(invoice)

        return {
            "sales_invoices": categorized_sales_invoices,
            "purchase_invoices": categorized_purchase_invoices,
        }




client = YukiClient(api_key)

# Fetch administrations
administrations = client.fetch_administrations()
print("Administrations:", administrations)

start_date = "2020-01-01"
end_date = "2025-03-01"

# purchase_invoices = client.fetch_documents_by_type(document_type=2, start_date="2020-01-01", end_date="2025-03-03")
# print("Purchase Invoices:", purchase_invoices)
#
# # Fetch sales invoices (type 3)
# sales_invoices = client.fetch_documents_by_type(document_type=3, start_date="2020-01-01", end_date="2025-03-03")
# print("Sales Invoices:", sales_invoices)


# documents = client.fetch_documents(start_date, end_date)
# print("Documents:", documents)

# Fetch outstanding creditor items (purchase-related) for the first administration
if administrations:
    administration_id = administrations[0]["id"]
    categorized_invoices = client.categorize_invoices(administration_id=administration_id, start_date=start_date,
                                                      end_date=end_date)

    # Print results
    print("Categorized Sales Invoices:")
    for invoice in categorized_invoices["sales_invoices"]:
        print(f"ID: {invoice['id']}, Subject: {invoice['subject']}, Status: {invoice['status']}")

    print("\nCategorized Purchase Invoices:")
    for invoice in categorized_invoices["purchase_invoices"]:
        print(f"ID: {invoice['id']}, Subject: {invoice['subject']}, Status: {invoice['status']}")
        # print(invoice)
        # if invoice.get('status') == 'paid':
        # print(client.fetch_document_details(invoice.get('id')))
