import ConfigParser
import pytest
from kinto_signer.serializer import canonical_json
from kinto_signer.signer.local_ecdsa import ECDSASigner
from kinto_http import Client, KintoException
from pytest_testrail.plugin import testrail


@pytest.fixture
def conf():
    config = ConfigParser.ConfigParser()
    config.read('manifest.ini')
    return config


def verify_signatures(client):
    """
    If we get an exception we need to check the HTTP status code. If it's a 401
    it's the result of the collection not existing, otherwise it should be a
    failure
    """
    try:
        dest_col = client.get_collection()
        records = client.get_records(_sort='-last_modified')
        timestamp = client.get_records_timestamp()
        serialized = canonical_json(records, timestamp)
        signature = dest_col['data']['signature']
        with open('pub', 'w') as f:
            f.write(signature['public_key'])
        signer = ECDSASigner(public_key='pub')
        return signer.verify(serialized, signature) is None
    except KintoException as e:
        if e.response.status_code == 401:
            return -1
        return 0


@testrail('C5478')
def test_addons_signatures(env, conf):
    client = Client(
        server_url=conf.get(env, 'server'),
        bucket='blocklists',
        collection='addons'
    )
    response = verify_signatures(client)

    if response != -1:
        assert response
    else:
        pytest.skip('Addons collection does not exist')


@testrail('C5475')
def test_plugins_signatures(env, conf):
    client = Client(
        server_url=conf.get(env, 'server'),
        bucket='blocklists',
        collection='plugins'
    )
    response = verify_signatures(client)

    if response != -1:
        assert response
    else:
        pass


@testrail('C5476')
def test_gfx_signatures(env, conf):
    client = Client(
        server_url=conf.get(env, 'server'),
        bucket='blocklists',
        collection='gfx'
    )
    response = verify_signatures(client)

    if response != -1:
        assert response
    else:
        pass


@testrail('C5477')
def test_certificates_signatures(env, conf):
    client = Client(
        server_url=conf.get(env, 'server'),
        bucket='blocklists',
        collection='certificates'
    )
    response = verify_signatures(client)

    if response != -1:
        assert response
    else:
        pass
