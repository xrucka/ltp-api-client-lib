import requests
import json
import os
from .ltp_api_client import LtpApiClient, LtpResponse, custom_response
CHUNK_SIZE_128M = 134217728


def read_in_chunks(file_object, chunk_size=CHUNK_SIZE_128M):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


class Archive(LtpApiClient):
    """
    Archive updates LtpApiClient class. This class defines all method
    for requesting (create, update, get, list, download) LTP-API for work
    with archive.
    ```python
    archive_client = Archive()
    response = archive_client.setup_context("test")
                             .setup_token("token")
                             .create({"name": "archive", "user_metadata": {}},
                                      "/path/to/file")

    ```
    """
    def __init__(self, ltp_api_address=None):
        super(Archive, self).__init__(ltp_api_address)
        self.subtype = "archive"

    @staticmethod
    def _upload(response_api, path):
        print(response_api)
        parts_url = response_api["parts_url"]
        chunk_size = response_api["chunk_size"]
        checksum_update = response_api["checksum_update"]
        finish_url = response_api["finish_url"]
        upload_id = response_api["upload_id"]
        origin = response_api["origin"]
        parts = []
        filename = os.path.basename(path)
        with open(path, "rb") as rf:
            for part_no, chunk in enumerate(read_in_chunks(rf, chunk_size)):
                url = parts_url[part_no]
                print(f"uploading part {part_no} to url: {url}")
                res = requests.put(url, data=chunk)
                print(f"headers: {res.headers}")
                etag = res.headers.get('ETag')
                parts.append({'ETag': etag, 'PartNumber': part_no + 1})
        s3_response = requests.post(finish_url, json={
            "checksum_update": checksum_update,
            "upload_id": upload_id,
            "parts": parts,
            "origin": origin,
            "filename": filename
        })
        print(s3_response, s3_response.text)

        return LtpResponse(s3_response)

    def create(self, data: dict, path: str) -> LtpResponse:
        """
        Creates archive.
        1) call api with data provided at args
        2) Uploading right into S3
        :param data:
        :param path:
        :return:
        """
        self._setup_header()
        url = self.build_url()
        if data is not None and isinstance(data, dict):
            data.update({"group": self.context})
        response = requests.post(url,
                                 json=data,
                                 headers=self.header)
        response_api = json.loads(response.json())
        return self._upload(response_api, path)

    def get(self, pk: int) -> LtpResponse:
        """
        Get all archives under context.
        :param pk:
        :return:
        """
        self._setup_header()
        url = self.build_url(get_attr={"group": {self.context}}, extend_url=[f"{pk}"])
        response = requests.get(url, headers=self.header)
        return LtpResponse(response)

    def download(self, pk: int, destination_path: str, chunk_size=100000) -> LtpResponse:
        """
        Prepare download package returns url for fetching
        :param destination_path:
        :param pk:
        :param chunk_size:
        :return:
        """
        self._setup_header()
        url = self.build_url(get_attr={"group": {self.context}}, extend_url=[f"{pk}", "download"])
        response = requests.get(url, headers=self.header)
        resp = LtpResponse(response)
        req = requests.get(resp.data.get("url"))
        with open(destination_path, 'wb') as wf:
            for chunk in req.iter_content(chunk_size):
                wf.write(chunk)
        return custom_response(200, "OK", {"Message": f"Archive was download successfully to {destination_path}"})

    def put(self, pk: int, new_data: dict = None, path: str = "") -> LtpResponse:
        """
        Updates archive.
        1) call api with data provided at args
        2) Uploading right into S3
        :param pk:
        :param new_data:
        :param path:
        :return:
        """
        self._setup_header()
        url = self.build_url(extend_url=[f"{pk}"])
        if new_data is not None and isinstance(new_data, dict):
            new_data.update({"group": self.context})
        resp = requests.put(url,
                            json=new_data,
                            headers=self.header)
        response_api = json.loads(resp.json())
        return self._upload(response_api, path)

    def patch(self, pk, new_data: dict = None) -> LtpResponse:
        """
        Updates archive.
        :param new_data:
        :param pk:
        :return:
        """
        self._setup_header()
        url = self.build_url(extend_url=[f"{pk}"])
        if new_data is not None and isinstance(new_data, dict):
            new_data.update({"group": self.context})

        response = requests.patch(url,
                                  json=new_data,
                                  headers=self.header)
        return LtpResponse(response)

    def list(self, limit=10) -> LtpResponse:
        """
        Get all archives under context.
        :param limit:
        :return:
        """
        self._setup_header()
        url = self.build_url(get_attr={"group": self.context, "limit": limit})
        response = requests.get(url, headers=self.header)
        return LtpResponse(response)
