import pytest
import vcr

from .config import token, url

from turkle_client.client import ClientBase
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/client/',
)


@my_vcr.use_cassette()
def test_bad_token():
    client = ClientBase(url, "bad_token")
    with pytest.raises(TurkleClientException, match="Invalid token"):
        client._get("http://localhost:8000/api/users/")


@my_vcr.use_cassette()
def test_404():
    client = ClientBase(url, token)
    with pytest.raises(TurkleClientException, match="No User matches the given query"):
        client._get("http://localhost:8000/api/users/999999/")
