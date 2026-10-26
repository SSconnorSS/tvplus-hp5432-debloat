# Kurulum ve kontrol — HP5432

Örnekler Windows PowerShell içindir. Profil aracı Python 3.11+ standart kütüphanesini kullanır. Denenen firmware [README](../README.md) ve [profile.json](../profiles/hp5432/profile.json) içinde belirtilmiştir. Komutları bir bütün olarak körlemesine çalıştırma; her bölümün sonucunu kontrol et.

## 1. Yetki, araçlar ve başlangıç kaydı

Önce [kapsam ve hizmet koşullarını](SCOPE.md) incele. Kendi cihazının model/yazılımını karşılaştır. Başka bir profil, firmware veya kiralık/tahsis edilmiş kutu için yetki varsayılmaz.

ADB için yalnız [Google Platform Tools](https://developer.android.com/tools/releases/platform-tools), Git ve Python için resmî dağıtımları kullan. Launcher derlenecekse JDK 17, Android SDK platform 34 ve build-tools 34.0.0 gerekir; [upstream derleme bilgileri](https://github.com/Gathin23/cleanyourtv/tree/f592b6d2db0cfa0e28779660f25ff65386a5ff9b#the-launcher) takip edilmeli.

Geliştirici seçeneklerini cihazın normal yöntemiyle aç. Denenen kutuda Android TV OS derlemesine yedi kez basmak başlangıçta sonuç vermedi; her HP5432 için bu yolun çalıştığı iddia edilmez. Bu kutuda Google Play'deki [Developer Tools — Roy Solberg](https://play.google.com/store/apps/details?id=com.roysolberg.android.developertools) uygulamasının geliştirici ayarları kısayolu kullanıldı. Uygulamadan normal geliştirici ayarları sayfasını aç; sunuluyorsa **Geliştirici seçeneklerini etkinleştir** anahtarını aç. Sonra aynı sistem ekranındaki USB/kablosuz hata ayıklama seçeneğini kullan ve kendi bilgisayarın için TV'deki normal izin istemini onayla. Menü erişilemez veya cihaz bu izni reddederse bu adımda dur; bu kısayolun her kutuda çalıştığı varsayılmaz. Fabrika/test menülerini kullanma. OEM kilit açma, root veya bootloader değişikliği bu kurulumun parçası değildir.

USB veya kablosuz hata ayıklamayı normal menüden açıp kendi bilgisayarını TV ekranında yetkilendir. Aynı yerel ağda, ekranda gördüğün güncel hedefi kullan:

```powershell
$TvEndpoint = Read-Host 'Kutunun ADB hedefi (IP:port veya USB hedefi)'
adb connect $TvEndpoint
adb devices
python tools/profile.py --device $TvEndpoint --save
```

`adb connect` yalnız ağ bağlantısı içindir; USB hedefinde gerekmez. Profil aracı bağlantıyı kendisi açmaz. Model, cihaz kodu, Android, SDK, tam fingerprint veya derleme uyuşmazsa durur. Kullanıcı 0 dışında paket okuması yapmaz.

`.local/` içindeki kayıt yalnız altı paketin başlangıç durumunu içerir; tam cihaz/uygulama yedeği değildir. Ayrıca mevcut Home, erişilebilirlik ve değiştirmeyi düşündüğün gizlilik ayarlarını **özel yerel kayıtlarında** sakla. Sonradan farklılaşan değerlerin üzerine yazma.

## 2. Paketleri ayrı değerlendir

[PACKAGES.md](../profiles/hp5432/PACKAGES.md) her paketin işlevini ve etkilenebilecek özelliklerini açıklar. Varsayılan seçili paket yoktur. Sağlayıcı yönetim paketleri uzaktan destek ve provizyonu etkileyebilir; kısa yayın testinin geçmesi tüm gelecek senaryoları doğrulamaz.

Örneğin yalnız geri bildirim bileşeni için, gözlenen başlangıç durumundan elle uygulanacak komutları üret:

```powershell
python tools/profile.py --device $TvEndpoint --package com.google.android.feedback --show-commands
```

Araç hiçbir komutu uygulamaz. Çıktıdaki `DEVICE_SERIAL` yer tutucusunu kendi yetkilendirilmiş hedefinle değiştir. Önizleme alındığı anda görülen eski ayar değişmiş olabilir; uygulamadan önce tekrar kontrol et. Paketleri tek tek kapat, sonucu kaydet ve temel işlevleri dene. `pm uninstall`, root ve firmware değişimi bu profilin paket yöntemine dahil değildir.

Geri dönüş, test cihazının varsayılanına göre toplu açma şeklinde yapılmamalıdır. Kendi gözlediğin önceki `0`/`1` durumuna göre üretilen satırı ve [geri dönüş rehberini](RECOVERY.md) kullan. Komut önizlemesi uygulanmış veya test edilmiş bir geri alma oturumu değildir; kayıt benzersiz fiziksel kutu kimliği içermez.

## 3. Launcher'ı upstream kaynağından derle

Bu deponun kardeşi olacak ayrı bir klasörde kaynak kopyası oluştur. Denenen sürüm:

```powershell
git clone https://github.com/Gathin23/cleanyourtv.git
git -C cleanyourtv checkout f592b6d2db0cfa0e28779660f25ff65386a5ff9b
```

JDK/SDK yollarını upstream talimatına göre ayarla. `cleanyourtv/launcher` klasöründe:

```powershell
./gradlew.bat --no-daemon testReleaseUnitTest lintRelease assembleRelease
```

Başarılı sonuçtan sonra oluşan `app/build/outputs/apk/release/app-release.apk` dosyasını kendi kutuna kur. Bu depo APK barındırmaz. HP5432'de denenmiş kurulum, upstream'in stok launcher'ı kapatan veya Home rolünü değiştiren genel kurulum yordamını kullanmadı; aşağıdaki yönlendirme düzenini kullandı. `INTERNET` izni bulunmadığını upstream manifesti ve oluşturduğun APK üzerinden kontrol et.

```powershell
adb -s $TvEndpoint install -r --user 0 ./app/build/outputs/apk/release/app-release.apk
adb -s $TvEndpoint shell am start -W -n com.gathin.tvhome/.MainActivity
```

Bu iki komut `cleanyourtv/launcher` içinden çalıştırılır. Kurulum doğrulaması başarısızsa mağaza/cihaz korumalarını kapatarak devam etme. Önceden aynı paket adıyla başka bir imza veya yapı kuruluysa kullanıcı verisini silerek geçiş yapma; imza/kurulum durumunu ayrıca değerlendir.

## 4. Glass ve Home yönlendirmesi

Bu depodaki `themes/glass/` klasörünü kullan. Upstream tema aracının Python ortamını kendi [tools/requirements.txt](https://github.com/Gathin23/cleanyourtv/blob/f592b6d2db0cfa0e28779660f25ff65386a5ff9b/tools/requirements.txt) dosyasından hazırla. Örnek, `cleanyourtv` kaynak klasöründe:

```powershell
python -m venv tools/venv
./tools/venv/Scripts/python.exe -m pip install -r tools/requirements.txt
$TvIp = Read-Host 'Kutunun IP adresi'
$GlassFolder = Read-Host 'Bu projenin themes/glass klasörünün tam yolu'
./tools/theme.ps1 -TvHost $TvIp -Theme $GlassFolder
```

Tema aktarımı dock'u, görünümü ve Home yardımcısını yeniden başlatabilir. Açık uygulamada kaydedilmemiş iş bırakma. Bu kaynak sürümündeki araç için IP ve port ayarları upstream yönergeleriyle eşleşmeli.

**HP5432'de stok `com.google.android.tvlauncher` etkin bırakıldı ve Android'in asıl Home rolünde kaldı.** Stok launcher'ı, setup wizard'ı veya temel kumanda servislerini kapatma. Başlangıçta başka bir launcher varsayılan ise bu profilin aynı koşullarda olmadığı kabul edilmeli; tercihleri kaydetmeden değiştirme.

Normal Ayarlar → Erişilebilirlik bölümünden yalnız CleanYourTV **HomeKeyService** yardımcısını aç. Başka erişilebilirlik hizmetlerini silen bir komut kullanma. InputKeyService, bildirim erişimi, `WRITE_SECURE_SETTINGS` ve konum izni bu profilde gerekli değildi; verilmedi.

Tema `key_filter: true` kullanır. Kısa Home için ek yönlendirme sağlar ve standart Settings/All Apps tuşlarını da ele alır. `consume_volume_keys: false`, boş uygulama tuş eşlemeleri ve `home_long_press_home: false` değerlerini koru. Gerçek kumanda testi zorunludur; ADB ile Home göndermek tek başına kanıt değildir.

`power_on_home: true`, açılışta kendiliğinden gelen `com.skyworth.iptv` penceresine sınırlı süre için yöneliktir; ilk fiziksel kullanıcı tuşu bu pencereyi kapatır. `power_on_home_always: false` bırakıldı. Kullanıcının uygulamaya dönmesini zorla engelleyen genel uyanma yönlendirmesi kullanılmadı.

Üst sırayı kendi kurulu uygulamalarına göre düzenleyebilirsin. `hidden_apps` yalnız görünürlük tercihidir; uygulama kaldırmaz. Tema değişikliği sonrası aynı fiziksel kontrolleri tekrarla.

## 5. İsteğe bağlı gizlilik tercihleri

Kullanım/teşhis, konum ve arka plan Wi-Fi taramasını normal menülerden kendi ihtiyacına göre değerlendir; başlangıç değerlerini sakla. Bluetooth kumandayı çalıştıran bileşenleri koru. Reklam kimliğini silmek eski kimliği geri getirmez; normal sistem ekranındaki açıklamayı oku.

Testte özel DNS olarak `dns.adguard-dns.com` kullanıldı. DNS işletmecisi sorguları işler; [gizlilik açıklaması](https://adguard-dns.io/en/privacy.html) ve [resmî kurulum bilgileri](https://adguard-dns.io/en/public-dns.html) incelenmeli. Mevcut filtre/VPN/DNS tercihini değiştirme kararı ayrıca verilmeli. TV+ açılışını ve yayını yeniden başlatma sonrasında da dene; sorun varsa kayıtlı eski DNS değerlerine dön. Araç otomatik DNS ayarı yapmaz.

SmartTube F-Droid ayrı ve isteğe bağlıdır; uygulama kurulumu veya Google hesabı girişi otomatik yapılmaz. Denenen sürüm 32.68 idi. F-Droid sürümünde geliştiricinin kendi güncelleyicisi yoktur. Harici topluluk servislerini istemiyorsan SponsorBlock, DeArrow'un kitle kaynaklı başlık/küçük resim seçenekleri ve beğeni/beğenmeme sayacını kapat. Bunlar kapalıyken hesap açılmadan tek video oynatma denendi. [Hizmet koşulları notunu](SCOPE.md) incele.

## 6. Fiziksel doğrulama ve iş bitimi

Kumandadan TV+ EV'yi aç, yayın/ses ve kanal değiştirmeyi dene. Home yeni ekrana dönmeli; ses tuşuna basılı tutunca ses kademeli değişmeli. Kapatıp açma ve gerçek yeniden başlatma sonrası aynı kontrolleri tekrarla. Uygulamaların tamamını, tüm yayınları veya güncelleme senaryolarını denemiş sayılmazsın.

Tamamlandıktan sonra bilgisayarın hata ayıklama yetkilerini kaldır, USB/kablosuz/ağ hata ayıklamayı kapat ve normal menüden yeniden başlat. Yetkiyi kaldırınca ADB oturumu kesilebilir; son kapatmayı kumandadan yapmak gerekebilir. Kapalı port testi, TV'nin ağda olduğunun da doğrulanmasıyla birlikte değerlendirilmelidir. Yeniden değişiklik gerekirse normal menüden açıkça yeniden yetkilendir.
