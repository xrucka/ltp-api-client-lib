import requests
from .ltp_api_client import LtpApiClient, LtpResponse


class Audit(LtpApiClient):
    def __init__(self, ltp_api_address=None):
        super(Audit, self).__init__(ltp_api_address)

    def get_for_archive(self, archive_pk, limit=10):
        """
        Get all audit for archive under context.
        :param archive_pk:
        :param limit:
        :return:
        """
        self._setup_header()
        get_request_url = f"{self.ltp_api_address}{self.version}/audit/archive/" \
                          f"{archive_pk}/?context={self.context}&limit={limit}"
        response = requests.get(get_request_url,
                                headers=self.header)
        print(response)
        print(response.text)
        return LtpResponse(response)

    def list_for_archive(self, limit=10):
        """
        Get all audit under context.
        :param limit:
        :return:
        """
        self._setup_header()
        get_request_url = f"{self.ltp_api_address}{self.version}/audit/" \
                          f"?context={self.context}&limit={limit}"

        response = requests.get(get_request_url,
                                headers=self.header)
        print(response)
        print(response.text)
        return LtpResponse(response)
