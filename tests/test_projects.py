import pytest
import vcr

from .config import token, url

from turkle_client.client import Projects
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/projects/',
)


@my_vcr.use_cassette()
def test_batches():
    client = Projects(url, token)
    batches = client.batches(1)
    assert len(batches) == 1
    assert batches[0]['name'] == 'Dickens'

@my_vcr.use_cassette()
def test_retrieve_on_bad_project():
    client = Projects(url, token)
    with pytest.raises(TurkleClientException, match="No Project matches the given query"):
        client.retrieve(99)
