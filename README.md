# 🔄 Veritabanı Çeviri Aracı

<div align="center">
  <img src="content/readme-header.svg" alt="Veritabanı Çeviri Aracı Logo" width="500">
  
  <p align="center">
    <b>MySQL ve MSSQL veritabanları için metin içeriği çeviri aracı</b>
  </p>
  
  <p align="center">
    <a href="#-özellikler"><strong>Özellikler</strong></a> •
    <a href="#-kurulum"><strong>Kurulum</strong></a> •
    <a href="#-kullanım"><strong>Kullanım</strong></a> •
    <a href="#-bağlantı-ayarları"><strong>Bağlantı Ayarları</strong></a> •
    <a href="#-çeviri-ayarları"><strong>Çeviri Ayarları</strong></a>
  </p>
</div>

## 📋 Proje Tanımı

Bu araç, veritabanınızdaki metin içeriklerini otomatik olarak çevirmek için tasarlanmıştır. MySQL ve MSSQL veritabanlarına bağlanabilir, tablolarınızı görüntüleyebilir ve seçtiğiniz sütunlardaki metinleri Google Translate API kullanarak istediğiniz dile çevirebilirsiniz. Çevirilen içerikleri sadece görüntüleyebilir veya doğrudan veritabanına kaydedebilirsiniz.

### 📸 Ekran Görüntüleri
<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <img src="content/homa-page-1.png" width="100%"/><br/>
        <b>Ana Ekran</b>
      </td>
      <td align="center" width="50%">
        <img src="content/database-connect-1.png" width="100%"/><br/>
        <b>Veritabanı Bağlantısı</b>
      </td>
    </tr>
    <tr>
      <td align="center" width="50%">
        <img src="content/get-table.png" width="100%"/><br/>
        <b>Tabloları Listeleme</b>
      </td>
      <td align="center" width="50%">
        <img src="content/select-table.png" width="100%"/><br/>
        <b>Listeden Tablo Seçme</b>
      </td>
    </tr>
    <tr>
      <td align="center" colspan="2">
        <img src="content/film-table-data-translate.png" width="50%"/><br/>
        <b>Veri Çevirisi</b>
      </td>
    </tr>
  </table>
</div>

## 🚀 Özellikler

<div align="center">
  <table>
    <tr>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/database.png" width="48px"/><br/>
        <b>Çoklu Veritabanı Desteği</b><br/>
        <small>MySQL ve MSSQL</small>
      </td>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/translate.png" width="48px"/><br/>
        <b>Otomatik Çeviri</b><br/>
        <small>Google Translate API</small>
      </td>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/edit.png" width="48px"/><br/>
        <b>Veritabanı Güncelleme</b><br/>
        <small>Çevirileri kaydetme</small>
      </td>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/test-tube.png" width="48px"/><br/>
        <b>Test Modu</b><br/>
        <small>Tek kayıt çevirisi</small>
      </td>
    </tr>
    <tr>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/debug.png" width="48px"/><br/>
        <b>Debug Modu</b><br/>
        <small>Detaylı log izleme</small>
      </td>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/data-backup.png" width="48px"/><br/>
        <b>Bağlantı Hatırlama</b><br/>
        <small>Ayarları kaydetme</small>
      </td>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/checked--v1.png" width="48px"/><br/>
        <b>Yazma Yetkisi Testi</b><br/>
        <small>Güvenli çalışma</small>
      </td>
      <td align="center" width="25%">
        <img src="https://img.icons8.com/color/48/000000/save-close.png" width="48px"/><br/>
        <b>Sonuçları Kaydetme</b><br/>
        <small>Log dosyaları</small>
      </td>
    </tr>
  </table>
</div>

## 📦 Kurulum

### Sistem Gereksinimleri

- **Python**: 3.7 veya üzeri
- **Veritabanı**: MySQL veya MSSQL
- **İşletim Sistemi**: Windows, Linux veya macOS

### Kurulum Adımları

1. Projeyi indirin veya klonlayın:

```bash
git clone https://github.com/mehmetdogandev/database-translate-tool.git
cd database-translate-tool
```

2. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:

```bash
python main.py
```

### Gerekli Kütüphaneler

requirements.txt dosyasında aşağıdaki kütüphaneler bulunur:

```
tkinter
mysql-connector-python
pyodbc
deep-translator
```

## 🖥️ Kullanım

### Adım 1: Veritabanına Bağlanma

1. Sol paneldeki "Bağlantı Ayarları" bölümünden veritabanı tipini seçin (MySQL veya MSSQL).
2. Bağlantı bilgilerini girin:
   - Host/Server
   - Veritabanı adı
   - Kullanıcı adı
   - Şifre
   - Port (MySQL için)
   - ODBC Sürücü (MSSQL için)
3. İsterseniz "Bağlantı bilgilerini hatırla" seçeneğini işaretleyebilirsiniz.
4. "Bağlan" butonuna tıklayın.

### Adım 2: Tabloları Görüntüleme

1. Bağlantı başarılıysa "Tabloları Getir" butonuna tıklayın.
2. Açılan listeden çeviri yapmak istediğiniz tabloyu seçin.

