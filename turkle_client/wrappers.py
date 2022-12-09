import json

from .exceptions import TurkleClientException


def plural(num, single, mult):
    return f"{num} {single if num == 1 else mult}"


class Wrapper:
    """
    Client wrappers that massage input and output to match exceptions for the CLI
    """
    def __init__(self, client):
        self.client = client

    def list(self, **kwargs):
        return self.client.list()


class UsersWrapper(Wrapper):
    def retrieve(self, id, username, **kwargs):
        if not id and not username:
            raise TurkleClientException("--id or --username must be set for 'users retrieve'")
        return self.client.retrieve(id, username) + "\n"

    def create(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for users create")
        with open(file, 'r') as fh:
            data = [json.loads(line) for line in fh]
            self.client.create(data)
            return f"{plural(len(data), 'user', 'users')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for users update")
        with open(file, 'r') as fh:
            data = [json.loads(line) for line in fh]
            self.client.update(data)
            return f"{plural(len(data), 'user', 'users')} updated\n"


class GroupsWrapper(Wrapper):
    def retrieve(self, id, name, **kwargs):
        if not id and not name:
            raise TurkleClientException("--id or --name must be set for 'groups retrieve'")
        return self.client.retrieve(id, name) + "\n"

    def create(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for groups create")
        url = self.Urls.list.format(base=self.base_url)
        with open(file, 'r') as fh:
            count = 0
            for line in fh:
                self._post(url, json.loads(line.strip()))
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
            self._post(url, data)
        return f"{plural(len(data['users']), 'user', 'users')} add to the group"
