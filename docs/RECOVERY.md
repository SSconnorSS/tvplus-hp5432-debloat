# Geri dönüş ve yerel kayıtlar

Bu genel rehber, başka bir kutunun özel geri alma günlüğü yerine geçmez. Değişiklikten önce **kendi kutundaki** paket ve ayar durumlarını yerelde kaydet. Eksik bir ayar, açıkça yazılmış bir değer ve varsayılan paket durumu birbirinden farklıdır. Ham kayıtları herkese açık depoya yükleme.

Profilde bulunan bütün paketleri tek komutla açan veya sistem ayarlarını topluca sıfırlayan bir işlem kullanma. Yalnız kendi seçip değiştirdiğin hedefleri, kaydettiğin önceki durumlarına döndür. Sonradan yaptığın başka bir değişiklikle çakışma varsa mevcut durumu koruyup kaydı incele.

## Asıl ana ekrana dönmek

Denenen kurulumda `com.google.android.tvlauncher` etkin ve Android'in asıl Home tercihi olarak bırakıldı. Yeni ana ekranın görünmesi, stock uygulamanın silinmesine veya kapatılmasına dayanmıyor.

1. Normal Android ayarlarında **Erişilebilirlik** bölümünü aç ve CleanYourTV'nin **HomeKeyService** yardımcısını kapat. Başka erişilebilirlik hizmetlerini kapatma.
2. Kumandadan Home'a basarak asıl ana ekrana ve normal ayarlara erişebildiğini doğrula. Cihaz bir varsayılan ana ekran seçicisi sunuyorsa kendi kaydındaki asıl seçimi kullan; her Android TV'de bu seçici bulunmaz.
3. Yeni launcher'ı kaldırmak istersen, asıl Home ve Ayarlar çalıştıktan sonra normal **Uygulamalar** ekranından kaldır. Yardımcıyı kapatmak için uygulama verilerini temizlemek gerekmez.
4. TV+ yayın/ses, kanal değiştirme, ses tuşuna basılı tutma, Home ve bekleme/uyanmayı tekrar dene. Ardından normal yeniden başlatma ile aynı kontrolleri tekrarla.

Başka bir kurulum asıl launcher'ı kapattıysa bu kısa yol yeterli olmayabilir. Önce o kurulumun kendi kaydına göre asıl launcher geri etkinleştirilmelidir. Bu profili, başka kurulumların stock launcher veya setup wizard değişikliklerine yönelik genel bir kurtarma aracı gibi kullanma.

## Gizlilik tercihlerini geri çevirmek

Normal ayar ekranları sunuyorsa **Kullanım ve teşhis**, **Konum** ve **arka planda Wi-Fi taraması** seçeneklerini kendi önceki tercihlerine getir. Menü adları firmware'e göre değişebilir; Bluetooth'u veya ağ ayarlarını topluca sıfırlamak gerekmez.

Özel DNS için cihazın bir ayar ekranı varsa kaydettiğin önceki yapılandırmayı kullan. Menü yoksa kendi yerel kaydına göre, yeniden yetkilendirilmiş ADB bağlantısıyla yalnız ilgili ayarları ele almak gerekir. DNS modu ve sunucu adını birlikte değerlendir: başlangıçta ayar hiç yoksa, rastgele bir değer yazmak eski durumu birebir geri getirmez. Sonradan seçilmiş farklı bir DNS sunucusunun üzerine yazma.

Silinmiş reklam kimliğinin eski değeri geri getirilemez. Sistem yeni bir kimlik oluşturma seçeneği sunabilir; bu eski kimliğin kurtarılması değildir.

## Kapatılmış paketlerin eski durumları

Android'in kullanıcı 0 için kaydettiği paket ayarı ile uygulamanın o anda çalışması aynı şey değildir. Geri dönüşte başlangıçtaki ayarı kullan:

| Kaydedilen önceki durum | Geri dönüşün anlamı |
|---|---|
| `enabled=0` | Üretici/uygulama varsayılanına dönme (`default-state`); bu, açıkça `enable` yazılmasıyla aynı ayar değildir. |
| `enabled=1` | Kullanıcı için açıkça etkinleştirilmiş duruma dönme (`enable`). |
| Başlangıçta zaten kapalı veya farklı durum | Kendiliğinden açma; önceki alt durumu ve nedenini kendi kayıtlarınla incele. |

Bu oturumda kapatılan altı paketin başlangıç değeri `0` idi. Aynı değer başka kutu için varsayılmamalıdır. Profildeki paket adları kendi başına güvenli kapatma, kötüye kullanım veya izleme kanıtı sayılmaz.

Önce doğru kutu, etkin kullanıcı ve derlemeyi doğrula. Paketleri birer birer ele al; her adımın sonucunu kaydet ve normal işlevleri kontrol et. Paket kaldırılmışsa, firmware değişmişse veya mevcut değer kayıttaki beklenen durumdan farklıysa otomatik olarak üzerine yazma.

## Kaldırılan uygulamalar

Kaldırılan uygulamaları, mevcutsa **Google Play Store** veya geliştiricinin resmî dağıtım kaynağından yeniden kur. Bu depo üretici APK'ları, abonelik uygulamaları veya kişisel kurulum yedekleri dağıtmaz.

Kendi yerel APK yedeğin varsa bütün bölünmüş kurulum dosyalarının ve kaydettiğin dosya özetlerinin birlikte doğrulanması gerekir. Tek bir `base.apk` her uygulama için yeterli değildir. Bu tür özel yedekleri depoya veya herkese açık bir sürüm ekine koyma; kurulum kaynağını ve dağıtım haklarını ayrıca değerlendir.

Veri koruma seçeneğiyle kaldırılmış bir uygulamanın tekrar kurulması, hesap oturumları, izinler, veriler veya önbellek için tam geri dönüş garantisi sağlamaz. Bu deneyde bir uygulamada gerçek geri kurulum denendi; beş uygulamanın tamamı için hesap/veri geri yükleme testi yapılmadı.

## Bağlantı veya geri dönüş başarısızsa

Çalışan normal Ayarlar ekranı varsa ilgili değişikliği oradan geri çevir. ADB gerekiyorsa hata ayıklamayı normal menüden yeniden açıp yalnız kendi bilgisayarını kutunun izin ekranından yetkilendir. Kendi kutunun güncel adresini kullan; eski bir bağlantı adresini veya başka cihazın kaydını kopyalama.

Bir adımın sonucu belirsizse aynı değişikliği körlemesine tekrarlamak yerine yerel kaydı ve mevcut durumu karşılaştır. ADB ve Ayarlar erişimi kaybolmuşsa bu depo kurtarma garantisi vermez; cihazın resmî destek/kurtarma yoluna başvur. Fabrika sıfırlaması hesapları ve verileri silebildiğinden otomatik geri alma adımı değildir.

İş bitince fiziksel yayın ve kumanda kontrollerini tamamla, hata ayıklamayı normal menüden kapat ve bakım bağlantısının artık erişilebilir olmadığını doğrula. Bu rehber firmware, uygulama verisi veya DRM anahtarı yedeği değildir.
