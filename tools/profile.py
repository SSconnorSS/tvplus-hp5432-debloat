#!/usr/bin/env python3
"""HP5432 profilini doğrula; isteğe bağlı olarak bağlı kutuyu yalnızca oku."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import secrets
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "profiles" / "hp5432" / "profile.json"
REVIEWED = {
    "com.google.android.feedback": "google_optional",
    "com.android.ondevicepersonalization.services": "google_optional",
    "com.android.federatedcompute.services": "google_optional",
    "com.sdt.android.tr369": "provider_optional",
    "com.skyworth.android.tr069": "provider_optional",
    "com.sdt.customization": "provider_optional",
}
PROPERTIES = {
    "manufacturer": "ro.product.manufacturer", "model": "ro.product.model",
    "device": "ro.product.device", "android_release": "ro.build.version.release",
    "sdk": "ro.build.version.sdk", "build_fingerprint": "ro.build.fingerprint",
    "build_display_id": "ro.build.display.id",
}


class ProfileError(Exception):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProfileError(message)


def validate_profile(profile: dict) -> dict:
    require(isinstance(profile, dict) and profile.get("schema_version") == 1,
            "Profil şeması desteklenmiyor.")
    require(profile.get("status") == "experimental", "Deneysel durum bilgisi eksik.")
    tested = profile.get("tested", {})
    require(isinstance(tested, dict) and all(isinstance(tested.get(k), str) and tested[k]
            for k in PROPERTIES), "Model/derleme bilgisi eksik.")
    require(tested.get("model") == "HP5432" and type(tested.get("units")) is int and tested["units"] == 1,
            "Bu araç yalnız tek HP5432 üzerinde denenmiş profil içindir.")
    packages = profile.get("packages")
    require(isinstance(packages, list) and len(packages) == len(REVIEWED),
            "İncelenmiş altı paket bulunmalı.")
    names = []
    for item in packages:
        require(isinstance(item, dict), "Paket kaydı geçersiz.")
        name = item.get("name")
        require(name in REVIEWED and item.get("group") == REVIEWED[name],
                "İncelenmemiş paket veya paket grubu reddedildi.")
        require(item.get("default_selected") is False, "Varsayılan paket seçimi yapılamaz.")
        require(type(item.get("original_enabled_setting")) is int
                and item["original_enabled_setting"] in (0, 1)
                and type(item.get("tested_enabled_setting")) is int
                and item["tested_enabled_setting"] == 3,
                "Deneme ayarları beklenen biçimde değil.")
        require(isinstance(item.get("reason_tr"), str) and item["reason_tr"].strip(),
                "Paket gerekçesi eksik.")
        names.append(name)
    require(set(names) == set(REVIEWED), "Paketler eksik veya yinelenmiş.")
    return profile


class Adb:
    """Yalnız sabit okuma komutları; bağlantı kurmaz ve eşleştirme yapmaz."""
    def __init__(self, serial: str, binary: str = "adb"):
        require(bool(re.fullmatch(r"[A-Za-z0-9\[][A-Za-z0-9._:\[\]%-]{0,254}", serial)),
                "Geçersiz cihaz hedefi.")
        self.serial, self.binary = serial, binary

    def _run(self, args: list[str]) -> str:
        try:
            result = subprocess.run([self.binary, "-s", self.serial, *args],
                                    capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=20, shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProfileError("ADB çalıştırılamadı veya okuma zaman aşımına uğradı.") from exc
        require(result.returncode == 0, "ADB okuması başarısız; bağlantı ve TV iznini kontrol et.")
        return result.stdout.strip()

    def ready(self) -> None:
        require(self._run(["get-state"]) == "device", "Cihaz zaten bağlı ve yetkilendirilmiş olmalı.")

    def shell(self, *tokens: str) -> str:
        allowed = (tokens[:1] == ("getprop",) and len(tokens) == 2 and tokens[1] in PROPERTIES.values())
        allowed |= tokens == ("am", "get-current-user")
        allowed |= (tokens[:5] == ("pm", "list", "packages", "--user", "0")
                    and len(tokens) == 6 and tokens[-1] in REVIEWED)
        allowed |= (tokens[:2] == ("dumpsys", "package") and len(tokens) == 3 and tokens[-1] in REVIEWED)
        require(allowed, "Bu araç yalnız incelenmiş okuma komutlarını çalıştırır.")
        return self._run(["shell", shlex.join(tokens)])


def enabled_setting(raw: str, package: str) -> int:
    """Etkin Packages bölümünü oku; gizli fabrika sürümünü ve yinelenen kullanıcıyı reddet."""
    blocks = re.findall(r"^Packages:[ \t]*\r?\n(.*?)(?=^\S|\Z)", raw, re.M | re.S)
    require(len(blocks) == 1, "Etkin paket bölümü tekil değil.")
    require(re.findall(r"^\s+Package \[([^\]]+)\]", blocks[0], re.M) == [package],
            "Etkin paket kaydı uyuşmuyor.")
    users = re.findall(r"^\s*User 0:([^\r\n]*)", blocks[0], re.M)
    require(len(users) == 1 and re.search(r"\binstalled=true\b", users[0]) is not None,
            "Etkin kullanıcı 0 kurulumu doğrulanamadı.")
    values = re.findall(r"\benabled=(\d+)\b", users[0])
    require(len(values) == 1 and values[0] in {"0", "1", "2", "3", "4"},
            "Paketin etkinleştirme ayarı okunamadı.")
    return int(values[0])


def inspect_device(adb: Adb, profile: dict) -> dict:
    validate_profile(profile)
    adb.ready()
    device = {key: adb.shell("getprop", prop) for key, prop in PROPERTIES.items()}
    require(all(device[k] == profile["tested"][k] for k in PROPERTIES),
            "Model/yazılım denenen profille aynı değil; paket okuması durdu.")
    require(adb.shell("am", "get-current-user") == "0", "Etkin kullanıcı 0 değil; işlem durdu.")
    states = {}
    for package in REVIEWED:
        lines = adb.shell("pm", "list", "packages", "--user", "0", package).splitlines()
        require(all(re.fullmatch(r"package:[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+", line)
                    for line in lines), "Paket listesi beklenen biçimde değil.")
        installed = "package:" + package in lines
        states[package] = {"installed": installed, "enabled_setting":
                           enabled_setting(adb.shell("dumpsys", "package", package), package) if installed else None}
    return {"schema_version": 1, "kind": "read_only_inspection",
            "created_at": datetime.now(timezone.utc).isoformat(), "device": device, "packages": states}


def command_preview(snapshot: dict, selected: list[str]) -> list[str]:
    require(bool(selected) and all(p in REVIEWED for p in selected), "İncelenmiş paketleri açıkça seç.")
    output = ["Yalnız metin önizlemesi: hiçbir değişiklik yürütülmedi.",
              "DEVICE_SERIAL yerine kendi hedefini yaz. Sözleşme/yetkiyi kendin değerlendir.",
              "Geri alma satırı gözlenen eski ayardır; uygulanmış veya doğrulanmış bir geri alma değildir."]
    for package in dict.fromkeys(selected):
        state = snapshot["packages"][package]
        before = state["enabled_setting"]
        if not state["installed"] or before not in (0, 1):
            output.append(f"Atlandı: {package} (kurulu değil veya zaten kapalı).")
            continue
        output.extend([f"Kapat: adb -s DEVICE_SERIAL shell pm disable-user --user 0 {package}",
                       f"Eski ayar: adb -s DEVICE_SERIAL shell pm {'default-state' if before == 0 else 'enable'} --user 0 {package}"])
    return output


def save_snapshot(snapshot: dict) -> Path:
    directory = ROOT / ".local"
    require(directory.resolve() == ROOT.resolve() / ".local", "Yerel kayıt dizini başka bir konuma yönleniyor.")
    directory.mkdir(exist_ok=True)
    target = directory / ("inspection-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                          + "-" + secrets.token_hex(3) + ".json")
    # Keep the privacy boundary even if a future caller adds other fields.
    safe = {"schema_version": 1, "kind": "read_only_inspection",
            "created_at": snapshot["created_at"],
            "device": {key: snapshot["device"][key] for key in PROPERTIES},
            "packages": {name: {key: snapshot["packages"][name][key]
                                for key in ("installed", "enabled_setting")} for name in REVIEWED}}
    with target.open("x", encoding="utf-8") as stream:
        json.dump(safe, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--device", help="Zaten bağlı ve izinli ADB hedefi; otomatik bağlanılmaz.")
    parser.add_argument("--adb", default="adb", help="Resmî Platform Tools içindeki ADB yolu.")
    parser.add_argument("--show-commands", action="store_true", help="Yalnız seçilen paketler için manuel komut metni yaz.")
    parser.add_argument("--package", action="append", default=[], choices=sorted(REVIEWED))
    parser.add_argument("--save", action="store_true", help="Okunan sınırlı bilgiyi yalnız .local/ içine kaydet.")
    args = parser.parse_args(argv)
    try:
        require(not args.show_commands or bool(args.device and args.package),
                "--show-commands için --device ve en az bir --package gerekir.")
        require(not args.package or args.show_commands, "--package yalnız --show-commands ile kullanılır.")
        require(not args.save or bool(args.device), "--save için --device gerekir.")
        profile = validate_profile(json.loads(args.profile.read_text(encoding="utf-8")))
        print("HP5432 deneysel profili doğrulandı: tek cihaz, aynı gün testi; altı isteğe bağlı paket.")
        if not args.device:
            print("Cihaza bağlanılmadı. Hiçbir paket seçilmedi ve ayar değiştirilmedi.")
            return 0
        snapshot = inspect_device(Adb(args.device, args.adb), profile)
        print("Model/yazılım ve kullanıcı 0 doğrulandı. Yalnız altı paket okundu.")
        for package, state in snapshot["packages"].items():
            print(f"{package}: " + (f"enabled={state['enabled_setting']}" if state["installed"] else "kurulu değil"))
        if args.show_commands:
            print("\n".join(command_preview(snapshot, args.package)))
        if args.save:
            print("Yerel kayıt: .local/" + save_snapshot(snapshot).name + " — herkese açık paylaşma.")
        return 0
    except (ProfileError, OSError, ValueError, TypeError, KeyError) as exc:
        print("Durdu: " + (str(exc) if isinstance(exc, ProfileError) else "Yerel profil veya kayıt okunamadı."), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
