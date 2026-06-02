from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import chromadb
from google import genai
from dotenv import load_dotenv
import os

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


@app.post("/belge-ekle")
def belge_ekle(belge: Belge):
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

    return {
        "mesaj": "Belge eklendi ve ChromaDB'ye kaydedildi",
        "bu_belgenin_parca_sayisi": len(parcalar),
        "toplam_parca": koleksiyon.count(),
    }


@app.post("/dosya-yukle")
def dosya_yukle(dosya: UploadFile = File(...)):
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

    return {
        "mesaj": f"'{dosya.filename}' dosyasi yuklendi ve islendi",
        "bu_dosyanin_parca_sayisi": len(parcalar),
        "toplam_parca": koleksiyon.count(),
    }


@app.post("/sorgula")
def sorgula(istek: Soru):
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