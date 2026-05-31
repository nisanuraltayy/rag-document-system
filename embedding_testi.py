from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

cumle = "Python bir programlama dilidir"

karsilastirilacaklar = [
    "Python yazilim gelistirmek icin kullanilir",
    "Kediler cok sevimli hayvanlardir",
    "Java da bir programlama dilidir",
    "Bugun hava cok guzel",
]

cumle_vektoru = model.encode(cumle)

print(f"Ana cumle: {cumle}\n")
print("Benzerlik skorlari (1.0 = ayni anlam, 0.0 = alakasiz):\n")

for metin in karsilastirilacaklar:
    metin_vektoru = model.encode(metin)
    benzerlik = util.cos_sim(cumle_vektoru, metin_vektoru).item()
    print(f"  {benzerlik:.3f}  <-  {metin}")