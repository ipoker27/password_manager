import json
import secrets
from os import path

from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


VAULT_PATH = "./password_manager/passwords/vault.json"

def derive_key(length: int, passphrase: str, salt=None, iterations=None, lanes=None, memory_cost=None,) -> tuple[bytes, bytes]:
    """
        Function that derives a key from the given passphrase and returns tuple[key, salt]
        parameters:
            length: length of the key
            passphrase: passphrase
            salt: salt for the key (optional, if not provided a random one will be generated)
            iterations: number of iterations for the key (optional, if not provided 5 will be used)
            lanes: number of lanes for the key (optional, if not provided 4 will be used)
            memory_cost: memory cost for the key (optional, if not provided 65536 will be used)
    """
    #if len(passphrase) < 8:
    #    raise Exception("Passphrase must be at least 8 characters")

    if salt is None:
        salt = secrets.token_bytes(16) # generate salt if it wasn't provided
    if iterations is None:
        iterations = 5
    if lanes is None:
        lanes = 4
    if memory_cost is None:
        memory_cost = 65536

    # encoding the secret
    secret: bytes = passphrase.encode()

    kdf = Argon2id( # construct the KDF
        salt=salt,
        length=length,
        iterations=iterations,
        lanes=lanes,
        memory_cost=memory_cost,
        ad=None,
    )

    # derive the key
    derived_key = kdf.derive(secret)

    return derived_key, salt

def init_vault(passphrase: str):
    """
        Function that initializes an empty vault and encrypts it with a passphrase
    """
    enc_key, salt = derive_key(32, passphrase)
    # generate a random nonce
    nonce = secrets.token_bytes(12)

    aes = AESGCM(enc_key)
    cipher = aes.encrypt(nonce, b"{}", None)

    # initial vault structure
    vault = {
        "version": "1",
        "kdf": {
            "type": "argon2id",
            "salt": salt.hex(),
            "iterations": 5,
            "memory_cost": 65536,
            "lanes": 4
        },
        "cipher": {
            "type": "aes-256-gcm",
            "nonce": nonce.hex()
        },
        "ciphertext": cipher.hex()
    }

    # create vault
    with open(VAULT_PATH, "w") as file:
        json.dump(vault, file, indent=4)

def decrypt_vault(passphrase):
    """
        Function that decrypts the vault
        parameters:
            passphrase: the passphrase
    """
    with open(VAULT_PATH, "r") as file:
        vault = json.load(file)

    salt = bytes.fromhex(vault["kdf"]["salt"]) # take the salt from the metadata
    nonce = bytes.fromhex(vault["cipher"]["nonce"]) # take the nonce from the metadata
    ciphertext = bytes.fromhex(vault["ciphertext"]) # the encrypted service data

    # derive the key
    key, salt = derive_key(32, passphrase, salt, vault["kdf"]["iterations"], vault["kdf"]["lanes"], vault["kdf"]["memory_cost"])

    aes = AESGCM(key)
    try:
        plaintext = aes.decrypt(nonce, ciphertext, None) # decrypt the service data
    except InvalidTag:
        print('Invalid password')
        return

    vault_data = json.loads(plaintext.decode())  # create a json object out of the data

    return vault, vault_data

def encrypt_vault(vault, vault_data, passphrase) -> None:
    """
        Function that encrypts the vault
        parameters:
            vault: the entire json vault with metadata
            vault_data: the vault data
            passphrase: the passphrase
    """
    with open(VAULT_PATH, "w") as file:
        salt = bytes.fromhex(vault["kdf"]["salt"])
        # derive key
        key, salt = derive_key(32, passphrase, salt, vault["kdf"]["iterations"], vault["kdf"]["lanes"], vault["kdf"]["memory_cost"])

        plaintext = json.dumps(vault_data).encode() # serialize the service data

        vault["cipher"]["nonce"] = secrets.token_bytes(12).hex() # generate a new nonce each time we encrypt the vault

        aes = AESGCM(key)
        # encrypt the vault
        ciphertext = aes.encrypt(bytes.fromhex(vault["cipher"]["nonce"]), plaintext, None)
        vault["ciphertext"] = ciphertext.hex() # append the ciphertext
        json.dump(vault, file, indent=4)


def new_entry( passphrase: str, params: dict[str, str]) -> None:
    """
        Function that adds a new entry to the database
        parameters:
            service: service name
            url: url of the service
            username: username
            password: password
            passphrase: passphrase
    """
    # decrypt the vault
    vault, vault_data = decrypt_vault(passphrase)
    # construct the json object of the new entry
    vault_data[params["service"]] = {
        "service": params["service"],
        "url": params["url"],
        "username": params["username"],
        "password": params["password"]
    }

    encrypt_vault(vault, vault_data, passphrase) # encrypt the vault back


def retrieve_password(service: str, passphrase: str) -> str:
    """
        Function that retrieves a password from the database and returns the password
        parameters:
            service: service name
            passphrase: passphrase
    """
    vault, vault_data = decrypt_vault(passphrase) # decrypt the vault
    password = vault_data[service]["password"] # look up the password
    encrypt_vault(vault, vault_data, passphrase) # encrypt the vault back
    return password


def list_entries(passphrase: str) -> list[dict[str, str]]:
    """
        Function that lists all entries in the database and returns a list
    """
    try:
        vault, vault_data = decrypt_vault(passphrase) # decrypt the vault
    except TypeError:
        return

    services: list[dict[str, str]] = list(vault_data.values()) # init a list to  fill in with services

    encrypt_vault(vault, vault_data, passphrase) # encrypt the vault back
    return services


def delete_entry(passphrase: str, service: str) -> None:
    """
        Function that deletes an entry from the database
        parameters:
            service: service name
    """
    vault_meta, vault_data = decrypt_vault(passphrase) # decrypt the vault

    if service in vault_data:
        del vault_data[service] # delete the entry if it's present in the database
        print("Deleted.")
    else:
        print("Service not in vault.")

    encrypt_vault(vault_meta, vault_data, passphrase) # encrypt the vault back
