import hashlib
import json
from base64 import b64encode


def sign_request(request_body, api_key):
    # Convert the request body to a compact JSON string
    body_json = json.dumps(request_body).encode()

    # Base64 encode the compact JSON string
    base64_encoded_body = b64encode(body_json).decode()

    # Concatenate the base64-encoded body with the API key
    concatenated = base64_encoded_body + api_key

    # Generate the MD5 hash
    hash_md5 = hashlib.md5(concatenated.encode())

    return hash_md5.hexdigest()
