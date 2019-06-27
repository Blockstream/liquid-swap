import json
import base64

from liquidswap.exceptions import (
    MissingValueError,
    UnexpectedValueError,
)


def encode_payload(payload):
    """
    Encode a payload (python dictionary or list) into JSON and then into
    base64 for transmission over the wire. Return a string.
    """

    json_data = json.dumps(payload)
    data_bytes = bytes(json_data, 'utf-8')
    encoded_bytes = base64.encodebytes(data_bytes)
    encoded_payload = str(encoded_bytes, 'utf-8')

    return encoded_payload


def decode_payload(encoded_payload):
    """
    Decode a payload from utf-8 str/bytes base64 of json data. Return a python
    dictionary or list.
    """

    if not encoded_payload:
        raise MissingValueError('Empty payload')

    if isinstance(encoded_payload, str):
        data_bytes = bytes(encoded_payload, 'utf-8')
    elif isinstance(encoded_payload, bytes):
        data_bytes = encoded_payload
    else:
        raise UnexpectedValueError('Unknown type {}'.format(
            type(encoded_payload)))

    decoded_bytes = base64.decodebytes(data_bytes)
    decoded_string = str(decoded_bytes, 'utf-8')
    decoded_payload = json.loads(decoded_string)

    return decoded_payload
