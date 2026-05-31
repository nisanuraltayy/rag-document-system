from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

belgeler = []


class Belge(BaseModel):
    baslik: str
    icerik: str


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
    belgeler.append({
        "baslik": belge.baslik,
        "icerik": belge.icerik,
        "parcalar": parcalar,
        "parca_sayisi": len(parcalar)
    })
    return {
        "mesaj": "Belge eklendi ve parcalara bolundu",
        "toplam_belge": len(belgeler),
        "bu_belgenin_parca_sayisi": len(parcalar)
    }


@app.get("/belgeler")
def belgeleri_listele():
    return {"toplam": len(belgeler), "belgeler": belgeler}