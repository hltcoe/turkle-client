import io
import json
import os

import requests

from .exceptions import TurkleClientException


class Client:
    """
    Client for the Turkle REST API

    Contains individual objects for each section of API:
      user = client.users.retrieve_by_username("smith")
      group = client.groups.create({'name': 'Spanish', 'users': [5, 43]})
      projects = client.projects.list()

    Methods raise TurkleClientException if errors
    """
    def __init__(self, base_url, token, debug=False):
        """Construct a client

        Args:
            base_url (str): The URL of the Turkle site
            token (str): An authentication token for Turkle
            debug (bool): Whether to log input to the methods
        """
        self.users = Users(base_url, token, debug)
        self.groups = Groups(base_url, token, debug)
        self.projects = Projects(base_url, token, debug)
        self.batches = Batches(base_url, token, debug)
        self.permissions = Permissions(base_url, token, debug)


class ClientBase:
    """
    Base client for Turkle REST API

    The child classes are Users, Groups, Projects, Batches, and Permissions.
    Their methods return dicts or csv data as a string.
    """
    def __init__(self, base_url, token, debug=False):
        """Construct a client base

        Args:
            base_url (str): The URL of the Turkle site
            token (str): An authentication token for Turkle
            debug (bool): Whether to log input to the methods
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'Authorization': f'Token {token}'}
        self.debug = debug

    class Urls:
        # child classes must set the list and detail url for that part of the API
        list = ""
        detail = ""

    def _walk(self, url,  **kwargs):
        objs = []
        data = {'next': url}
        while data['next']:
            response = self._get(data['next'], **kwargs)
            if response.status_code >= 400:
                self._handle_errors(response)
            data = response.json()
            objs.extend(data['results'])
        return objs

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
                raise TurkleClientException(f"{parts[0]} - {parts[1]}")


class CrudMixin:
    """
    Generic list, retrieve, and create methods for the entity-specific classes
    """

    def list(self):
        """List all instances (user, group, project, batch)

        Returns:
            list: list of instance dicts
        """
        url = self.Urls.list.format(base=self.base_url)
        return self._walk(url)

    def retrieve(self, instance_id):
        """Retrieve an instance from an id (user, group, project, batch)

        Args:
            instance_id (int): Instance id

        Returns:
            dict: retrieved instance
        """
        url = self.Urls.detail.format(base=self.base_url, id=instance_id)
        response = self._get(url)
        return response.json()

    def create(self, instance):
        """Create an instance (group, project, batch)

        Args:
            instance (dict): Instance fields as dict

        Returns:
            dict: created instance
        """
        if self.debug:
            print(f"Debug: Create object dict: {instance}")
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, instance)
        return response.json()


class Users(CrudMixin, ClientBase):
    class Urls:
        list = "{base}/api/users/"
        detail = "{base}/api/users/{id}/"
        username = "{base}/api/users/username/{username}/"

    def retrieve_by_username(self, username):
        """Retrieve a user from a username

        Args:
            username (str): Username
        Returns:
            dict: retrieved user
        """
        url = self.Urls.username.format(base=self.base_url, username=username)
        response = self._get(url)
        return response.json()

    def create(self, user):
        """Create a user

        Args:
            user (dict): User fields as dict

        Returns:
            dict: created user
        """
        if self.debug:
            print(f"Debug: New user dict: {user}")
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, user)
        return response.json()

    def update(self, user):
        """Update a user

        Args:
            user (dict): User fields as dict including id

        Returns:
            dict: updated user
        """
        if self.debug:
            print(f"Debug: Updated user dict: {user}")
        url = self.Urls.detail.format(base=self.base_url, id=user['id'])
        response = self._patch(url, user)
        return response.json()


class Groups(CrudMixin, ClientBase):
    class Urls:
        list = "{base}/api/groups/"
        detail = "{base}/api/groups/{id}/"
        name = "{base}/api/groups/name/{name}/"
        add_users = "{base}/api/groups/{id}/users/"

    def retrieve_by_name(self, name):
        """Retrieve groups from a name

        Args:
            name (str): Group name

        Returns:
            list: list of dicts for groups with that name
        """
        url = self.Urls.name.format(base=self.base_url, name=name)
        return self._walk(url)

    def add_users(self, group_id, user_ids, **kwargs):
        """Add users to a group

        Args:
            group_id (int): Group id
            user_ids (list): List of User ids

        Returns:
            dict: updated group
        """
        url = self.Urls.add_users.format(base=self.base_url, id=group_id)
        data = {'users': user_ids}
        response = self._post(url, data)
        return response.json()


class Projects(CrudMixin, ClientBase):
    class Urls:
        list = "{base}/api/projects/"
        detail = "{base}/api/projects/{id}/"
        batches = "{base}/api/projects/{id}/batches/"

    def create(self, project):
        """Create a project

        Args:
            project (dict): Project fields as a dict

        Returns:
            dict: created project
        """
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, project)
        return response.json()

    def update(self, project):
        """Update a project

        Args:
            project (dict): Project fields including the id

        Returns:
            dict: updated project
        """
        url = self.Urls.detail.format(base=self.base_url, id=project['id'])
        response = self._patch(url, project)
        return response.json()

    def batches(self, project_id):
        """List all batches for a project

        Args:
            project_id (int): Project id

        Returns:
            list: list of dicts for the project's batches
        """
        url = self.Urls.batches.format(base=self.base_url, id=project_id)
        return self._walk(url)


class Batches(CrudMixin, ClientBase):
    class Urls:
        list = "{base}/api/batches/"
        detail = "{base}/api/batches/{id}/"
        input = "{base}/api/batches/{id}/input/"
        results = "{base}/api/batches/{id}/results/"
        progress = "{base}/api/batches/{id}/progress/"
        tasks = "{base}/api/batches/{id}/tasks/"

    def create(self, batch):
        """Create a batch

        Args:
            batch (dict): Batch fields as a dict

        Returns:
            dict: created batch
        """
        url = self.Urls.list.format(base=self.base_url)
        response = self._post(url, batch)
        return response.json()

    def update(self, batch):
        """Update a batch

        Cannot update the CSV data. See add_tasks to add additional tasks.

        Args:
            batch (dict): Batch fields as a dict including the id

        Returns:
            dict: updated batch
        """
        if 'csv_text' in batch:
            raise TurkleClientException("Cannot update the csv data using update. Use add_tasks")
        url = self.Urls.detail.format(base=self.base_url, id=batch['id'])
        response = self._patch(url, batch)
        return response.json()

    def add_tasks(self, batch):
        """Add tasks to a batch

        Can only add tasks. Cannot update other fields.

        Args:
            batch (dict): Dict with id and csv_text as only fields

        Returns:
            dict: updated batch
        """
        if set(batch.keys()) != {'id', 'csv_text'}:
            raise TurkleClientException("add_tasks requires 'id' and 'csv_text'")
        url = self.Urls.tasks.format(base=self.base_url, id=batch['id'])
        response = self._post(url, batch)
        return response.json()

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
             dict: progress object as dict
        """
        url = self.Urls.progress.format(base=self.base_url, id=batch_id)
        response = self._get(url)
        return response.json()


class Permissions(ClientBase):
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
        """Retrieve the permissions for a project or batch

        Args:
            instance_type (str): Name of the type (project, batch)
            instance_id (int): ID of the project or batch

        Returns:
            dict: representation of the permissions
        """
        url = self._get_url(instance_type, instance_id)
        response = self._get(url)
        return response.json()

    def add(self, instance_type, instance_id, permissions):
        """Add additional users and groups to the permissions

        Args:
            instance_type (str): Name of the type (project, batch)
            instance_id (int): ID of the project or batch
            permissions (dict): Dictionary with keys 'users' and 'groups' for lists of ids

        Returns:
            dict: representation of the updated permissions
        """
        url = self._get_url(instance_type, instance_id)
        response = self._post(url, permissions)
        return response.json()

    def replace(self, instance_type, instance_id, permissions):
        """Replace the permissions

        Args:
            instance_type (str): Name of the type (project, batch)
            instance_id (int): ID of the project or batch
            permissions (dict): Dictionary with keys 'users' and 'groups' for lists of ids

        Returns:
            dict: representation of the updated permissions
        """
        url = self._get_url(instance_type, instance_id)
        response = self._put(url, permissions)
        return response.json()
