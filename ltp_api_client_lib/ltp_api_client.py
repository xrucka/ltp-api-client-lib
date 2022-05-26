import os


class LtpApiClient:
    """
    Basic class which wraps main functionality for communication with LTP-API.
    Contains method for setup context, token etc. This class should be extend for
    calling api see archive.py.
    Builder pattern is used.
    """

    def __init__(self, ltp_api_address=None):
        self.ltp_api_address = (
            ltp_api_address
            if ltp_api_address is not None
            else os.environ.get('LTP_API_ADDRESS', 'https://ltp.cesnet.cz/api/')
        )
        self.ltp_api_address_with_version = os.path.join(self.ltp_api_address, 'v2')
        self.token = os.environ.get('LTP_API_TOKEN', None)
        self.header = None
        self.context = os.environ.get('LTP_API_CONTEXT', None)
        self.subtype = None

    def __str__(self):
        return f'{self.ltp_api_address} - {self.context} - {self.token}'

    def _setup_header(self):
        self.header = {'Authorization': f'Token {self.token}'}

    def setup_token(self, token: str):
        self.token = token
        return self

    def setup_context(self, context: str):
        self.context = context
        return self

    def build_url(self, get_attr: dict = None, extend_url=None) -> str:
        if extend_url is None:
            extend_url = []
        url = os.path.join(self.ltp_api_address_with_version, self.subtype)
        for sub in extend_url:
            url = os.path.join(url, sub)
        url += '/'
        if get_attr is not None:
            get_params = '?' + '&'.join([f'{k}={v}' for k, v in get_attr.items()])
            url += get_params
        print(f'URL {url}')
        return url


class LtpResponse:
    status = None
    message = None
    data = None

    def __init__(self, response=None):
        if response is not None:
            self.from_requests_response(response)

    def __str__(self):
        return f'[{self.status}]: {self.message}'

    def from_requests_response(self, response):
        self.status = response.status_code
        self.message = response.text
        # print(f'Response {self.message}')
        try:
            self.data = response.json()
        except Exception as e:
            print(f'Response xception {e} {self.message}')
            self.data = {}


def custom_response(status, message, data):
    response = LtpResponse()
    response.data = data
    response.message = message
    response.status = status
    return response
