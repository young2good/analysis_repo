import json
import pandas as pd

with open("data/raw_posts_dedup.json", encoding="utf-8") as f:
    posts = json.load(f)

src = open("analyze_freq.py", encoding="utf-8").read()
chunk = src.split("REGION_GROUP")[0]
ns = {}
exec(chunk, ns)
VENUE_KEYWORDS = ns["VENUE_KEYWORDS"]
VENUE_DISTRICT = ns["VENUE_DISTRICT"]

region_src = src.split("REGION_GROUP")[1]
region_chunk = "REGION_GROUP" + region_src.split("\n\n")[0]
exec(region_chunk, ns)
REGION_GROUP = ns["REGION_GROUP"]

def extract_venue(title):
    t = title.replace(" ", "")
    for kw, name in VENUE_KEYWORDS:
        if kw.replace(" ", "") in t:
            return name
    return None

rows = []
for p in posts:
    venue = extract_venue(p["title"])
    sido, sigungu, region = None, None, None
    if venue and venue in VENUE_DISTRICT:
        sido, sigungu = VENUE_DISTRICT[venue]
        if sido == "서울":
            region = "서울"
        elif sido == "인천":
            region = "인천"
        else:
            region = REGION_GROUP.get(sigungu, "경기 기타")
    rows.append({
        "title":   p["title"],
        "board":   p["board"],
        "created": p["created"],
        "venue":   venue,
        "sido":    sido,
        "sigungu": sigungu,
        "region":  region,
    })

df = pd.DataFrame(rows)
df["created"] = pd.to_datetime(df["created"])

df.to_parquet("data/posts_processed.parquet", index=False)
print(f"저장 완료: data/posts_processed.parquet ({len(df)}행)")
print(df[df["venue"].notna()][["title","venue","sido","sigungu","region"]].head(5).to_string())
