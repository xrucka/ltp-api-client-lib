import requests
import json
import os
from .ltp_api_client import LtpApiClient, LtpResponse, custom_response
import time

CHUNK_SIZE_128M = 134_217_728


def read_in_chunks(file_object, chunk_size=CHUNK_SIZE_128M):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def upload_part(url, file_name, cursor, part_no, chunk_size):
    with open(file_name, 'rb') as rf:
        rf.seek(cursor)
        data = rf.read(chunk_size)
        print(f'{part_no} data size: {len(data)}')
        if data is None or len(data) == 0:
            return None
        for i in range(0, 5):
            try:
                print(f'uploading part {part_no} to url: {url}')
                res = requests.put(url, data=data)
                if 'Connection' in res.headers and res.headers['Connection'] == 'close':
                    continue
                print(f'{part_no} - headers: {res.headers}')
                etag = res.headers.get('ETag', '')
                return {'ETag': etag.replace('"', ''), 'PartNumber': part_no}
            except Exception as e:
                print(f'Error {e} tryies: {i}')
                time.sleep(1)


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
        self.subtype = 'archive'

    @staticmethod
    def _upload(response_api, path):
        import multiprocessing as mp

        # print(f'Uploading {response_api}')
        parts_url = response_api['parts_url']
        chunk_size = response_api['chunk_size']
        checksum_update = response_api['checksum_update']
        finish_url = response_api['finish_url']
        upload_id = response_api['upload_id']
        origin = response_api['origin']
        expected_num_chunks = response_api['num_chunks']
        parts = []
        filename = os.path.basename(path)
        futures = []
        with mp.Pool(mp.cpu_count()) as pool:
            for i in range(0, expected_num_chunks):
                url = parts_url[i]
                part_no = i + 1
                cursor = i * chunk_size
                futures.append(
                    pool.apply_async(
                        upload_part, args=[url, path, cursor, part_no, chunk_size]
                    )
                )
            for fut in futures:
                part = fut.get()
                if part is not None:
                    parts.append(part)

        print(
            f'Finishing checksum_update: {checksum_update}, upload_id: {upload_id}, {origin}, filename: {filename} - {parts}'
        )
        s3_response = requests.post(
            finish_url,
            json={
                'checksum_update': checksum_update,
                'upload_id': upload_id,
                'parts': parts,
                'origin': origin,
                'filename': filename,
            },
        )

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
            data.update({'group': self.context})
        data.update({'file_size': os.path.getsize(path)})
        response = requests.post(url, json=data, headers=self.header)
        try:
            response_api = json.loads(response.json())
            return self._upload(response_api, path)
        except:
            return LtpResponse(response)

    def get(self, pk: int) -> LtpResponse:
        """
        Get all archives under context.
        :param pk:
        :return:
        """
        self._setup_header()
        url = self.build_url(get_attr={'group': {self.context}}, extend_url=[f'{pk}'])
        response = requests.get(url, headers=self.header)
        return LtpResponse(response)

    def download(
        self, pk: int, destination_path: str, chunk_size=100_000
    ) -> LtpResponse:
        """
        Prepare download package returns url for fetching
        :param destination_path:
        :param pk:
        :param chunk_size:
        :return:
        """
        self._setup_header()
        url = self.build_url(extend_url=[f'{pk}', 'download'], get_attr={'group': self.context})
        print(f'{url} - {self.context}')
        response = requests.get(url, headers=self.header)
        print(f'response {response}')
        if response.status_code == 204:
            return custom_response(
                200, 'OK', {'Message': 'Package preparing please try again later'}
            )
        elif response.status_code == 200:
            resp = response.json()
            url = resp.get('url')
            print(f'URL for download: {url}')
            req = requests.get(url)
            with open(destination_path, 'wb') as wf:
                for chunk in req.iter_content(chunk_size):
                    wf.write(chunk)
            return custom_response(
                200,
                'OK',
                {'Message': f'Archive was download successfully to {destination_path}'},
            )
        return LtpResponse()

    def put(self, pk: int, new_data: dict = None, path: str = '') -> LtpResponse:
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
        url = self.build_url(extend_url=[f'{pk}'])
        if new_data is not None and isinstance(new_data, dict):
            new_data.update({'group': self.context})
        new_data.update({'file_size': os.path.getsize(path)})
        resp = requests.put(url, json=new_data, headers=self.header)
        if resp.status_code > 300:
            return LtpResponse(resp)
        response = resp.json()
        if isinstance(response, str):
            response_api = json.loads(resp.json())
        else:
            response_api = response
        print(f"{response_api}")
        return self._upload(response_api, path)

    def patch(self, pk, new_data: dict = None) -> LtpResponse:
        """
        Updates archive.
        :param new_data:
        :param pk:
        :return:
        """
        self._setup_header()
        url = self.build_url(extend_url=[f'{pk}'])
        if new_data is not None and isinstance(new_data, dict):
            new_data.update({'group': self.context})

        response = requests.patch(url, json=new_data, headers=self.header)
        return LtpResponse(response)

    def list(self, limit=10) -> LtpResponse:
        """
        Get all archives under context.
        :param limit:
        :return:
        """
        self._setup_header()
        url = self.build_url(get_attr={'group': self.context, 'limit': limit})
        response = requests.get(url, headers=self.header)
        return LtpResponse(response)
