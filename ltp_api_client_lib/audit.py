import requests
from .ltp_api_client import LtpApiClient, LtpResponse


class Audit(LtpApiClient):
    def __init__(self, ltp_api_address=None):
        super(Audit, self).__init__(ltp_api_address)
        self.subtype = 'audit'

    def get_for_archive(self, archive_pk: int, limit=10):
        """
        Get all audit for archive under context.
        :param archive_pk:
        :param limit:
        :return:
        """
        self._setup_header()
        url = self.build_url(
            get_attr={'group': self.context, 'limit': limit},
            extend_url=['archive', f'{archive_pk}'],
        )
        response = requests.get(url, headers=self.header)
        return LtpResponse(response)

    def list_for_archive(self, limit=10):
        """
        Get all audit under context.
        :param limit:
        :return:
        """
        self._setup_header()
        url = self.build_url(get_attr={'group': self.context, 'limit': limit})
        response = requests.get(url, headers=self.header)
        return LtpResponse(response)
