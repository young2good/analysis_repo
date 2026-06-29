"""
Step 5 — venue dimension 빌드

1) 기존 alias 매핑 (venues_final.xlsx) + 새 리뷰 완료 파일 병합
   - 병합 결과: alias_mapping.xlsx  (venue_confirm, city, conflict_name)
2) conflict_name unique 기준으로 경기장 dimension 생성
   - 결과: venue_dimension.xlsx  (conflict_name, city)
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent

EXISTING   = BASE / "venues_final.xlsx"
NEW_REVIEW = Path(r"E:\downloads\new_venues_to_review_(완료).xlsx")
OUT_ALIAS  = BASE / "alias_mapping.xlsx"
OUT_DIM    = BASE / "venue_dimension.xlsx"

# ── 1) 기존 alias 매핑 로드 ───────────────────────────────────────────────────
df_existing = pd.read_excel(EXISTING)[["venue_confirm", "city", "conflict_name"]]
print(f"기존 alias: {len(df_existing)}행")

# ── 2) 새 리뷰 파일 로드 + 컬럼 맞추기 ──────────────────────────────────────
df_new = pd.read_excel(NEW_REVIEW)

# venue_confirm이 비어있거나 '????' 인 행 제외
df_new = df_new[
    df_new["venue_confirm"].notna() &
    (df_new["venue_confirm"].astype(str).str.strip() != "") &
    (df_new["venue_confirm"].astype(str).str.strip() != "????")
].copy()

df_new = df_new.rename(columns={
    "venue_candidate": "venue_confirm",
    "venue_confirm":   "conflict_name",
})
df_new = df_new[["venue_confirm", "city", "conflict_name"]]
print(f"새 alias: {len(df_new)}행")

# ── 3) 병합 + venue_confirm 기준 중복 제거 ───────────────────────────────────
df_alias = (
    pd.concat([df_existing, df_new], ignore_index=True)
    .drop_duplicates(subset="venue_confirm")
    .sort_values("venue_confirm")
    .reset_index(drop=True)
)
print(f"병합 후 alias: {len(df_alias)}행")
df_alias.to_excel(OUT_ALIAS, index=False)
print(f"저장: {OUT_ALIAS}")

# ── 4) conflict_name unique 기준 경기장 dimension ────────────────────────────
df_dim = (
    df_alias[df_alias["conflict_name"].notna() &
             (df_alias["conflict_name"].astype(str).str.strip() != "") &
             (df_alias["conflict_name"].astype(str).str.strip() != "NaN")]
    [["conflict_name", "city"]]
    .drop_duplicates(subset="conflict_name")
    .sort_values("conflict_name")
    .reset_index(drop=True)
)

missing_city = (df_dim["city"] == "미확인").sum()
print(f"\n경기장 dimension: {len(df_dim)}개  (city 미확인: {missing_city}개)")
if missing_city:
    print("미확인 목록:")
    print(df_dim[df_dim["city"] == "미확인"]["conflict_name"].tolist())

df_dim.to_excel(OUT_DIM, index=False)
print(f"저장: {OUT_DIM}")
