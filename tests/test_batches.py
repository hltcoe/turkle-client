import pytest
import vcr

from .config import token, url

from turkle_client.client import Batches
from turkle_client.exceptions import TurkleClientException

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes/batches/',
)


@my_vcr.use_cassette()
def test_retrieve_on_bad_project():
    client = Batches(url, token)
    with pytest.raises(TurkleClientException, match="No Batch matches the given query"):
        client.retrieve(99)

@my_vcr.use_cassette()
def test_update_with_not_allowed_csv():
    client = Batches(url, token)
    with pytest.raises(TurkleClientException, match="Cannot update the csv data using update. Use addtasks"):
        client.update({'id': 1, 'csv_text': 'test,test2\n1,2'})
