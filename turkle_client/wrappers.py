import csv
import json
import os.path

from .client import Permissions
from .exceptions import TurkleClientException


def plural(num, single, mult):
    return f"{num} {single if num == 1 else mult}"


def load_records(file_path, exts=None):
    """
    Yields dictionaries from a .jsonl, .json or .csv file.

    Args:
        file_path (str): Path to the input file
        exts (list): List of extensions to support

    Returns:
        Iterator: iterator over dictionaries
    """
    exts = exts if exts else ['.jsonl', '.json', '.csv']
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in exts:
        raise ValueError(f"Unsupported file format: {ext}")

    try:
        with open(file_path, 'r', encoding='utf-8') as fh:
            if ext == '.jsonl':
                for lineno, line in enumerate(fh, start=1):
                    if not line.strip():
                        continue  # skip blank lines
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON on line {lineno} in {file_path}: {e}")
            elif ext == '.csv':
                reader = csv.DictReader(fh)
                for row in reader:
                    yield row
            elif ext == '.json':
                yield json.load(fh)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
    except OSError as e:
        raise ValueError(f"Could not open file {file_path}: {e}")


class Wrapper:
    """
    Client wrappers that massage input and output to match expectations for the CLI
    """
    def __init__(self, client):
        self.client = client

    def list(self, **kwargs):
        return self.client.list()


class UsersWrapper(Wrapper):
    def retrieve(self, id, username, **kwargs):
        if id:
            return self.client.retrieve(id) + "\n"
        elif username:
            return self.client.retrieve_by_username(username) + "\n"
        else:
            raise TurkleClientException("--id or --username must be set for 'users retrieve'")

    def create(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'users create'")

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file), start=1):
                self.client.create(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on line {lineno} in {file}: {e}")

        return f"{plural(lineno, 'user', 'users')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'users update'")

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file), start=1):
                self.client.update(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on line {lineno} in {file}: {e}")

        return f"{plural(lineno, 'user', 'users')} updated\n"


class GroupsWrapper(Wrapper):
    def retrieve(self, id, name, **kwargs):
        if id:
            return self.client.retrieve(id) + "\n"
        elif name:
            return self.client.retrieve_by_name(name)
        else:
            raise TurkleClientException("--id or --name must be set for 'groups retrieve'")

    def create(self, file, **kwargs):
        if not file:
            raise ValueError("--file must be set for 'groups create'")

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file, [".jsonl", ".json"]), start=1):
                self.client.create(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on object {lineno} in {file}: {e}")

        return f"{plural(lineno, 'group', 'groups')} created\n"

    def addusers(self, id, file, **kwargs):
        # file contains json encoded list of user ids
        if not id:
            raise ValueError("--id must be set for 'groups addusers'")
        if not file:
            raise ValueError("--file must be set for 'groups addusers'")

        try:
            user_ids = next(load_records(file, [".json"]))
            self.client.addusers(id, user_ids)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure in {file}: {e}")
        return f"{plural(len(user_ids), 'user', 'users')} added to the group\n"


class ProjectsWrapper(Wrapper):
    def retrieve(self, id, **kwargs):
        if not id:
            raise TurkleClientException("--id must be set for 'projects retrieve'")
        return self.client.retrieve(id) + "\n"

    def create(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'projects create'")

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file, [".jsonl", ".json"]), start=1):
                if 'html_template' not in obj:
                    with open(os.path.expanduser(obj['filename']), 'r') as template_fh:
                        obj['html_template'] = template_fh.read()
                        obj['filename'] = os.path.basename(obj['filename'])
                self.client.create(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on object {lineno} in {file}: {e}")

        return f"{plural(lineno, 'project', 'projects')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'projects update'")

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file, [".jsonl", ".json"]), start=1):
                if 'html_template' not in obj:
                    with open(os.path.expanduser(obj['filename']), 'r') as template_fh:
                        obj['html_template'] = template_fh.read()
                        obj['filename'] = os.path.basename(obj['filename'])
                self.client.create(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on object {lineno} in {file}: {e}")

        return f"{plural(lineno, 'project', 'projects')} updated\n"

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

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file, [".jsonl", ".json"]), start=1):
                with open(os.path.expanduser(obj['filename']), 'r') as csv_fh:
                    obj['csv_text'] = csv_fh.read()
                    obj['filename'] = os.path.basename(obj['filename'])
                self.client.create(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on object {lineno} in {file}: {e}")

        return f"{plural(lineno, 'batch', 'batches')} created\n"

    def update(self, file, **kwargs):
        if not file:
            raise TurkleClientException("--file must be set for 'batches update'")

        lineno = 0
        try:
            for lineno, obj in enumerate(load_records(file, [".jsonl", ".json"]), start=1):
                if 'filename' in obj:
                    with open(os.path.expanduser(obj['filename']), 'r') as csv_fh:
                        obj['csv_text'] = csv_fh.read()
                        obj['filename'] = os.path.basename(obj['filename'])
                self.client.update(obj)
        except TurkleClientException as e:
            raise TurkleClientException(f"Failure on object {lineno} in {file}: {e}")

        return f"{plural(lineno, 'batch', 'batches')} updated\n"

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
        text = self.client.get(*self._prepare_args(pid, bid))
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
