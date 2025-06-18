import pytest
import vcr

import json

from .config import token, url

from turkle_client.client import Users
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/users/',
)


@my_vcr.use_cassette()
def test_retrieve():
    client = Users(url, token)
    user = client.retrieve(1)
    assert user['username'] == 'AnonymousUser'

@my_vcr.use_cassette()
def test_retrieve_by_username():
    client = Users(url, token)
    user = client.retrieve_by_username("user1")
    assert user['first_name'] == 'Bob'

@my_vcr.use_cassette()
def test_retrieve_by_username_with_bad_username():
    client = Users(url, token)
    with pytest.raises(TurkleClientException, match="No User matches the given query"):
        client.retrieve_by_username("no_user")

@my_vcr.use_cassette()
def test_list():
    client = Users(url, token)
    users = client.list()
    assert len(users) == 6

@my_vcr.use_cassette()
def test_create():
    client = Users(url, token)
    user = client.create({'username': 'user5', 'password': '123456'})
    assert user['username'] == 'user5'

@my_vcr.use_cassette()
def test_update():
    client = Users(url, token)
    user = client.update({'id': 3, 'first_name': 'Craig'})
    assert user['username'] == 'user1'
    assert user['first_name'] == 'Craig'

@my_vcr.use_cassette()
def test_update_on_bad_user():
    client = Users(url, token)
    with pytest.raises(TurkleClientException, match="No User matches the given query"):
        client.update({'id': 99, 'username': 'test'})
