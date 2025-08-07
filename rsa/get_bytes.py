import argparse
import tempfile
import os
import base64
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def main():
    parser = argparse.ArgumentParser(description="Fetch keys via mutual TLS and save decoded binary stream.")
    parser.add_argument("--cert", required=True, help="Path to client certificate PEM file")
    parser.add_argument("--key", required=True, help="Path to client private key PEM file")
    parser.add_argument("--password", default=None, help="Password for encrypted private key (optional)")
    parser.add_argument("--url", required=True, help="URL to request keys from")
    parser.add_argument("--output", default="bin_stream.bin", help="Output file for concatenated binary keys")
    parser.add_argument("--count", default = 10, help = "Number of keys to request")
    args = parser.parse_args()

    # Read private key
    with open(args.key, "rb") as f:
        key_data = f.read()

    password_bytes = args.password.encode() if args.password else None

    private_key = serialization.load_pem_private_key(
        key_data,
        password=password_bytes,
        backend=default_backend()
    )

    # Serialize decrypted or unencrypted private key to temp file (no encryption)
    with tempfile.NamedTemporaryFile("wb", delete=False) as tmp_key_file:
        tmp_key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
        tmp_key_path = tmp_key_file.name

    concatenated_bytes = b""
    number_of_keys = int(args.count)
    try:
        for i in range(number_of_keys):  # fixed 10 requests
            resp = requests.get(args.url, cert=(args.cert, tmp_key_path), verify=False)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("keys", []):
                key_val = item.get("key")
                if key_val:
                    raw_bytes = base64.b64decode(key_val)
                    concatenated_bytes += raw_bytes
                    print(f"[{i+1}] Extracted key: {key_val}")
    finally:
        os.remove(tmp_key_path)

    with open(args.output, "wb") as f:
        f.write(concatenated_bytes)

    print(f"\nWritten {len(concatenated_bytes)} bytes to '{args.output}'")

if __name__ == "__main__":
    main()

