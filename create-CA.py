import datetime
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from cryptography.x509.oid import NameOID

# script setting

CA_NAME = u'Simple Test CA'
CA_ORGANIZATION = u'Organization'
CA_COUNTRY_NAME = u'US'
VALID_TO = 'Jun 1 2020  1:33PM'
PATH = '/tmp/'

def main(args):
    valid_to = datetime.datetime.strptime(VALID_TO, '%b %d %Y %I:%M%p')

    one_day = datetime.timedelta(days=1)
    today = datetime.date.today()

    today_minus_one = today - one_day
    yesterday = datetime.datetime(today_minus_one.year, today_minus_one.month, today_minus_one.day)

    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
    )

    ca_name = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, CA_NAME),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, CA_ORGANIZATION),
    x509.NameAttribute(NameOID.COUNTRY_NAME, CA_COUNTRY_NAME)
    ])

    # CA CREATION
    public_key = private_key.public_key()
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(ca_name)
    builder = builder.issuer_name(ca_name)
    builder = builder.not_valid_before(yesterday)
    builder = builder.not_valid_after(valid_to)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
    x509.BasicConstraints(ca=True, path_length=None),
    critical=True)
    certificate = builder.sign(
    private_key=private_key, algorithm=hashes.SHA256(),
    backend=default_backend()
    )
    private_bytes = private_key.private_bytes(encoding = serialization.Encoding.PEM, format = serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm = serialization.NoEncryption())
    public_bytes = certificate.public_bytes(encoding = serialization.Encoding.PEM)

    with open(PATH + "caa_ca.pem", "wb") as fout: 
        fout.write(private_bytes + public_bytes)

    with open(PATH + "caa_ca.crt", "wb") as fout:
        fout.write(public_bytes)
    
    # SIGNED CERT CREATION
    service_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
    )

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, 'service.test.local')
    ]))
    builder = builder.issuer_name(ca_name)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(yesterday)
    builder = builder.not_valid_after(valid_to)
    builder = builder.public_key(public_key)
    certificate = builder.sign(
    private_key=private_key, algorithm=hashes.SHA256(),
    backend=default_backend()
    )
    private_bytes = service_private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption())
    public_bytes = certificate.public_bytes(
    encoding=serialization.Encoding.PEM)

    with open(PATH + "caa_service.pem", "wb") as fout:
        fout.write(private_bytes + public_bytes)

if __name__ == "__main__":
    main(sys.argv[1:])