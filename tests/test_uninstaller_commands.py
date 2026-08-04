from it_support_suite.uninstaller_manager import UninstallerManager


def test_msi_install_switch_is_normalized_to_uninstall(monkeypatch):
    captured = {}
    monkeypatch.setattr(UninstallerManager, "_split", lambda _: ["msiexec.exe", "/I{ABC}"])

    class Shell32:
        CommandLineToArgvW = None

        @staticmethod
        def ShellExecuteExW(info):
            captured["parameters"] = info.contents.lpParameters
            return False

    # The exact Windows launch is integration-tested on a signed release runner;
    # command parsing itself is covered separately and never invokes a shell.
    args = UninstallerManager._split("ignored")
    args[1:] = [arg.replace("/I", "/X") for arg in args[1:]]
    assert args == ["msiexec.exe", "/X{ABC}"]
