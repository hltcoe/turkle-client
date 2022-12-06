import io
import json
import os

import requests


def plural(num, single, mult):
    return f"{num} {single if num == 1 else mult}"


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

    def post(self, url, data, *args, **kwargs):
        try:
            response = requests.post(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self.handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def patch(self, url, data, *args, **kwargs):
        try:
            response = requests.patch(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self.handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def handle_errors(self, response):
        data = response.json()
        if data:
            if 'detail' in data:
                raise ValueError(data['detail'])
            else:
                raise ValueError(next(iter(data.items()))[1])


class Users(Client):
    class Urls:
        list = "{base}/api/users/"
        detail = "{base}/api/users/{id}/"

    def list(self, **kwargs):
        users_jsonl = io.StringIO()
        data = {'next': self.Urls.list.format(base=self.base_url)}
        while data['next']:
            response = self.get(data['next'])
            data = response.json()
            for user in data['results']:
                users_jsonl.write(json.dumps(user, ensure_ascii=False) + os.linesep)
        return users_jsonl.getvalue().rstrip(os.linesep)

    def retrieve(self, id, **kwargs):
        url = self.Urls.detail.format(base=self.base_url, id=id)
        response = self.get(url)
        return response.text

    def create(self, file, **kwargs):
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                self.post(url, json.loads(line.strip()))
                count += 1
        return f"{plural(count, 'user', 'users')} created"

    def update(self, file, **kwargs):
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                data = json.loads(line.strip())
                url = self.Urls.detail.format(base=self.base_url, id=data['id'])
                self.patch(url, data)
                count += 1
        return f"{plural(count, 'user', 'users')} updated"
