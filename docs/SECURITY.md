# Security policy

Report suspected vulnerabilities privately to `[SECURITY EMAIL]`. Include the
affected version, reproduction steps, impact, and relevant sanitized logs. Do
not include customer backups, passwords, or personal data.

Supported commercial releases receive security fixes according to the signed
support agreement. Release executables must be Authenticode-signed and published
with SHA-256 checksums. Never distribute signing certificates or passwords with
the source tree or build artifacts.

Privileged changes require an explicit UAC prompt. Backup extraction rejects
paths escaping the selected temporary directory. Encrypted backups authenticate
content and reject wrong passwords or modified ciphertext.
