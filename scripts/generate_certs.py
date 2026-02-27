
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os
import ipaddress

CERT_DIR = "src/config/security"
os.makedirs(CERT_DIR, exist_ok=True)

def generate_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

def save_key(key, filename):
    with open(os.path.join(CERT_DIR, filename), "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

def save_cert(cert, filename):
    with open(os.path.join(CERT_DIR, filename), "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

def generate_certs():
    print("Generating Root CA...")
    # 1. Root CA
    ca_key = generate_key()
    save_key(ca_key, "ca.key")
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"UHC Agent CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"UHC Agent Root CA"),
    ])
    
    ca_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        ca_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).add_extension(
        x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
                      data_encipherment=False, key_agreement=False, key_cert_sign=True, crl_sign=True,
                      encipher_only=False, decipher_only=False), critical=True,
    ).sign(ca_key, hashes.SHA256())
    
    save_cert(ca_cert, "ca.crt")
    
    print("Generating Server Cert...")
    # 2. Server Cert (localhost)
    server_key = generate_key()
    save_key(server_key, "server.key")
    
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"UHC Agent"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    
    server_cert = x509.CertificateBuilder().subject_name(
        server_subject
    ).issuer_name(
        issuer
    ).public_key(
        server_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost"), x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))]),
        critical=False,
    ).sign(ca_key, hashes.SHA256())
    
    save_cert(server_cert, "server.crt")
    
    print("Generating Client Cert...")
    # 3. Client Cert (for internal agents)
    client_key = generate_key()
    save_key(client_key, "client.key")
    
    client_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"UHC Agent"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"internal-agent"),
    ])
    
    client_cert = x509.CertificateBuilder().subject_name(
        client_subject
    ).issuer_name(
        issuer
    ).public_key(
        client_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).sign(ca_key, hashes.SHA256())
    
    save_cert(client_cert, "client.crt")
    
    print("Certificates generated in src/config/security/")

if __name__ == "__main__":
    generate_certs()
