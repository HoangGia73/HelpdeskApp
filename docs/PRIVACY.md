# Privacy and data handling

IT Support Tool Suite operates locally and does not intentionally transmit
telemetry. It can read and copy user documents, browser profiles, Outlook data,
driver packages, installed-application metadata, and local-network device data
when the operator selects those functions.

Application logs are stored under
`%LOCALAPPDATA%\ITSupportToolSuite\logs`, rotate at 2 MB, and retain five old
files. Logs must not contain backup passwords or file contents. Operators should
review logs before sending them to support because paths and device names may be
personal data.

Encrypted `.itsbackup` files use AES-256-GCM with a key derived from the user's
password using scrypt. Passwords are not stored and cannot be recovered by the
publisher. Losing the password permanently prevents recovery.

The customer determines the lawful basis, retention period, destination, access
controls, and deletion policy for backups and logs. Complete publisher identity,
support contact, jurisdiction-specific rights, and processor/subprocessor terms
before release.
