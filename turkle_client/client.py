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

    def walk(self, url,  **kwargs):
        jsonl = io.StringIO()
        data = {'next': url}
        while data['next']:
            response = self.get(data['next'], **kwargs)
            if response.status_code >= 400:
                self.handle_errors(response)
            data = response.json()
            for instance in data['results']:
                jsonl.write(json.dumps(instance, ensure_ascii=False) + os.linesep)
        return jsonl.getvalue().rstrip(os.linesep)

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
        username = "{base}/api/users/username/{username}/"

    def list(self, **kwargs):
        url = self.Urls.list.format(base=self.base_url)
        return self.walk(url)

    def retrieve(self, id=None, username=None, **kwargs):
        if id:
            url = self.Urls.detail.format(base=self.base_url, id=id)
        elif username:
            url = self.Urls.username.format(base=self.base_url, username=username)
        else:
            raise ValueError(f"--id or --username must be set for 'users retrieve'")
        response = self.get(url)
        return response.text

    def create(self, file, **kwargs):
        if not file:
            raise ValueError(f"--file must be set for users create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                self.post(url, json.loads(line.strip()))
                count += 1
        return f"{plural(count, 'user', 'users')} created"

    def update(self, file, **kwargs):
        if not file:
            raise ValueError(f"--file must be set for users update")
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                data = json.loads(line.strip())
                url = self.Urls.detail.format(base=self.base_url, id=data['id'])
                self.patch(url, data)
                count += 1
        return f"{plural(count, 'user', 'users')} updated"


class Groups(Client):
    class Urls:
        list = "{base}/api/groups/"
        detail = "{base}/api/groups/{id}/"
        name = "{base}/api/groups/name/{name}/"
        addusers = "{base}/api/groups/{id}/users/"

    def list(self, **kwargs):
        url = self.Urls.list.format(base=self.base_url)
        return self.walk(url)

    def retrieve(self, id=None, name=None, **kwargs):
        if id:
            url = self.Urls.detail.format(base=self.base_url, id=id)
            response = self.get(url)
            return response.text
        elif name:
            url = self.Urls.name.format(base=self.base_url, name=name)
            return self.walk(url)
        else:
            raise ValueError(f"--id or --name must be set for 'groups retrieve'")

    def create(self, file, **kwargs):
        if not file:
            raise ValueError(f"--file must be set for groups create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                self.post(url, json.loads(line.strip()))
                count += 1
        return f"{plural(count, 'user', 'users')} created"

    def addusers(self, id, file, **kwargs):
        if not id:
            raise ValueError(f"--id must be set for groups addusers")
        if not file:
            raise ValueError(f"--file must be set for groups addusers")
        url = self.Urls.addusers.format(base=self.base_url, id=id)
        with open(file, 'r') as fh:
            data = json.load(fh)
            self.post(url, data)
        return f"{plural(len(data['users']), 'user', 'users')} add to the group"
