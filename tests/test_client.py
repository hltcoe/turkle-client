import pytest
import vcr

from turkle_client.client import Client
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/client/',
)


@my_vcr.use_cassette()
def test_bad_token():
    client = Client("http://localhost:8000/", "bad_token")
    with pytest.raises(TurkleClientException, match="Invalid token"):
        client._get("http://localhost:8000/api/users/")


@my_vcr.use_cassette()
def test_404():
    client = Client("http://localhost:8000/", "41dcbb22264dd60c5232383fc844dbbab4839146")
    with pytest.raises(TurkleClientException, match="Not found"):
        client._get("http://localhost:8000/api/users/999999/")
