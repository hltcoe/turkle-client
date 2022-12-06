import io
import json
import os

import requests


class Client:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {'Authorization': f'TOKEN {token}'}

    def get(self, url, *args, **kwargs):
        try:
            response = requests.get(url, *args, **kwargs, headers=self.headers)
            if response.status_code >= 400:
                self.handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def handle_errors(self, response):
        print(response.status_code)
        if response.status_code == 403:
            raise ValueError(response.json()['detail'])
        elif response.status_code == 404:
            raise ValueError(response.json()['detail'])


class Users(Client):
    class Urls:
        list = "{base}/api/users/"
        detail = "{base}/api/users/{id}/"

    def list(self, **kwargs):
        users_jsonl = io.StringIO()
        url = self.Urls.list.format(base=self.base_url)
        response = self.get(url)
        data = response.json()
        for user in data['results']:
            users_jsonl.write(json.dumps(user, ensure_ascii=False) + os.linesep)
        return users_jsonl.getvalue().rstrip(os.linesep)

    def retrieve(self, id, **kwargs):
        url = self.Urls.detail.format(base=self.base_url, id=id)
        response = self.get(url)
        return response.text
