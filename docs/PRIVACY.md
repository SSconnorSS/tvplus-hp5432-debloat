# Gizlilik ve paylaşılacak bilgiler

Profil aracı üçüncü taraf servise veri yüklemez. Varsayılan çalışmada yalnız yerel JSON'u okur. `--device` verilirse zaten yetkilendirilmiş ADB bağlantısından model/derleme ve profildeki altı paketin kurulum/açıklık durumunu okur. Kendiliğinden bağlanmaz, eşleştirme yapmaz veya hata ayıklamayı açmaz.

`--save` yerel bir kayıt oluşturur. ADB uç noktası, benzersiz seri/Android kimliği, MAC, hesaplar, tam paket envanteri, uygulama verileri veya anahtarlar kaydedilmez. `.local/` Git tarafından dışlanır. Buna rağmen paylaşmadan önce yerel dosyaları kendin gözden geçir.

Sorun bildirimine model, Android/derleme, seçtiğin paket ve kısa sonuç yeterlidir. Ham `getprop`, `dumpsys`, yedek, logcat, hesap ekranı, reklam kimliği, abonelik bilgisi veya ADB anahtarı ekleme. Ekran görüntülerinde Wi-Fi adı, e-posta ve hesap ayrıntılarını kaldır.

Tema uygulaması ile gizlilik ayarları farklı işlemlerdir. Ana ekranın internet izni bulunmaması diğer uygulamaların veri göndermediğini göstermez. TV+ ve diğer yayın servisleri kullanım/hesap kayıtları tutabilir. Paket kapatma ve DNS filtresi tüm takibi veya yayın içi reklamları kaldırmaz.

Özel DNS kullanılırsa seçilen DNS işletmecisi alan adı sorgularını işler. Mevcut kurumsal/aile DNS'i veya VPN ayarı değiştirilmeden önce başlangıç değeri ve ihtiyaçlar değerlendirilmeli. Depo aracı bu ayarı değiştirmez.
