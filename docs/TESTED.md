# HP5432 test kaydı

Bu sayfa, **26 Ekim 2026'da tek bir fiziksel kutuda, aynı gün yapılan kontrolleri** özetler. Ham günlük, ağ adresi, cihazın benzersiz tanımlayıcıları ve hesap ekranları yayımlanmaz.

| Alan | Denenen yapı |
|---|---|
| Üretici / model | SkyworthDigital HP5432 |
| Sistem | Android TV 14, SDK 34 |
| Derleme | `UKG3.250826.001.P01.02.079_20260612` |
| Güvenlik yaması | 5 Nisan 2026 |
| Ana ekran kaynağı | [CleanYourTV'nin kullanılan kaynak sürümü](https://github.com/Gathin23/cleanyourtv/tree/f592b6d2db0cfa0e28779660f25ff65386a5ff9b) |
| Görünüm | Glass teması temelinde altı sütunlu uygulama sırası ve uygulama kitaplığı |

Launcher, upstream kaynak değiştirilmeden yerelde derlendi. Kurulan launcher'ın manifestinde `INTERNET` izni bulunmuyor. Bu gözlem, kutudaki diğer uygulamaların ağ trafiği veya veri toplaması hakkında sonuç vermez.

## Home ve açılış davranışı

Asıl Android ana ekranı `com.google.android.tvlauncher` etkin bırakıldı. Yeni görünüm için yalnız **HomeKeyService** erişilebilirlik yardımcısı kullanıldı; InputKeyService etkinleştirilmedi ve launcher'a `WRITE_SECURE_SETTINGS` verilmedi.

| Seçenek | Denenen değer / davranış |
|---|---|
| `stock_home_redirect` | `com.google.android.tvlauncher`; asıl ana ekran göründüğünde yeni launcher'a yönlendirme |
| `key_filter` | `true`; kısa Home basışı için ek yönlendirme yolu |
| `home_long_press_home` | `false`; her uzun Home basışını zorla yeni ana ekrana çeviren seçenek kapalı |
| `power_on_home` | `true`; açılışta sağlayıcının kendiliğinden açtığı `com.skyworth.iptv` penceresine yönelik sınırlı yönlendirme |
| `power_on_home_always` | `false`; beklemeden dönüşte her uygulamanın üzerine zorla ana ekran açma kapalı |
| `restore_key_services` | `false`; yardımcının kendisini güvenli ayarlara yazarak geri eklemesi kapalı |
| `consume_volume_keys` | `false`; özel ses tuşu tüketme/tekrar üretme kapalı |

`power_on_home`, açılış veya ekranın açılması sonrasındaki sınırlı sürede çalışır. İlk fiziksel kullanıcı tuşu, güç/uyandırma tuşları dışında, bu yönlendirme penceresini kapatır. Kullanıcının daha sonra bilerek TV+ açması engellenmez. Bu davranış `power_on_home_always` ile aynı değildir.

`key_filter: true` tamamen etkisiz bir arka plan gözlemcisi değildir: kaynak kod, standart Settings ve All Apps tuşlarını da ele alır. Boş özel tuş eşlemeleri, her kumanda veya firmware için tüm tuş davranışlarının aynı kalacağını kanıtlamaz. Uzun Home, oyun kumandaları ve farklı kumanda modelleri için kapsamlı doğrulama yapılmadı.

## Kontrol sonuçları

| Kontrol | Sonuç ve kanıtın sınırı |
|---|---|
| Launcher derleme, statik kontrol ve testleri | Geçti; donanımdaki bütün davranışları kapsamaz. |
| Bu depodaki salt okunur profil aracı | On çevrimdışı test geçti. Yeni aracın bütün ADB akışı fiziksel kutuda yeniden çalıştırılmadı; kutunun bakım bağlantısı kapalı tutuldu. Donanım sonuçları önceki yerel inceleme ve fiziksel kumanda kontrollerinden gelir. |
| TV+ canlı yayın, ses ve kanal değiştirme | Fiziksel kullanımda doğrulandı; tüm kanal/içerik türleri ayrı ayrı denenmedi. |
| Home ile yeni ana ekrana dönüş | Fiziksel kumandayla doğrulandı. |
| Ses tuşuna basılı tutarak tekrar | Fiziksel kumandayla doğrulandı. |
| Yeniden başlatma sonrası yayın, Home ve kumanda | Son kurulumdan sonra fiziksel kullanımda doğrulandı. |
| Kumandadan kapatma ve tekrar açma | Doğrulandı; her uygulamada ayrı bir bekleme/uyanma matrisi uygulanmadı. |
| TV+ yayın hizmeti ve HomeKeyService | Son yerel kontrolde çalışır durumda gözlendi. Hizmetin çalışması tek başına görüntü/ses kanıtı sayılmadı. |
| Özel DNS | AdGuard DNS doğrulaması yerel sistem durumunda başarılıydı. Bütün reklamların veya izlemelerin engellendiği test edilmedi. |
| Paket geri alma denemesi | TR-369 bileşeninde kapatma ve eski duruma geri açma denendi. Bütün paketler için ayrı bir tam geri alma çevrimi yapılmadı. |
| Kaldırılan uygulama geri kurma denemesi | TV Bro, özel yerel yedeğinden geri kuruldu ve sonra yeniden kaldırıldı. Diğer dört uygulamada yedek dosyalarının bütünlüğü doğrulandı. Bu APK'lar yayımlanmaz. |

## Bakım bağlantısının kapatılması

Bilgisayarın hata ayıklama yetkisi normal sistem onayıyla kaldırıldı ve bağlantının yetkisiz olduğu gözlendi. Ardından USB hata ayıklaması kullanıcı tarafından kapatıldı; kutu yeniden başlatıldı ve fiziksel kullanım tekrar doğrulandı.

Son bağımsız ağ kontrolünde kutu erişilebilirken ADB'nin kullanılan bakım portu **5555 bağlantıyı reddetti**. Bu, yalnız o andaki söz konusu port kontrolüdür; bütün portlar veya ağ hizmetleri hakkında güvenlik taraması iddiası değildir.

## Sonucun kapsamı

Bu kayıt çok günlük dayanıklılık, güncelleme sonrası kalıcılık veya başka kutularla uyumluluk testi değildir. Aynı modelde farklı derleme ve sağlayıcı ayarları farklı sonuç verebilir. Firmware güncellemesi sonrasında profil yeniden değerlendirilmelidir.

Yayın/DRM bileşenleri değiştirilmedi ve temel işlevler denendi; bu durum genel teknik güvenlik veya hukuka uygunluk garantisi oluşturmaz. Bu depo bir bağımsız gözlem ve profil paylaşımıdır, resmî ürün desteği değildir.
