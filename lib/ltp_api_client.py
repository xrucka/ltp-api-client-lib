import os


class LtpApiClient:
    """
    Basic class which wraps main functionality for communication with LTP-API.
    Contains method for setup context, token etc. This class should be extend for
    calling api see archive.py.
    Builder pattern is used.
    """
    def __init__(self, ltp_api_address=None):
        self.ltp_api_address = ltp_api_address if ltp_api_address is not None \
            else os.environ.get("LTP_API_ADDRESS", "https://rep2.du2.cesnet.cz/api/")
        self.version = 2
        self.token = os.environ.get("LTP_API_TOKEN", None)
        self.header = None
        self.context = os.environ.get("LTP_API_CONTEXT", None)

    def _setup_header(self):
        self.header = {'Authorization': f'Token {self.token}'}

    def setup_token(self, token: str):
        self.token = token
        return self

    def setup_context(self, context: str):
        self.context = context
        return self


class LtpResponse:
    status = None
    message = None
    data = None

    def __init__(self, response=None):
        if response is not None:
            self.from_requests_response(response)

    def from_requests_response(self, response):
        self.status = response.status_code
        self.message = response.text
        try:
            self.data = response.json()
        except Exception as e:
            print(e)
            self.data = {}


def custom_response(status, message, data):
    response = LtpResponse()
    response.data = data
    response.message = message
    response.status = status
    return response
