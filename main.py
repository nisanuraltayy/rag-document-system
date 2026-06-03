from fastapi import FastAPI, UploadFile, File, Depends
from pypdf import PdfReader
from io import BytesIO
from pydantic import BaseModel
import chromadb
from google import genai
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from database import get_db, BelgeKaydi

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

chroma_client = chromadb.PersistentClient(path="./chroma_db")
koleksiyon = chroma_client.get_or_create_collection(name="belgeler")

sayac = koleksiyon.count()


class Belge(BaseModel):
    baslik: str
    icerik: str


class Soru(BaseModel):
    soru: str
    kac_sonuc: int = 3


def get_koleksiyon():
    return koleksiyon


def get_llm_client():
    return client


def metni_parcala(metin: str, parca_boyutu: int = 200, ortusme: int = 50):
    parcalar = []
    baslangic = 0
    while baslangic < len(metin):
        bitis = baslangic + parca_boyutu
        parca = metin[baslangic:bitis]
        parcalar.append(parca)
        baslangic = bitis - ortusme
    return parcalar


def embedding_uret(metinler: list[str]):
    sonuc = client.models.embed_content(
        model="gemini-embedding-001",
        contents=metinler,
    )
    return [e.values for e in sonuc.embeddings]


@app.get("/")
def ana_sayfa():
    return {"mesaj": "RAG belge sistemi calisiyor!"}


@app.get("/saglik")
def saglik_kontrolu():
    return {"durum": "iyi", "kayitli_parca_sayisi": koleksiyon.count()}


@app.get("/belgeler")
def belgeleri_listele(
    tur: str | None = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    sorgu = db.query(BelgeKaydi)

    if tur:
        sorgu = sorgu.filter(BelgeKaydi.tur == tur)

    sorgu = sorgu.order_by(BelgeKaydi.yukleme_tarihi.desc()).limit(limit)
    kayitlar = sorgu.all()

    return {
        "toplam_donen": len(kayitlar),
        "belgeler": [
            {
                "id": k.id,
                "dosya_adi": k.dosya_adi,
                "tur": k.tur,
                "parca_sayisi": k.parca_sayisi,
                "yukleme_tarihi": k.yukleme_tarihi.isoformat(),
            }
            for k in kayitlar
        ],
    }


@app.post("/belge-ekle")
def belge_ekle(
    belge: Belge,
    koleksiyon = Depends(get_koleksiyon),
    db: Session = Depends(get_db),
):
    global sayac
    parcalar = metni_parcala(belge.icerik)
    parca_vektorleri = embedding_uret(parcalar)

    id_listesi = []
    metadata_listesi = []
    for parca in parcalar:
        id_listesi.append(f"parca_{sayac}")
        metadata_listesi.append({"baslik": belge.baslik})
        sayac += 1

    koleksiyon.add(
        ids=id_listesi,
        embeddings=parca_vektorleri,
        documents=parcalar,
        metadatas=metadata_listesi,
    )

    yeni_kayit = BelgeKaydi(
        dosya_adi=belge.baslik,
        tur="metin",
        parca_sayisi=len(parcalar),
    )
    db.add(yeni_kayit)
    db.commit()
    db.refresh(yeni_kayit)

    return {
        "mesaj": "Belge eklendi ve ChromaDB'ye kaydedildi",
        "bu_belgenin_parca_sayisi": len(parcalar),
        "toplam_parca": koleksiyon.count(),
        "belge_id": yeni_kayit.id,
    }


@app.post("/dosya-yukle")
def dosya_yukle(
    dosya: UploadFile = File(...),
    koleksiyon = Depends(get_koleksiyon),
    db: Session = Depends(get_db),
):
    global sayac
    icerik_bytes = dosya.file.read()
    metin = icerik_bytes.decode("utf-8")

    parcalar = metni_parcala(metin)
    parca_vektorleri = embedding_uret(parcalar)

    id_listesi = []
    metadata_listesi = []
    for parca in parcalar:
        id_listesi.append(f"parca_{sayac}")
        metadata_listesi.append({"baslik": dosya.filename})
        sayac += 1

    koleksiyon.add(
        ids=id_listesi,
        embeddings=parca_vektorleri,
        documents=parcalar,
        metadatas=metadata_listesi,
    )

    yeni_kayit = BelgeKaydi(
        dosya_adi=dosya.filename,
        tur="txt",
        parca_sayisi=len(parcalar),
    )
    db.add(yeni_kayit)
    db.commit()
    db.refresh(yeni_kayit)

    return {
        "mesaj": f"'{dosya.filename}' dosyasi yuklendi ve islendi",
        "bu_dosyanin_parca_sayisi": len(parcalar),
        "toplam_parca": koleksiyon.count(),
        "belge_id": yeni_kayit.id,
    }


@app.post("/pdf-yukle")
def pdf_yukle(
    dosya: UploadFile = File(...),
    koleksiyon = Depends(get_koleksiyon),
    db: Session = Depends(get_db),
):
    global sayac

    pdf_bytes = dosya.file.read()
    try:
        pdf_okuyucu = PdfReader(BytesIO(pdf_bytes))
    except Exception:
        return {"hata": "Gecerli bir PDF dosyasi yukleyin. Dosya bozuk, bos veya PDF formatinda degil."}

    metin = ""
    for sayfa in pdf_okuyucu.pages:
        metin += sayfa.extract_text() + "\n"

    if not metin.strip():
        return {"mesaj": "PDF'ten metin cikarilamadi. Taranmis bir PDF olabilir."}

    parcalar = metni_parcala(metin)
    parca_vektorleri = embedding_uret(parcalar)

    id_listesi = []
    metadata_listesi = []
    for parca in parcalar:
        id_listesi.append(f"parca_{sayac}")
        metadata_listesi.append({"baslik": dosya.filename})
        sayac += 1

    koleksiyon.add(
        ids=id_listesi,
        embeddings=parca_vektorleri,
        documents=parcalar,
        metadatas=metadata_listesi,
    )

    yeni_kayit = BelgeKaydi(
        dosya_adi=dosya.filename,
        tur="pdf",
        parca_sayisi=len(parcalar),
    )
    db.add(yeni_kayit)
    db.commit()
    db.refresh(yeni_kayit)

    return {
        "mesaj": f"'{dosya.filename}' PDF'i yuklendi ve islendi",
        "sayfa_sayisi": len(pdf_okuyucu.pages),
        "bu_pdfin_parca_sayisi": len(parcalar),
        "toplam_parca": koleksiyon.count(),
        "belge_id": yeni_kayit.id,
    }


@app.post("/sorgula")
def sorgula(
    istek: Soru,
    koleksiyon = Depends(get_koleksiyon),
    client = Depends(get_llm_client),
):
    if koleksiyon.count() == 0:
        return {"mesaj": "Henuz belge eklenmemis. Once belge ekleyin."}

    soru_vektoru = embedding_uret([istek.soru])[0]

    sonuc = koleksiyon.query(
        query_embeddings=[soru_vektoru],
        n_results=istek.kac_sonuc,
    )

    parcalar = sonuc["documents"][0]
    baglam = "\n\n".join(parcalar)

    prompt = f"""Asagidaki baglam bilgisini kullanarak soruyu cevapla.
Sadece baglamda verilen bilgilere dayan. Baglamda cevap yoksa
"Bu bilgi belgede bulunmuyor." de.

BAGLAM:
{baglam}

SORU: {istek.soru}

CEVAP:"""

    yanit = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
    )

    return {
        "soru": istek.soru,
        "cevap": yanit.text,
        "kullanilan_parcalar": parcalar,
    }