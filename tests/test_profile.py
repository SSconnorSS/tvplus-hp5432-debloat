import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("hp5432_profile", Path(__file__).resolve().parents[1] / "tools/profile.py")
profile_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile_tool)


def fixture():
    return {"schema_version": 1, "status": "experimental", "tested": {
        "date": "2026-10-26", "units": 1, "manufacturer": "SkyworthDigital", "model": "HP5432",
        "device": "HP4CD-TVplus", "android_release": "14", "sdk": "34",
        "build_fingerprint": "TVplus/HP5432-TVplus/HP4CD-TVplus:14/UKG3.250826.001/P01.02.079_20260612:user/release-keys",
        "build_display_id": "UKG3.250826.001.P01.02.079_20260612"}, "packages": [
            {"name": name, "group": group, "reason_tr": "İncelenmiş isteğe bağlı bileşen.",
             "original_enabled_setting": 0, "tested_enabled_setting": 3, "default_selected": False}
            for name, group in profile_tool.REVIEWED.items()]}


def package_dump(package, setting=0):
    return (f"Packages:\n  Package [{package}] (active):\n    versionCode=1\n"
            f"    User 0: installed=true enabled={setting}\n\n"
            f"Hidden system packages:\n  Package [{package}] (factory):\n"
            "    User 0: installed=true enabled=0\n")


class FakeAdb:
    def __init__(self, *, model="HP5432", absent=None, user="0"):
        self.calls, self.model, self.absent, self.user = [], model, absent, user

    def ready(self):
        self.calls.append(("get-state",))

    def shell(self, *tokens):
        self.calls.append(tokens)
        if tokens[0] == "getprop":
            key = next(k for k, v in profile_tool.PROPERTIES.items() if v == tokens[1])
            return self.model if key == "model" else fixture()["tested"][key]
        if tokens == ("am", "get-current-user"):
            return self.user
        package = tokens[-1]
        if tokens[:3] == ("pm", "list", "packages"):
            return "" if package == self.absent else "package:" + package
        if tokens[:2] == ("dumpsys", "package"):
            return package_dump(package)
        raise AssertionError("Unexpected or mutating ADB call")


