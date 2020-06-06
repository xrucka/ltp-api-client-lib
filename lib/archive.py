import requests
import json
from .ltp_api_client import LtpApiClient, LtpResponse, custom_response


class Archive(LtpApiClient):
    """
    Archive extends LtpApiClient class. This class defines all method
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

    def create(self, data, path):
        """
        Creates archive.
        1) call api with data provided at args
        2) Uploading right into S3
        :param data:
        :param path:
        :return:
        """
        self._setup_header()
        response = requests.post(f"{self.ltp_api_address}{self.version}/archive/",
                                 json=data,
                                 headers=self.header)
        response_api = json.loads(response.json())
        print(response_api)
        p = path.split("/")
        filename = p[len(p) - 1]
        print(filename)
        with open(path, "rb") as rf:
            s3_request_data = response_api["data"]["fields"]
            url = response_api["data"]["url"]
            s3_response = requests.post(url, data=s3_request_data, files={"file": (filename, rf)})
            print(s3_response, s3_response.text)
        return LtpResponse(s3_response)

    def get(self, pk):
        """
        Get all archives under context.
        :param context:
        :return:
        """
        self._setup_header()
        response = requests.get(f"{self.ltp_api_address}{self.version}/archive/{pk}/?context={self.context}",
                                headers=self.header)
        print(response)
        print(response.text)
        return LtpResponse(response)

    def download(self, pk, destination_path, chunk_size=100000):
        """
        Prepare download package returns url for fetching
        :param destination_path:
        :param pk:
        :param context:
        :return:
        """
        self._setup_header()
        response = requests.get(f"{self.ltp_api_address}{self.version}/archive/{pk}/download/?context={self.context}",
                               headers=self.header)
        print(response)
        print(response.text)
        resp = LtpResponse(response)
        req = requests.get(resp.data.get("url"))
        with open(destination_path, 'wb') as wf:
            for chunk in req.iter_content(chunk_size):
                wf.write(chunk)
        return custom_response(200, "OK", {"Message": "Archive was download successfully to {destination_path}"})

    def put(self, pk, data, path):
        """
        Updates archive.
        1) call api with data provided at args
        2) Uploading right into S3
        :param pk:
        :param data:
        :param path:
        :return:
        """
        self._setup_header()
        resp = requests.put(f"{self.ltp_api_address}{self.version}/archive/{pk}/",
                            json=data,
                            headers=self.header)
        response_api = json.loads(resp.json())
        p = path.split("/")
        filename = p[len(p) - 1]
        print(filename)
        with open("bag-correct_zip.zip", "rb") as rf:
            s3_request_data = response_api["data"]["fields"]
            url = response_api["data"]["url"]
            s3_response = requests.post(url, data=s3_request_data, files={"file": (filename, rf)})
            print(s3_response, s3_response.text)
        return LtpResponse(s3_response)

    def patch(self, pk, new_data):
        """
        Updates archive.
        :param pk:
        :param data:
        :param path:
        :return:
        """
        self._setup_header()
        response = requests.patch(f"{self.ltp_api_address}{self.version}/archive/{pk}/",
                                  json=new_data,
                                  headers=self.header)
        print(response, response.json())
        return LtpResponse(response)

    def list(self):
        """
        Get all archives under context.
        :param context:
        :return:
        """
        self._setup_header()
        response = requests.get(f"{self.ltp_api_address}{self.version}/archive/?context={self.context}",
                                headers=self.header)
        print(response)
        print(response.text)
        return LtpResponse(response)
