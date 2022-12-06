import pytest
import vcr

from turkle_client.client import Users

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes',
)


@my_vcr.use_cassette()
def test_retrieve_user():
    client = Users("http://localhost:8000/", "858cac69a52c1f7846571d0d81d397e792d35888")
    text = client.retrieve(1)
    assert 'AnonymousUser' in text


@my_vcr.use_cassette()
def test_retrieve_invalid_user():
    client = Users("http://localhost:8000/", "858cac69a52c1f7846571d0d81d397e792d35888")
    with pytest.raises(ValueError, match="Not found"):
        client.retrieve(999)