class ProfileTests(unittest.TestCase):
    def test_wrong_device_stops_before_any_package_reads(self):
        adb = FakeAdb(model="ANOTHER-TV")
        with self.assertRaises(profile_tool.ProfileError):
            profile_tool.inspect_device(adb, fixture())
        self.assertFalse(any(c[0] in {"pm", "dumpsys"} for c in adb.calls))

    def test_nonzero_user_stops_before_package_reads(self):
        adb = FakeAdb(user="10")
        with self.assertRaises(profile_tool.ProfileError):
            profile_tool.inspect_device(adb, fixture())
        self.assertFalse(any(c[0] in {"pm", "dumpsys"} for c in adb.calls))

    def test_unreviewed_system_target_is_rejected(self):
        data = fixture()
        data["packages"][0]["name"] = "com.android.systemui"
        with self.assertRaises(profile_tool.ProfileError):
            profile_tool.validate_profile(data)
        with self.assertRaises(profile_tool.ProfileError):
            profile_tool.Adb("example-device").shell("pm", "disable-user", "--user", "0", "com.android.systemui")

    def test_active_state_ignores_hidden_factory_copy_and_rejects_ambiguity(self):
        name = "com.google.android.feedback"
        self.assertEqual(profile_tool.enabled_setting(package_dump(name, 1), name), 1)
        ambiguous = package_dump(name).replace("    versionCode=1", "    User 0: installed=true enabled=1\n    versionCode=1")
        with self.assertRaises(profile_tool.ProfileError):
            profile_tool.enabled_setting(ambiguous, name)

    def test_retained_data_stub_is_absent_when_installed_list_omits_it(self):
        name = "com.google.android.feedback"
        adb = FakeAdb(absent=name)
        result = profile_tool.inspect_device(adb, fixture())
        self.assertEqual(result["packages"][name], {"installed": False, "enabled_setting": None})
        self.assertNotIn(("dumpsys", "package", name), adb.calls)

    def test_preview_restores_exact_default_or_explicit_enable_and_skips_disabled(self):
        names = list(profile_tool.REVIEWED)[:3]
        snapshot = {"packages": {name: {"installed": True, "enabled_setting": before}
                                 for name, before in zip(names, (0, 1, 3))}}
        output = "\n".join(profile_tool.command_preview(snapshot, names))
        self.assertIn("pm default-state --user 0 " + names[0], output)
        self.assertIn("pm enable --user 0 " + names[1], output)
        self.assertNotIn("pm disable-user --user 0 " + names[2], output)
        with self.assertRaises(profile_tool.ProfileError):
            profile_tool.command_preview(snapshot, ["com.android.systemui"])

    def test_default_cli_never_creates_an_adb_client(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(fixture()), encoding="utf-8")
            with patch.object(profile_tool, "DEFAULT_PROFILE", path), patch.object(profile_tool, "Adb") as adb:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(profile_tool.main([]), 0)
                adb.assert_not_called()

    def test_preview_requires_both_connected_target_and_explicit_selection(self):
        for arguments in (["--show-commands"], ["--show-commands", "--device", "example-device"]):
            with patch.object(profile_tool, "Adb") as adb, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(profile_tool.main(arguments), 2)
                adb.assert_not_called()

    def test_subprocess_allowlist_reads_only_and_does_not_expose_stderr(self):
        calls = []
        def run(args, **kwargs):
            calls.append((args, kwargs))
            if args[-1] == "get-state":
                stdout = "device\n"
            else:
                tokens = args[-1].split()
                stdout = FakeAdb().shell(*tokens)
            return type("Result", (), {"returncode": 0, "stdout": stdout})()
        with patch.object(profile_tool.subprocess, "run", side_effect=run):
            result = profile_tool.inspect_device(profile_tool.Adb("example-device"), fixture())
        self.assertEqual(len(result["packages"]), 6)
        self.assertNotIn("serial", json.dumps(result))
        self.assertNotIn("example-device", json.dumps(result))
        for args, options in calls:
            self.assertFalse(options["shell"])
            self.assertLessEqual(options["timeout"], 20)
            self.assertNotIn("connect", args)
            self.assertNotIn("pair", args)
            self.assertNotIn("disable-user", args[-1])
        with patch.object(profile_tool.subprocess, "run", return_value=type("Result", (), {
                "returncode": 1, "stdout": "", "stderr": "secret-raw-endpoint"})()):
            with self.assertRaises(profile_tool.ProfileError) as error:
                profile_tool.Adb("example-device").ready()
            self.assertNotIn("secret-raw-endpoint", str(error.exception))

    def test_saved_snapshot_excludes_unexpected_private_fields_and_never_overwrites(self):
        snapshot = profile_tool.inspect_device(FakeAdb(), fixture())
        snapshot.update(endpoint="private-endpoint", serial="private-serial")
        snapshot["device"]["mac"] = "private-mac"
        snapshot["packages"]["org.private.application"] = {"installed": True}
        with tempfile.TemporaryDirectory() as directory, patch.object(profile_tool, "ROOT", Path(directory)):
            first = profile_tool.save_snapshot(snapshot)
            original = first.read_bytes()
            saved = json.loads(original)
            self.assertEqual(set(saved["device"]), set(profile_tool.PROPERTIES))
            self.assertEqual(set(saved["packages"]), set(profile_tool.REVIEWED))
            self.assertNotIn("private-", original.decode())
            with patch.object(profile_tool, "datetime") as clock, patch.object(profile_tool.secrets, "token_hex", return_value="fixed"):
                clock.now.return_value.strftime.return_value = "fixed-time"
                profile_tool.save_snapshot(snapshot)
                with self.assertRaises(FileExistsError):
                    profile_tool.save_snapshot(snapshot)
            self.assertEqual(first.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
