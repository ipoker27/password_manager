# Password Manager

## Project Structure

~~~text
password_manager/
├── main.py
├── README.md
├── requirements.txt
└── password_manager/
    ├── passwords/
    │   └── vault.json
    └── manager.py
~~~

## Install Dependencies

~~~bash
pip install -r requirements.txt
~~~

## Usage

### Initialize Vault

Create a new encrypted vault protected by a master passphrase.

The master passphrase is used to derive the encryption key and is required to decrypt the stored credentials.

Important: Losing the master passphrase means losing access to the encrypted data.

### Add a New Entry

Select New Entry and provide the following information:

Service: Name of the website or application

URL: Website address

Username: Account username or email

Password: Account password

After submission, the application encrypts the updated vault.

### List Entries

Select List Entries and enter your master passphrase.

The application decrypts the vault and displays saved entries in a scrollable interface.

Each entry displays its service name, username, and URL.

### Retrieve Password

Select the password action for a saved service and provide the master passphrase when prompted.

The application decrypts the vault and retrieves the requested password.

The retrieved password will be automatically copied to clipboard.