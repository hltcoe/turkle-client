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
    def __init__(self, base_url, token, debug=False):
        """Construct a client

        Args:
            base_url (str): The URL of the Turkle site
            token (str): An authentication token for Turkle
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'Authorization': f'TOKEN {token}'}
        self.debug = debug

    class Urls:
        # child classes must set the list and detail url for that part of the API
        list = ""
        detail = ""

    def list(self):
        """List all instances (user, group, project, batch)

        Returns:
            str: jsonl where each line is an object
        """
        url = self.Urls.list.format(base=self.base_url)
        return self._walk(url)

    def retrieve(self, instance_id):
        """Retrieve an instance from an id (user, group, project, batch)

        Args:
            instance_id (int): Instance id

        Returns:
            str: instance encoded as json
        """
        url = self.Urls.detail.format(base=self.base_url, id=instance_id)
        response = self._get(url)
        return response.text

    def create(self, instance):
        """Create an instance (user, group, project, batch)

        Args:
            instance (dict): Instance fields as dict

        Returns:
            str: json representation of the created instance
        """
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, instance)
        return response.text

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
            raise TurkleClientException(f"Unable to connect to {self.base_url}")

    def _post(self, url, data, *args, **kwargs):
        try:
            response = requests.post(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise TurkleClientException(f"Unable to connect to {self.base_url}")

    def _patch(self, url, data, *args, **kwargs):
        try:
            response = requests.patch(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise TurkleClientException(f"Unable to connect to {self.base_url}")

    def _put(self, url, data, *args, **kwargs):
        try:
            response = requests.put(url, *args, **kwargs, json=data, headers=self.headers)
            if response.status_code >= 400:
                self._handle_errors(response)
            return response
        except requests.exceptions.ConnectionError:
            raise TurkleClientException(f"Unable to connect to {self.base_url}")

    def _handle_errors(self, response):
        data = response.json()
        if data:
            if 'detail' in data:
                raise TurkleClientException(data['detail'])
            else:
                # grab the first error
                parts = next(iter(data.items()))
                raise TurkleClientException(f"{parts[0]} - {parts[1][0]}")


class Users(Client):
    class Urls:
        list = "{base}/api/users/"
        detail = "{base}/api/users/{id}/"
        username = "{base}/api/users/username/{username}/"

    def retrieve_by_username(self, username):
        """Retrieve a user from a username

        Args:
            username (str): Username
        Returns:
            str: user object as json
        """
        url = self.Urls.username.format(base=self.base_url, username=username)
        response = self._get(url)
        return response.text

    def create(self, user):
        """Create a user

        Args:
            user (dict): User fields as dict

        Returns:
            str: json representation of the created user
        """
        if self.debug:
            print(f"Debug: New user dict: {user}")
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, user)
        return response.text

    def update(self, user):
        """Update a user

        Args:
            user (dict): User fields as dict including id

        Returns:
            str: json representation of the updated user
        """
        url = self.Urls.detail.format(base=self.base_url, id=user['id'])
        response = self._patch(url, user)
        return response.text


class Groups(Client):
    class Urls:
        list = "{base}/api/groups/"
        detail = "{base}/api/groups/{id}/"
        name = "{base}/api/groups/name/{name}/"
        addusers = "{base}/api/groups/{id}/users/"

    def retrieve_by_name(self, name):
        """Retrieve groups from a name

        Args:
            name (str): Group name

        Returns:
            str: jsonl with each line being a group that has that name
        """
        url = self.Urls.name.format(base=self.base_url, name=name)
        return self._walk(url)

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

    def create(self, project):
        """Create a project

        Args:
            project (dict): Project fields as a dict

        Returns:
            str: json representation of the created project
        """
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, project)
        return response.text

    def update(self, project):
        """Update a project

        Args:
            project (dict): Project fields including the id

        Returns:
            str: json representation of the updated project
        """
        url = self.Urls.detail.format(base=self.base_url, id=project['id'])
        response = self._patch(url, project)
        return response.text

    def batches(self, project_id):
        """List all batches for a project

        Args:
            project_id (int): Project id

        Returns:
            str: jsonl where each line is a batch object
        """
        url = self.Urls.batches.format(base=self.base_url, id=project_id)
        return self._walk(url)


class Batches(Client):
    class Urls:
        list = "{base}/api/batches/"
        detail = "{base}/api/batches/{id}/"
        input = "{base}/api/batches/{id}/input/"
        results = "{base}/api/batches/{id}/results/"
        progress = "{base}/api/batches/{id}/progress/"

    def create(self, batch):
        """Create a batch

        Args:
            batch (dict): Batch fields as a dict

        Returns:
            str: json representation of the created batch
        """
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, batch)
        return response.text

    def update(self, batch):
        """Update a batch

        Cannot update the CSV data. See addtasks to add additional tasks.

        Args:
            batch (dict): Batch fields as a dict including the id

        Returns:
            str: json representations of the updated batch
        """
        url = self.Urls.detail.format(base=self.base_url, id=batch['id'])
        response = self._patch(url, batch)
        return response.text

    def input(self, batch_id):
        """Get the input CSV for the batch

        Args:
            batch_id (int): Batch id

        Returns:
             str: CSV data as a string
        """
        url = self.Urls.input.format(base=self.base_url, id=batch_id)
        response = self._get(url)
        return response.text

    def results(self, batch_id):
        """Get the results CSV for the batch

        Args:
            batch_id (int): Batch id

        Returns:
             str: CSV data as a string
        """
        url = self.Urls.results.format(base=self.base_url, id=batch_id)
        response = self._get(url)
        return response.text

    def progress(self, batch_id):
        """Get the progress information for the batch

        Args:
            batch_id (int): batch id

        Returns:
             str: json progress object
        """
        url = self.Urls.progress.format(base=self.base_url, id=batch_id)
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

    def get(self, instance_type, instance_id):
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

    def list(self):
        raise NotImplementedError()

    def create(self, instance):
        raise NotImplementedError()

    def retrieve(self, instance_id):
        raise NotImplementedError()
