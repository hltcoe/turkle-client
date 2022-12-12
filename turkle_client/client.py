import io
import json
import os

import requests

from .exceptions import TurkleClientException


class Client:
    """
    Base client for Turkle REST API

    The child classes are Users, Groups, Projects, Batches, and Permissions.
    Their methods return json/jsonl or csv data as a string.
    """
    def __init__(self, base_url, token):
        """Construct a client

        Args:
            base_url (str): The URL of the Turkle site
            token (str): An authentication token for Turkle
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'Authorization': f'TOKEN {token}'}

    def list(self):
        """List all instances

        Returns:
            str: jsonl where each line is an object
        """
        url = self.Urls.list.format(base=self.base_url)
        return self._walk(url)

    def _walk(self, url,  **kwargs):
        jsonl = io.StringIO()
        data = {'next': url}
        while data['next']:
            response = self._get(data['next'], **kwargs)
            if response.status_code >= 400:
                self._handle_errors(response)
            data = response.json()
            for instance in data['results']:
                jsonl.write(json.dumps(instance, ensure_ascii=False) + os.linesep)
        return jsonl.getvalue()

    def _get(self, url, *args, **kwargs):
        try:
            response = requests.get(url, *args, **kwargs, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def _post(self, url, data, *args, **kwargs):
        try:
            response = requests.post(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def _patch(self, url, data, *args, **kwargs):
        try:
            response = requests.patch(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def _put(self, url, data, *args, **kwargs):
        try:
            response = requests.put(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Unable to connect to {self.base_url}")

    def _handle_errors(self, response):
        data = response.json()
        if data:
            if 'detail' in data:
                raise ValueError(data['detail'])
            else:
                # grab the first error
                parts = next(iter(data.items()))
                raise ValueError(f"{parts[0]} - {parts[1][0]}")


class Users(Client):
    class Urls:
        list = "{base}/api/users/"
        detail = "{base}/api/users/{id}/"
        username = "{base}/api/users/username/{username}/"

    def retrieve(self, id=None, username=None):
        """Retrieve a user using id or username

        Args:
            id (int): User id
            username (str): Username
        Returns:
            str: user object as json
        """
        if id:
            url = self.Urls.detail.format(base=self.base_url, id=id)
        elif username:
            url = self.Urls.username.format(base=self.base_url, username=username)
        else:
            raise TurkleClientException("id or username must be passed")
        response = self._get(url)
        return response.text

    def create(self, users):
        """Create users

        Args:
            users (list): List of user object dictionaries

        Returns:
            str: jsonl where each line is a created user
        """
        url = self.Urls.list.format(base=self.base_url)
        text = ''
        for user in users:
            response = self._post(url, user)
            text += response.text + '\n'
        return text

    def update(self, users):
        """Update users

        Args:
            users (list): List of user object dictionaries with ids

        Returns:
            str: jsonl where each line is an updated user
        """
        text = ''
        for user in users:
            url = self.Urls.detail.format(base=self.base_url, id=user['id'])
            response = self._patch(url, user)
            text += response.text + '\n'
        return text


class Groups(Client):
    class Urls:
        list = "{base}/api/groups/"
        detail = "{base}/api/groups/{id}/"
        name = "{base}/api/groups/name/{name}/"
        addusers = "{base}/api/groups/{id}/users/"

    def retrieve(self, id=None, name=None):
        """Retrieve a group(s) using id or name

        Args:
            id (int): Group id
            name (str): Group name

        Returns:
            str: single line if using id and one or more lines if name
        """
        if id:
            url = self.Urls.detail.format(base=self.base_url, id=id)
            response = self._get(url)
            return response.text
        elif name:
            url = self.Urls.name.format(base=self.base_url, name=name)
            return self._walk(url)
        else:
            raise TurkleClientException("id or name must be passed")

    def create(self, groups):
        """Create groups

        Args:
            groups (list): List of group object dictionaries

        Returns:
            str: jsonl where each line is a created group
        """
        url = self.Urls.list.format(base=self.base_url)
        text = ''
        for group in groups:
            response = self._post(url, group)
            text += response.text + '\n'
        return text

    def addusers(self, group_id, user_ids, **kwargs):
        """Add users to a group

        Args:
            group_id (int): Group id
            user_ids (list): List of User ids

        Returns:
            str: jsonl where each line is a created group
        """
        url = self.Urls.addusers.format(base=self.base_url, id=group_id)
        data = {'users': user_ids}
        response = self._post(url, data)
        return response.text


class Projects(Client):
    class Urls:
        list = "{base}/api/projects/"
        detail = "{base}/api/projects/{id}/"
        batches = "{base}/api/projects/{id}/batches/"

    def retrieve(self, id):
        """Retrieve a project using id

        Args:
            id (int): project id

        Returns:
            str: project encoded as json
        """
        url = self.Urls.detail.format(base=self.base_url, id=id)
        response = self._get(url)
        return response.text

    def create(self, projects):
        """Create projects

        Args:
            projects (list): List of project object dictionaries

        Returns:
            str: jsonl where each line is a created project
        """
        url = self.Urls.list.format(base=self.base_url)
        text = ''
        for project in projects:
            response = self._post(url, project)
            text += response.text + '\n'
        return text

    def update(self, projects):
        """Update projects

        Args:
            projects (list): List of project object dictionaries with ids

        Returns:
            str: jsonl where each line is an updated project
        """
        text = ''
        for project in projects:
            url = self.Urls.detail.format(base=self.base_url, id=project['id'])
            response = self._patch(url, project)
            text += response.text + '\n'
        return text

    def batches(self, id):
        """List all batches for a project

        Returns:
            str: jsonl where each line is a batch object
        """
        url = self.Urls.batches.format(base=self.base_url, id=id)
        return self._walk(url)


class Batches(Client):
    class Urls:
        list = "{base}/api/batches/"
        detail = "{base}/api/batches/{id}/"
        input = "{base}/api/batches/{id}/input/"
        results = "{base}/api/batches/{id}/results/"
        progress = "{base}/api/batches/{id}/progress/"

    def retrieve(self, id):
        """Retrieve a batch using id

        Args:
            id (int): batch id

        Returns:
            str: batch encoded as json
        """
        url = self.Urls.detail.format(base=self.base_url, id=id)
        response = self._get(url)
        return response.text

    def create(self, batches):
        """Create batches

        Args:
            batches (list): List of batch object dictionaries

        Returns:
            str: jsonl where each line is a created batch
        """
        url = self.Urls.list.format(base=self.base_url)
        text = ''
        for batch in batches:
            response = self._post(url, batch)
            text += response.text + '\n'
        return text

    def update(self, batches):
        """Update batches

        Cannot update the CSV data. See addtasks to add additional tasks.

        Args:
            batches (list): List of batch object dictionaries with ids

        Returns:
            str: jsonl where each line is an updated batch
        """
        text = ''
        for batch in batches:
            url = self.Urls.detail.format(base=self.base_url, id=batch['id'])
            response = self._patch(url, batch)
            text += response.text + '\n'
        return text

    def input(self, id):
        """Get the input CSV for the batch

        Args:
            id (int): batch id

        Returns:
             str: CSV data as a string
        """
        url = self.Urls.input.format(base=self.base_url, id=id)
        response = self._get(url)
        return response.text

    def results(self, id):
        """Get the results CSV for the batch

        Args:
            id (int): batch id

        Returns:
             str: CSV data as a string
        """
        url = self.Urls.results.format(base=self.base_url, id=id)
        response = self._get(url)
        return response.text

    def progress(self, id):
        """Get the progress information for the batch

        Args:
            id (int): batch id

        Returns:
             str: json progress object
        """
        url = self.Urls.progress.format(base=self.base_url, id=id)
        response = self._get(url)
        return response.text


class Permissions(Client):
    class Urls:
        projects = "{base}/api/projects/{id}/permissions/"
        batches = "{base}/api/batches/{id}/permissions/"

    PROJECT = 'project'
    BATCH = 'batch'

    def _get_url(self, instance_type, instance_id):
        if instance_type == self.PROJECT:
            url = self.Urls.projects.format(base=self.base_url, id=instance_id)
        elif instance_type == self.BATCH:
            url = self.Urls.batches.format(base=self.base_url, id=instance_id)
        else:
            raise TurkleClientException(f"Unrecognized instance type: {instance_type}")
        return url

    def retrieve(self, instance_type, instance_id):
        """Get the permissions for the project or batch

        Args:
            instance_type (str): Name of the type (project, batch)
            instance_id (int): Id of the project or batch

        Returns:
            str: json representation of the permissions
        """
        url = self._get_url(instance_type, instance_id)
        response = self._get(url)
        return response.text

    def add(self, instance_type, instance_id, permissions):
        """Add additional users and groups to the permissions

        Args:
            instance_type (str): Name of the type (project, batch)
            instance_id (int): Id of the project or batch
            permissions (dict): Dictionary with keys 'users' and 'groups' for lists of ids

        Returns:
            str: json representation of the updated permissions
        """
        url = self._get_url(instance_type, instance_id)
        response = self._post(url, permissions)
        return response.text

    def replace(self, instance_type, instance_id, permissions):
        """Replace the permissions

        Args:
            instance_type (str): Name of the type (project, batch)
            instance_id (int): Id of the project or batch
            permissions (dict): Dictionary with keys 'users' and 'groups' for lists of ids

        Returns:
            str: json representation of the updated permissions
        """
        url = self._get_url(instance_type, instance_id)
        response = self._put(url, permissions)
        return response.text
