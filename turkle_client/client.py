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

    def put(self, url, data, *args, **kwargs):
        try:
            response = requests.put(url, *args, **kwargs, json=data, headers=self.headers)
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
            raise ValueError("--id or --username must be set for 'users retrieve'")
        response = self.get(url)
        return response.text

    def create(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for users create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                self.post(url, json.loads(line.strip()))
                count += 1
        return f"{plural(count, 'user', 'users')} created"

    def update(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for users update")
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
            raise ValueError("--file must be set for groups create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                self.post(url, json.loads(line.strip()))
                count += 1
        return f"{plural(count, 'user', 'users')} created"

    def addusers(self, id, file, **kwargs):
        if not id:
            raise ValueError("--id must be set for groups addusers")
        if not file:
            raise ValueError("--file must be set for groups addusers")
        url = self.Urls.addusers.format(base=self.base_url, id=id)
        with open(file, 'r') as fh:
            data = json.load(fh)
            self.post(url, data)
        return f"{plural(len(data['users']), 'user', 'users')} add to the group"


class Projects(Client):
    class Urls:
        list = "{base}/api/projects/"
        detail = "{base}/api/projects/{id}/"

    def list(self, **kwargs):
        url = self.Urls.list.format(base=self.base_url)
        return self.walk(url)

    def retrieve(self, id=None, **kwargs):
        if not id:
            raise ValueError("--id must be set for 'projects retrieve'")
        url = self.Urls.detail.format(base=self.base_url, id=id)
        response = self.get(url)
        return response.text

    def create(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for projects create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                data = json.loads(line.strip())
                if 'html_template' not in data:
                    with open(data['filename'], 'r') as csv_fh:
                        data['html_template'] = csv_fh.read()
                        data['filename'] = os.path.basename(data['filename'])
                self.post(url, data)
                count += 1
        return f"{plural(count, 'project', 'projects')} created"

    def update(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for projects update")
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                data = json.loads(line.strip())
                if 'html_template' not in data and 'filename' in data:
                    with open(data['filename'], 'r') as csv_fh:
                        data['html_template'] = csv_fh.read()
                        data['filename'] = os.path.basename(data['filename'])
                url = self.Urls.detail.format(base=self.base_url, id=data['id'])
                self.patch(url, data)
                count += 1
        return f"{plural(count, 'project', 'projects')} updated"


class Batches(Client):
    class Urls:
        list = "{base}/api/batches/"
        detail = "{base}/api/batches/{id}/"

    def list(self, **kwargs):
        url = self.Urls.list.format(base=self.base_url)
        return self.walk(url)

    def retrieve(self, id=None, **kwargs):
        if not id:
            raise ValueError(f"--id must be set for 'batches retrieve'")
        url = self.Urls.detail.format(base=self.base_url, id=id)
        response = self.get(url)
        return response.text

    def create(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for batches create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                data = json.loads(line.strip())
                with open(data['filename'], 'r') as csv_fh:
                    data['csv_text'] = csv_fh.read()
                    data['filename'] = os.path.basename(data['filename'])
                self.post(url, data)
                count += 1
        return f"{plural(count, 'batch', 'batches')} created"

    def update(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for batches update")
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                data = json.loads(line.strip())
                url = self.Urls.detail.format(base=self.base_url, id=data['id'])
                self.patch(url, data)
                count += 1
        return f"{plural(count, 'batch', 'batches')} updated"


class Permissions(Client):
    class Urls:
        projects = "{base}/api/projects/{id}/permissions/"
        batches = "{base}/api/batches/{id}/permissions/"

    def get_url(self, pid=None, bid=None):
        if pid:
            url = self.Urls.projects.format(base=self.base_url, id=pid)
        elif bid:
            url = self.Urls.batches.format(base=self.base_url, id=bid)
        else:
            raise ValueError("--pid or --bid is required")
        return url

    def retrieve(self, pid=None, bid=None, **kwargs):
        url = self.get_url(pid, bid)
        response = self.get(url)
        return response.text

    def add(self, pid=None, bid=None, file=None, **kwargs):
        if not file:
            raise ValueError("--file must be set for permissions add")
        url = self.get_url(pid, bid)
        with open(file, 'r') as fh:
            data = json.load(fh)
            self.post(url, data)
        return "Permissions updated"

    def replace(self, pid=None, bid=None, file=None, **kwargs):
        if not file:
            raise ValueError("--file must be set for permissions replace")
        url = self.get_url(pid, bid)
        with open(file, 'r') as fh:
            data = json.load(fh)
            self.put(url, data)
        return "Permissions updated"
