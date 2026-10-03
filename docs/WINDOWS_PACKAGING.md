# Windows packaging

The verified Windows packaging path uses the official PySide6 deployment model
with Nuitka and the Microsoft v143 compiler toolchain.

## Pinned build environment

- Python 3.13
- PySide6 6.11.2
- Nuitka 4.2.2
- Visual Studio 2022 Build Tools 17.14 or newer
- MSVC v143 x64/x86 tools
- Windows SDK

## Build modes

Run `tools/build_windows_nuitka.py` from an x64 Visual Studio developer command
environment.

The troubleshooting build keeps a console:

```text
python tools/build_windows_nuitka.py <destination> --console
```

The normal user build hides the console:

```text
python tools/build_windows_nuitka.py <destination>
```

The resulting executable is `windows_entry.dist/EmberVaultControlCenter.exe`.

## Verification boundary

Do not distribute a bundle until the executable has been launched from outside
the source repository with `--smoke-test` and exits with code 0. The smoke test
loads the QML shell and verifies the packaged seed inventory, including the
module and knowledge counts enforced by the application.

The troubleshooting build should be retained for diagnosing QML, Qt plugin,
module discovery, and startup failures. The user build should be tested from a
clean temporary directory before release.
