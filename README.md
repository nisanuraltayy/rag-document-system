# RAG Belge Sorgulama Sistemi

Yuklenen belgeler uzerinde dogal dil ile soru sorulabilen, RAG (Retrieval-Augmented Generation) mimarisi kullanan bir backend sistemi.

Kullanici metin, TXT veya PDF olarak belge yukler, sisteme soru sorar ve sistem yalnizca o belgedeki bilgilere dayanarak cevap uretir. Belgede olmayan bilgiler icin "Bu bilgi belgede bulunmuyor" yanitini verir, boylece yanlis bilgi (halusinasyon) onlenir.

## Canli Demo

Sistem internette canli olarak calismaktadir:

**[https://rag-document-system-88fu.onrender.com/docs](https://rag-document-system-88fu.onrender.com/docs)**

Not: Render ucretsiz katmanda calistigi icin servis 15 dakika kullanilmazsa uyur. Ilk istek 30-60 saniye surebilir, sonraki istekler hizlidir.

## Ozellikler

- Metin, TXT dosyasi veya PDF dosyasi ile belge yukleme
- Belgeleri otomatik olarak parcalara bolme (chunking, overlap destekli)
- Her parcayi vektore cevirme (embedding, Gemini API)
- Vektorleri kalici olarak saklama (ChromaDB)
- Anlamsal arama: soruya en yakin parcalari bulma
- LLM ile cevap uretme (Google Gemini)
- Bozuk veya gecersiz dosyalar icin anlamli hata mesajlari
- FastAPI dependency injection ile test edilebilir mimari
- Docker ile container destegi

## Kullanilan Teknolojiler

- **Python** & **FastAPI** — backend ve API
- **Google Gemini** — embedding ve cevap uretimi (LLM)
- **ChromaDB** — vektor veritabani (kalici depolama)
- **pypdf** — PDF dosyalarindan metin cikarma
- **uvicorn** — sunucu
- **Docker** — container ve tasinabilir ortam
- **Render** — production deploy

## RAG Akisi

1. **Belge alma** — kullanici metin, TXT veya PDF yukler
2. **Parcalama** — uzun metin kucuk, ortusmeli parcalara bolunur
3. **Embedding** — her parca anlamini koruyan bir vektore cevrilir
4. **Saklama** — vektorler ChromaDB'ye kalici olarak kaydedilir
5. **Sorgulama** — sorunun vektoru ile en yakin parcalar bulunur
6. **Cevap uretme** — bulunan parcalar Gemini'ye verilir, cevap uretilir

## Kurulum

```bash
# Sanal ortam olustur ve aktiflestir
python -m venv venv
venv\Scripts\activate

# Gerekli kutuphaneleri kur
pip install -r requirements.txt

# .env dosyasi olustur ve Gemini API anahtarini ekle
# GEMINI_API_KEY=senin_anahtarin

# Sunucuyu calistir
uvicorn main:app --reload
```

## Docker ile Calistirma

```bash
# Image olustur
docker build -t rag-system .

# Container'i baslat
docker run -d -p 8000:8000 --env-file .env --name rag-container rag-system
```

## API Endpointleri

| Method | Endpoint | Aciklama |
|--------|----------|----------|
| GET | `/saglik` | Sistem durumu ve kayitli parca sayisi |
| POST | `/belge-ekle` | Metin olarak belge ekleme |
| POST | `/dosya-yukle` | TXT dosyasi yukleme |
| POST | `/pdf-yukle` | PDF dosyasi yukleme (metin katmanli PDF'ler) |
| POST | `/sorgula` | Belgeye dayali soru sorma |

Tum endpointlerin detayli dokumantasyonu icin `/docs` (Swagger UI) adresine bakin.

## Mimari Notlar

**Dependency Injection:** Endpointler, ihtiyac duyduklari servisleri (`koleksiyon`, `llm_client`) global degisken yerine FastAPI'nin `Depends()` mekanizmasiyla parametre olarak alir. Bu, test edilebilirligi ve esnekligi artirir.

**Halusinasyon onleme:** Prompt'a "sadece baglamda verilen bilgilere dayan, baglamda cevap yoksa 'bu bilgi belgede bulunmuyor' de" talimati eklenmistir. LLM'in kendi bilgisinden uydurma yapmasi engellenir.

**Production hazirligi:** Embedding ve LLM islemleri API uzerinden yapilir (yerel agir model yok), bu sayede sistem dusuk bellekli sunucularda da calisabilir.

