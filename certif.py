from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime



class Certif:
    def generate_ca():
        # Generate the root CA private key
        root_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate the root CA certificate
        root_cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .serial_number(x509.random_serial_number())
            .public_key(root_key.public_key())
            .sign(root_key, hashes.SHA256(), default_backend())
        )

        # Save the root CA private key
        with open("key/ca.key", "wb") as key_file:
            key_file.write(root_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the root CA certificate
        with open("key/cacert.pem", "wb") as cert_file:
            cert_file.write(root_cert.public_bytes(serialization.Encoding.PEM))

    def user_add_policy():
        # Generate a user key pair
        user_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate a signing request for the user
        user_req = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"User")]))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .sign(user_key, hashes.SHA256(), default_backend())
        )

        # Save the user key pair
        with open("key/user.key", "wb") as key_file:
            key_file.write(user_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the user signing request
        with open("key/user.req", "wb") as req_file:
            req_file.write(user_req.public_bytes(serialization.Encoding.PEM))

    def ca_sign_user_request():
        # Load the CA private key
        with open("key/ca.key", "rb") as key_file:
            ca_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        # Load the user signing request
        with open("key/user.req", "rb") as req_file:
            user_req = x509.load_pem_x509_csr(req_file.read(), default_backend())

        # Sign the user request
        user_cert = (
            x509.CertificateBuilder()
            .subject_name(user_req.subject)
            .issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .public_key(user_req.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .sign(ca_key, hashes.SHA256(), default_backend())
        )

        # Save the signed user certificate
        with open("key/user.pem", "wb") as cert_file:
            cert_file.write(user_cert.public_bytes(serialization.Encoding.PEM))

    # # Add other functions as needed

    # if __name__ == "__main__":
    #     generate_ca()
    #     user_add_policy()
    #     ca_sign_user_request()
    #     # Add calls to other functions as needed
