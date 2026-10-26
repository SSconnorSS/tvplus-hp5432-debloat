# İncelenen paketler

Bu liste tek HP5432 ve `UKG3.250826.001.P01.02.079_20260612` derlemesindeki aynı gün testini kaydeder. Paket adı, bir bileşenin kötü amaçlı olduğu veya tüm işlevlerinin gereksiz olduğu anlamına gelmez. Her satır ayrıca seçilmelidir.

| Paket | İşlev / kaybedilebilecek özellik |
|---|---|
| `com.google.android.feedback` | Google geri bildirim gönderimi |
| `com.android.ondevicepersonalization.services` | İsteğe bağlı cihaz içi kişiselleştirme |
| `com.android.federatedcompute.services` | İsteğe bağlı dağıtık hesaplama |
| `com.sdt.android.tr369` | Sağlayıcı uzaktan yönetim ve destek |
| `com.skyworth.android.tr069` | Sağlayıcı yapılandırma ve yönetim |
| `com.sdt.customization` | Partner yapılandırması ve görsel özelleştirmeler |

Test cihazında her biri başlangıçta `enabled=0` (varsayılan), sonunda `enabled=3` (kullanıcı tarafından kapalı) idi. Başka cihazın başlangıç durumu bu tablodan çıkarılamaz. Önce kendi kaydını al; `0` ve `1` durumları geri dönüşte ayrı tutulur. Zaten kapalı bileşeni açıp kapatma.

Sağlayıcı paketleri uzaktan destek veya ilerideki yeniden yapılandırma işlemleri için gerekebilir. Aynı gün yayın testinin geçmesi gelecekteki tüm provizyon/güncelleme senaryolarının doğrulandığı anlamına gelmez.

Korunan örnekler: TV+ EV/IPTV, TV+ OTT, DRM/sertifika bileşenleri, güncelleyiciler, Play Store/Play Services, Cast, klavye, Bluetooth, kumanda eşleme/global tuşlar ve stok ana ekran. Ortak sistem UID'sine toplu ağ engeli uygulanmadı.

Bir kişiye ait uygulama kaldırma tercihleri genel profil yapılmadı. Bu depodaki yöntem paketleri silmek yerine, seçilen kullanıcı durumunu kapatıp geri döndürmeye odaklanır.
