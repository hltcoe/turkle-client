import pytest
import vcr

from turkle_client.client import Client

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/client/',
)


@my_vcr.use_cassette()
def test_bad_token():
    client = Client("http://localhost:8000/", "bad_token")
    with pytest.raises(ValueError, match="Invalid token"):
        client.get("http://localhost:8000/api/users/")


@my_vcr.use_cassette()
def test_404():
    client = Client("http://localhost:8000/", "858cac69a52c1f7846571d0d81d397e792d35888")
    with pytest.raises(ValueError, match="Not found"):
        client.get("http://localhost:8000/api/users/999999/")
