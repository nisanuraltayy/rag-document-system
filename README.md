# RAG Belge Sorgulama Sistemi

Yuklenen belgeler uzerinde dogal dil ile soru sorulabilen, RAG (Retrieval-Augmented Generation) mimarisi kullanan bir backend sistemi.

Kullanici bir belge yukler, sisteme soru sorar ve sistem yalnizca o belgedeki bilgilere dayanarak cevap uretir. Belgede olmayan bilgiler icin "bu bilgi belgede bulunmuyor" yanitini verir, boylece yanlis bilgi (halusinasyon) onlenir.

## Ozellikler

- Metin veya TXT dosyasi ile belge yukleme
- Belgeleri otomatik olarak parcalara bolme (chunking, overlap destekli)
- Her parcayi vektore cevirme (embedding)
- Vektorleri kalici olarak saklama (ChromaDB)
- Anlamsal arama: soruya en yakin parcalari bulma
- LLM ile cevap uretme (Google Gemini)

## Kullanilan Teknolojiler

- **Python** & **FastAPI** — backend ve API
- **sentence-transformers** — embedding (metni vektore cevirme)
- **ChromaDB** — vektor veritabani (kalici depolama)
- **Google Gemini** — cevap uretimi (LLM)
- **uvicorn** — sunucu

## RAG Akisi

1. **Belge alma** — kullanici metin veya dosya yukler
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
pip install fastapi uvicorn sentence-transformers chromadb google-genai python-dotenv python-multipart

# .env dosyasi olustur ve Gemini API anahtarini ekle
# GEMINI_API_KEY=senin_anahtarin

# Sunucuyu calistir
uvicorn main:app --reload
```

## API Endpointleri

| Method | Endpoint | Aciklama |
|--------|----------|----------|
| GET | `/saglik` | Sistem durumu ve kayitli parca sayisi |
| POST | `/belge-ekle` | Metin olarak belge ekleme |
| POST | `/dosya-yukle` | TXT dosyasi yukleme |
| POST | `/sorgula` | Belgeye dayali soru sorma |



