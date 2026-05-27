import sys, re, json

with open("data/raw_posts_dedup.json", encoding="utf-8") as f:
    posts = json.load(f)

# analyze_freq.py 에서 VENUE_KEYWORDS / VENUE_DISTRICT 직접 파싱
src = open("analyze_freq.py", encoding="utf-8").read()
# VENUE_KEYWORDS 와 VENUE_DISTRICT 블록만 exec
chunk = src.split("REGION_GROUP")[0]   # 두 변수 선언까지만
local_ns = {}
exec(chunk, local_ns)
VENUE_KEYWORDS = local_ns["VENUE_KEYWORDS"]
VENUE_DISTRICT = local_ns["VENUE_DISTRICT"]

def extract_venue(title):
    t = title.replace(" ", "")
    for kw, name in VENUE_KEYWORDS:
        if kw.replace(" ", "") in t:
            return name
    return None

venue_pat = re.compile(
    r"([가-힣a-zA-Z0-9]+(?:구장|운동장|체육공원|스타디움|경기장|공원축구장|체육센터|센터|배수지|둔치|인조잔디구장|잔디구장|푸른물센터|소체육공원|근린공원축구장))"
)

unmapped = {}
for p in posts:
    if extract_venue(p["title"]) is None:
        t = p["title"].replace(" ", "")
        t_clean = re.sub(r"^[\d\.\/\(\)월일토일요화수목금]+", "", t)
        t_clean = re.sub(r"^\d+시", "", t_clean)
        m = venue_pat.search(t_clean)
        if m:
            name = re.sub(r"^\d+", "", m.group(1))
            if len(name) >= 4:
                unmapped[name] = unmapped.get(name, 0) + 1

sorted_v = sorted(unmapped.items(), key=lambda x: -x[1])
total = sum(v for _, v in sorted_v)
print(f"미매핑 (장소 파악 가능): {len(sorted_v)}개 장소 / {total}개 게시물\n")
print("2회 이상:")
for v, cnt in sorted_v:
    if cnt >= 2:
        print(f"  {cnt:3d}회  {v}")
print("\n1회:")
for v, cnt in sorted_v:
    if cnt == 1:
        print(f"       {v}")