### Adım 3: Çeviri Ayarları

1. Çevrilecek sütunları işaretleyin (metin içeren sütunlar otomatik seçilir).
2. Çeviri modunu seçin:
   - "Sadece Göster": Çevirileri gösterir ancak veritabanını güncellemez.
   - "Veritabanına Kaydet": Çevirileri veritabanına kaydeder.
3. Test modu için "Sadece 1 kayıt işle" seçeneğini işaretleyebilirsiniz.
4. Kayıt limitini belirleyin (kaç satır çevrileceğini sınırlar).
5. Hedef dili seçin (varsayılan: Türkçe).

### Adım 4: Çeviri İşlemi

1. "Verileri Getir ve Çevir" butonuna tıklayın.
2. Çeviri sonuçları sağ panelde görüntülenecektir.
3. İsterseniz sonuçları "Sonuçları Kaydet" butonu ile dosyaya kaydedebilirsiniz.

## ⚙️ Bağlantı Ayarları

### MySQL Bağlantısı

- **Host/Server**: Veritabanı sunucu adresi (örn. localhost)
- **Veritabanı**: Veritabanı adı
- **Kullanıcı Adı**: MySQL kullanıcı adı
- **Şifre**: MySQL şifresi
- **Port**: MySQL port numarası (varsayılan: 3306)

### MSSQL Bağlantısı

- **Host/Server**: SQL Server adresi (örn. localhost\SQLEXPRESS)
- **Veritabanı**: Veritabanı adı
- **Kullanıcı Adı**: SQL Server kullanıcı adı
- **Şifre**: SQL Server şifresi
- **ODBC Sürücü**: Kurulu ODBC sürücüsü (örn. ODBC Driver 17 for SQL Server)

## 🌐 Çeviri Ayarları

### Çeviri Modu

- **Sadece Göster**: Çevirileri gösterir ancak veritabanını değiştirmez
- **Veritabanına Kaydet**: Çevirileri doğrudan veritabanına kaydeder

### Test Modu

Test modunu aktifleştirerek sadece bir kayıt üzerinde çeviri yapabilirsiniz. Bu özellik, büyük tablolarda çeviri yapmadan önce test etmek için kullanışlıdır.

### Kayıt Limiti

Çevrilecek maksimum kayıt sayısını belirler. Büyük tablolarda performans için bu değeri düşük tutmanız önerilir.

### Desteklenen Diller

- Türkçe (tr)
- İngilizce (en)
- İspanyolca (es)
- Fransızca (fr)
- Almanca (de)
- İtalyanca (it)
- Portekizce (pt)
- Rusça (ru)
- Japonca (ja)
- Korece (ko)
- Çince (zh)

## 🧪 Test Özellikleri

### Yazma Yetkisi Testi

Bağlantı kurulduktan sonra veritabanına yazma yetkinizi test edebilirsiniz. Bu özellik, çeviri yapılacak veritabanında yeterli yetkilere sahip olduğunuzdan emin olmanızı sağlar.

### Manuel UPDATE Testi

Seçili tabloda manuel bir UPDATE sorgusu çalıştırarak veritabanı güncelleme işlemini test edebilirsiniz.

## 🔍 Debug Modu

"Debug Modu" seçeneğini işaretleyerek detaylı logları görüntüleyebilirsiniz. Bu özellik, hata ayıklama ve sorun giderme için kullanışlıdır.

## 📝 Notlar

- Büyük tablolarda çeviri işlemi zaman alabilir. Başlangıçta düşük kayıt limiti ile test etmeniz önerilir.
- Çeviri işlemi sırasında internet bağlantısı gereklidir (Google Translate API için).
- MSSQL bağlantısı için uygun ODBC sürücüsünün yüklü olması gerekir.
- Veritabanına yazma yetkisine sahip olduğunuzdan emin olun.

## 👨‍💻 Geliştiriciler

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/mehmetdogandev">
          <img src="https://github.com/mehmetdogandev.png" width="100px;" alt="Mehmet Doğan"/>
          <br />
          <b>Mehmet DOĞAN</b>
        </a>
        <br />
        <small>Proje Geliştiricisi</small>
      </td>
    </tr>
  </table>
</div>

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

<div align="center">
  <p>Developed with ❤️ by <a href="https://github.com/mehmetdogandev">Mehmet DOĞAN</a></p>
  <a href="https://github.com/mehmetdogandev/database-translate-tool/stargazers">
    <img src="https://img.shields.io/github/stars/mehmetdogandev/database-translate-tool?style=flat-square" alt="Stars"/>
  </a>
  <a href="https://github.com/mehmetdogandev/database-translate-tool/network/members">
    <img src="https://img.shields.io/github/forks/mehmetdogandev/database-translate-tool?style=flat-square" alt="Forks"/>
  </a>
  <a href="https://github.com/mehmetdogandev/database-translate-tool/issues">
    <img src="https://img.shields.io/github/issues/mehmetdogandev/database-translate-tool?style=flat-square" alt="Issues"/>
  </a>
</div>
