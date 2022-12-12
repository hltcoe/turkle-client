import json
import os.path

from .client import Permissions
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
            raise TurkleClientException("--file must be set for 'users create'")
        with open(file, 'r') as fh:
            data = [json.loads(line) for line in fh]
            self.client.create(data)
            return f"{plural(len(data), 'user', 'users')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'users update'")
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
            raise ValueError("--file must be set for 'groups create'")
        with open(file, 'r') as fh:
            data = [json.loads(line) for line in fh]
            self.client.create(data)
            return f"{plural(len(data), 'group', 'groups')} created\n"

    def addusers(self, id, file, **kwargs):
        # file contains json encoded list of user ids
        if not id:
            raise ValueError("--id must be set for 'groups addusers'")
        if not file:
            raise ValueError("--file must be set for 'groups addusers'")
        with open(file, 'r') as fh:
            data = json.load(fh)
            self.client.addusers(id, data)
            return f"{plural(len(data), 'user', 'users')} added to the group\n"


class ProjectsWrapper(Wrapper):
    def retrieve(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'projects retrieve'")
        return self.client.retrieve(id) + "\n"

    def create(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'projects create'")
        with open(file, 'r') as fh:
            projects = []
            for line in fh:
                project = json.loads(line.strip())
                if 'html_template' not in project:
                    with open(project['filename'], 'r') as template_fh:
                        project['html_template'] = template_fh.read()
                        project['filename'] = os.path.basename(project['filename'])
                projects.append(project)
            self.client.create(projects)
            return f"{plural(len(projects), 'project', 'projects')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'projects update'")
        with open(file, 'r') as fh:
            projects = []
            for line in fh:
                project = json.loads(line.strip())
                if 'html_template' not in project and 'filename' in project:
                    with open(project['filename'], 'r') as template_fh:
                        project['html_template'] = template_fh.read()
                        project['filename'] = os.path.basename(project['filename'])
                projects.append(project)
            self.client.update(projects)
            return f"{plural(len(projects), 'project', 'projects')} updated\n"

    def batches(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'projects batches'")
        return self.client.batches(id)


class BatchesWrapper(Wrapper):
    def retrieve(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'batches retrieve'")
        return self.client.retrieve(id) + "\n"

    def create(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'batches create'")
        with open(file, 'r') as fh:
            batches = []
            for line in fh:
                batch = json.loads(line)
                with open(batch['filename'], 'r') as csv_fh:
                    batch['csv_text'] = csv_fh.read()
                    batch['filename'] = os.path.basename(batch['filename'])
                batches.append(batch)
            self.client.create(batches)
            return f"{plural(len(batches), 'batch', 'batches')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'batches update'")
        with open(file, 'r') as fh:
            data = [json.loads(line) for line in fh]
            self.client.update(data)
            return f"{plural(len(data), 'batch', 'batches')} updated\n"

    def input(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'batches input'")
        return self.client.input(id)

    def progress(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'batches progress'")
        return self.client.progress(id) + "\n"

    def results(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'batches results'")
        return self.client.results(id)


class PermissionsWrapper(Wrapper):
    def _prepare_args(self, pid, bid):
        if pid:
            return Permissions.PROJECT, pid
        else:
            return Permissions.BATCH, bid

    def retrieve(self, pid, bid, **kwargs):
        if not pid and not bid:
            raise TurkleClientException("--pid or --bid is required for 'permissions retrieve'")
        text = self.client.retrieve(*self._prepare_args(pid, bid))
        return text + "\n"

    def add(self, pid, bid, file, **kwargs):
        if not pid and not bid:
            raise TurkleClientException("--pid or --bid is required for 'permissions add'")
        if not file:
            raise ValueError("--file must be set for 'permissions add'")
        with open(file, 'r') as fh:
            data = json.load(fh)
            text = self.client.add(*self._prepare_args(pid, bid), data)
            return text + "\n"

    def replace(self, pid, bid, file, **kwargs):
        if not pid and not bid:
            raise TurkleClientException("--pid or --bid is required for 'permissions replace'")
        if not file:
            raise ValueError("--file must be set for 'permissions replace'")
        with open(file, 'r') as fh:
            data = json.load(fh)
            text = self.client.replace(*self._prepare_args(pid, bid), data)
            return text + "\n"
