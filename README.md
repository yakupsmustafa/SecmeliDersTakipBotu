Seçmeli Ders Kontenjan Takip Botu

Bu proje, Selçuk Üniversitesi Öğrenci Bilgi Sistemi (OBS) üzerinde yer alan seçmeli derslerin kontenjan durumunu otomatik olarak takip eden ve kontenjan açıldığı anda Telegram üzerinden bildirim gönderen bir otomasyon botudur.

Bot Ne Yapar?

OBS sistemine otomatik giriş yapar
Ders Kayıt sayfasını kontrol eder
Durumu “Dolu” olan dersleri izler
Eğer dersin durumu “Dolu” → “Seçilebilir (+)” olursa:
Telegram üzerinden anında bildirim gönderir
Aksi durumda hiçbir işlem yapmaz

Nasıl Çalışır?

Bot, GitHub Actions kullanılarak bulut ortamında çalışır
Cron job sayesinde 20 dakikada bir otomatik olarak tetiklenir
Kullanıcı bilgisayarını açık tutmak zorunda değildir

Güvenlik:

OBS kullanıcı adı, şifre ve Telegram bilgileri GitHub Secrets ile saklanır
Hassas bilgiler kod içinde kesinlikle yer almaz
Repo public olsa bile gizli bilgiler korunur

Kullanılan Teknolojiler:

Python
Playwright – Web otomasyonu (OBS etkileşimi)
GitHub Actions – Otomatik çalıştırma ve cron job
Telegram Bot API – Bildirim sistemi
HTML / DOM Parsing – Kontenjan durumu kontrolü

Kullanılan Sistemler ve Servisler:

GitHub Actions
Telegram
GitHub Secrets

Kimler İçin?

Seçmeli ders kontenjanını manuel takip etmek istemeyen öğrenciler
Otomasyon ve web scraping öğrenmek isteyenler
GitHub Actions ve cron job kullanımını öğrenmek isteyen geliştiriciler

⚠️ Not
Bu proje kişisel kullanım ve eğitim amaçlıdır.
