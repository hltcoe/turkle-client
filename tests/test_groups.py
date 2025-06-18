import pytest
import vcr

import json

from .config import token, url

from turkle_client.client import Groups
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/groups/',
)


@my_vcr.use_cassette()
def test_retrieve():
    # Turkle creates an admin group on installation so 2 = Group1
    client = Groups(url, token)
    text = client.retrieve(2)
    assert 'Group1' in text

@my_vcr.use_cassette()
def test_retrieve_by_name():
    client = Groups(url, token)
    text = client.retrieve_by_name("Group1")
    groups = json.loads(text)
    assert len(groups) == 1
    assert groups[0]['name'] == "Group1"

@my_vcr.use_cassette()
def test_retrieve_on_bad_group():
    client = Groups(url, token)
    with pytest.raises(TurkleClientException, match="No Group matches the given query"):
        client.retrieve(99)

@my_vcr.use_cassette()
def test_add_users():
    client = Groups(url, token)
    text = client.addusers(2, [5, 6])
    group = json.loads(text)
    assert len(group['users']) == 4
