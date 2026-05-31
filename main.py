from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

app = FastAPI()

print("Embedding modeli yukleniyor...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model hazir!")

belgeler = []


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
    return {"durum": "iyi"}


@app.post("/belge-ekle")
def belge_ekle(belge: Belge):
    parcalar = metni_parcala(belge.icerik)
    parca_vektorleri = model.encode(parcalar)
    for i, parca in enumerate(parcalar):
        belgeler.append({
            "baslik": belge.baslik,
            "parca": parca,
            "vektor": parca_vektorleri[i],
        })
    return {
        "mesaj": "Belge eklendi, parcalandi ve vektorlere cevrildi",
        "toplam_parca": len(belgeler),
        "bu_belgenin_parca_sayisi": len(parcalar),
    }


@app.get("/belgeler")
def belgeleri_listele():
    sonuc = [{"baslik": b["baslik"], "parca": b["parca"]} for b in belgeler]
    return {"toplam": len(belgeler), "parcalar": sonuc}


@app.post("/sorgula")
def sorgula(istek: Soru):
    if not belgeler:
        return {"mesaj": "Henuz belge eklenmemis. Once belge ekleyin."}

    soru_vektoru = model.encode(istek.soru)

    sonuclar = []
    for parca_kaydi in belgeler:
        benzerlik = util.cos_sim(soru_vektoru, parca_kaydi["vektor"]).item()
        sonuclar.append({
            "baslik": parca_kaydi["baslik"],
            "parca": parca_kaydi["parca"],
            "benzerlik": round(benzerlik, 3),
        })

    sonuclar.sort(key=lambda x: x["benzerlik"], reverse=True)

    return {
        "soru": istek.soru,
        "en_alakali_parcalar": sonuclar[:istek.kac_sonuc],
    }