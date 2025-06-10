import pytest
import vcr

from turkle_client.client import Users

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/users/',
)


@my_vcr.use_cassette()
def test_retrieve():
    client = Users("http://localhost:8000/", "41dcbb22264dd60c5232383fc844dbbab4839146")
    text = client.retrieve(1)
    assert 'AnonymousUser' in text
