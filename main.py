import base64
import argparse
from datetime import datetime, timedelta, UTC
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

def build_name(args):
    attributes = []
    if args.C: attributes.append(x509.NameAttribute(NameOID.COUNTRY_NAME, args.C))
    if args.ST: attributes.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, args.ST))
    if args.L: attributes.append(x509.NameAttribute(NameOID.LOCALITY_NAME, args.L))
    if args.O: attributes.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, args.O))
    if args.OU: attributes.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, args.OU))
    if args.CN: attributes.append(x509.NameAttribute(NameOID.COMMON_NAME, args.CN))
    if not attributes:
        raise ValueError("At least one subject/issuer attribute (like --CN) must be provided")
    return x509.Name(attributes)

def generate_cert(private_key, public_key, filename_prefix, subject, is_ed25519=False):
    builder = x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(public_key).serial_number(
        x509.random_serial_number()).not_valid_before(datetime.now(UTC)).not_valid_after(datetime.now(UTC) + timedelta(days=365))
    certificate = builder.sign(
        private_key=private_key,
        algorithm=None if is_ed25519 else hashes.SHA256(),
        backend=default_backend()
    )

    with open(f"{filename_prefix}_cert.pem", "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
    with open(f"{filename_prefix}_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"Saved {filename_prefix}_cert.pem and {filename_prefix}_key.pem")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate Ed25519 X.509 cert from QKD keys")

    parser.add_argument('--key', action='append', required=True, help="Base64-encoded QKD key (can be used multiple times)")
    parser.add_argument('--prefix', default='qkd_ed25519', help="Filename prefix for cert and key")

    # Subject/issuer fields
    parser.add_argument('--C', help="Country Name (e.g., RO)")
    parser.add_argument('--ST', help="State or Province Name")
    parser.add_argument('--L', help="Locality Name")
    parser.add_argument('--O', help="Organization Name")
    parser.add_argument('--OU', help="Organizational Unit Name")
    parser.add_argument('--CN', help="Common Name")

    args = parser.parse_args()

    # Build subject/issuer name
    subject = build_name(args)

    # Decode and combine QKD entropy
    entropy = b''.join(base64.b64decode(k) for k in args.key)
    if len(entropy) < 32:
        raise ValueError("Not enough entropy: need at least 32 bytes from QKD keys")

    ed25519_seed = entropy[:32]
    ed25519_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(ed25519_seed)

    generate_cert(ed25519_private_key, ed25519_private_key.public_key(), args.prefix, subject, is_ed25519=True)
