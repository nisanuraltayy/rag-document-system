from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

belgeler = []


class Belge(BaseModel):
    baslik: str
    icerik: str


@app.get("/")
def ana_sayfa():
    return {"mesaj": "RAG belge sistemi calisiyor!"}


@app.get("/saglik")
def saglik_kontrolu():
    return {"durum": "iyi"}


@app.post("/belge-ekle")
def belge_ekle(belge: Belge):
    belgeler.append({"baslik": belge.baslik, "icerik": belge.icerik})
    return {"mesaj": "Belge eklendi", "toplam_belge": len(belgeler)}


@app.get("/belgeler")
def belgeleri_listele():
    return {"toplam": len(belgeler), "belgeler": belgeler}