import pytest
import vcr

from .config import token, url

from turkle_client.client import Permissions
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/permissions/',
)


@my_vcr.use_cassette()
def test_retrieve():
    client = Permissions(url, token)
    perms = client.retrieve("project", 1)
    assert len(perms) == 2
    assert len(perms['users']) == 0
    assert len(perms['groups']) == 2

def test_retrieve_on_bad_type():
    client = Permissions(url, token)
    with pytest.raises(TurkleClientException, match="Unrecognized instance type: projects"):
        client.retrieve("projects", 1)

@my_vcr.use_cassette()
def test_retrieve_on_bad_id():
    client = Permissions(url, token)
    with pytest.raises(TurkleClientException, match="No Project matches the given query"):
        client.retrieve("project", 999)

@my_vcr.use_cassette()
def test_retrieve_for_empty_permissions():
    client = Permissions(url, token)
    perms = client.retrieve("batch", 1)
    assert len(perms) == 2
    assert len(perms['users']) == 0
    assert len(perms['groups']) == 0

@my_vcr.use_cassette()
def test_add():
    client = Permissions(url, token)
    perms = client.add("project", 1, {
        'users': [3, 4],
        'groups': [1]
    })
    assert len(perms) == 2
    assert len(perms['users']) == 2
    assert len(perms['groups']) == 3
    # return to starting permissions
    client.replace("project", 1, {
        'users': [],
        'groups': [2, 3]
    })

@my_vcr.use_cassette()
def test_replace():
    client = Permissions(url, token)
    perms = client.replace("project", 1, {
        'users': [3, 4],
        'groups': [2]
    })
    assert len(perms) == 2
    assert len(perms['users']) == 2
    assert len(perms['groups']) == 1
    # return to starting permissions
    client.replace("project", 1, {
        'users': [],
        'groups': [2, 3]
    })
