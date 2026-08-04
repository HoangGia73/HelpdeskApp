# Commercial release procedure

1. Replace publisher/contact placeholders and obtain legal approval of the EULA,
   privacy notice, security policy, third-party notices, and code-signing identity.
2. Create a clean virtual environment and install `requirements-dev.txt`.
3. Set `SIGN_CERT_PATH` and, if necessary, `SIGN_CERT_PASSWORD` in the build
   machine's secret store. Never save these values in the repository.
4. Install Windows SDK `signtool.exe` and Inno Setup 6.
5. Run:

   ```powershell
   .\scripts\release.ps1 -Version 1.2.2 -RequireSignature -CreateInstaller
   ```

6. Verify the Authenticode signer and timestamp on both EXE files, test install,
   launch, backup, restore and uninstall on clean supported Windows VMs.
7. Commit the version and release notes, then create a signed tag from a clean
   tree using `-CreateGitTag`, or let the protected CI release job do so.
8. Publish only signed artifacts together with `SHA256SUMS-vX.Y.Z.txt`.

Unsigned builds are development artifacts and must not be marketed or distributed
as commercial releases.
