from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb

app = FastAPI()

print("Embedding modeli yukleniyor...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model hazir!")

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
    parca_vektorleri = model.encode(parcalar).tolist()

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


@app.post("/sorgula")
def sorgula(istek: Soru):
    if koleksiyon.count() == 0:
        return {"mesaj": "Henuz belge eklenmemis. Once belge ekleyin."}

    soru_vektoru = model.encode(istek.soru).tolist()

    sonuc = koleksiyon.query(
        query_embeddings=[soru_vektoru],
        n_results=istek.kac_sonuc,
    )

    parcalar = sonuc["documents"][0]
    mesafeler = sonuc["distances"][0]
    basliklar = [m["baslik"] for m in sonuc["metadatas"][0]]

    en_alakali = []
    for i in range(len(parcalar)):
        en_alakali.append({
            "baslik": basliklar[i],
            "parca": parcalar[i],
            "mesafe": round(mesafeler[i], 3),
        })

    return {"soru": istek.soru, "en_alakali_parcalar": en_alakali}