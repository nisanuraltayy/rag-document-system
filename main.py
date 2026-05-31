from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def ana_sayfa():
    return {"mesaj": "RAG belge sistemi calisiyor!"}


@app.get("/saglik")
def saglik_kontrolu():
    return {"durum": "iyi"}