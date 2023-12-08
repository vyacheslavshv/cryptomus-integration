import requests
from .utils import sign_request
from .exceptions import CryptomusAPIException


class CryptomusAPI:
    """
    A class to interact with the Cryptomus API.
    """
    def __init__(self, merchant_uuid, api_key):
        """
        Initializes the API client with merchant UUID and API key.

        :param merchant_uuid: Merchant's UUID.
        :param api_key: API key for authentication.
        """
        self.merchant_uuid = merchant_uuid
        self.api_key = api_key
        self.base_url = "https://api.cryptomus.com/v1/"

    def send_request(self, endpoint, data):
        """
        Sends a request to a given Cryptomus API endpoint.

        :param endpoint: API endpoint to send the request to.
        :param data: Data to be sent in the request.
        :return: JSON response from the API.
        """
        headers = {
            'merchant': self.merchant_uuid,
            'sign': sign_request(data, self.api_key),
            'Content-Type': 'application/json'
        }
        response = requests.post(self.base_url + endpoint, headers=headers, json=data)
        if response.status_code != 200:
            raise CryptomusAPIException(response.text)
        return response.json()['result']

    def create_invoice(self, amount, order_id, currency='USDT', network='tron',
                       additional_data=None, **kwargs):
        """
        Creates a new invoice.

        :param amount: Amount to be paid.
        :param order_id: Unique order ID in your system.
        :param currency: Currency code (default is 'USDT').
        :param network: Blockchain network code (default is 'tron').
        :param additional_data: Optional additional data.
        :return: Details of the created invoice.
        """
        data = {
            "amount": amount,
            "currency": currency,
            "order_id": str(order_id),
            "network": network,
            "additional_data": additional_data,
            **kwargs
        }
        return self.send_request("payment", data)

    def generate_qr(self, invoice_uuid):
        """
        Generates a QR code for a given invoice.

        :param invoice_uuid: Invoice UUID.
        :return: Base64 encoded QR-code image.
        """
        data = {"merchant_payment_uuid": invoice_uuid}
        return self.send_request("payment/qr", data)

    def payment_info(self, order_id=None, uuid=None, paid_status=False):
        """
        Fetches payment information by order ID or invoice UUID.

        :param order_id: Order ID in your system.
        :param uuid: Invoice UUID.
        :param paid_status: If True, returns payment status (paid or not).
        :return: Payment information or boolean payment status if 'paid_status' is True.
        """
        if not (order_id or uuid):
            raise ValueError("Either 'order_id' or 'uuid' must be provided")
        data = {}
        if order_id:
            data['order_id'] = str(order_id)
        if uuid:
            data['uuid'] = uuid
        response = self.send_request("payment/info", data)
        if not paid_status:
            return response
        return response['payment_status'] in ('paid', 'paid_over')

    def is_paid(self, order_id=None, uuid=None):
        """
        Checks if the payment for a given order ID or invoice UUID is complete.

        :param order_id: Order ID in your system.
        :param uuid: Invoice UUID.
        :return: True if paid, False otherwise.
        """
        return self.payment_info(order_id, uuid, paid_status=True)

    def get_payment_history(self, date_from=None, date_to=None, cursor=None):
        """
        Retrieves payment history with optional date filters and pagination.

        :param date_from: Start date for filtering (optional).
        :param date_to: End date for filtering (optional).
        :param cursor: Cursor for pagination (optional).
        :return: Payment history data.
        """
        data = {}
        if date_from:
            data['date_from'] = date_from
        if date_to:
            data['date_to'] = date_to
        if cursor:
            data['cursor'] = cursor
        return self.send_request("payment/list", data)
