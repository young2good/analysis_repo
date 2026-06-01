"""
Step 4 — Unique 장소 리스트 생성
Step 3(수동 작업) 완료된 venues_final_{BOARD_LABEL}_{DATE_FROM}_{DATE_TO}.xlsx 의
conflict_name 기준 unique 경기장 목록 + city 를 Excel로 저장.

사용법:
    python step4_make_unique_list.py
아래 CONFIG 블록만 수정하면 됨 (step1·2와 동일하게 맞출 것).
"""
from pathlib import Path

import pandas as pd

# ── CONFIG ───────────────────────────────────────────────────────────────────
BOARD_LABEL = "경기북부게시판"
DATE_FROM   = "2026-04-15"
DATE_TO     = "2026-04-30"
# ─────────────────────────────────────────────────────────────────────────────

BASE   = Path(__file__).parent
INPUT  = BASE / f"venues_final_{BOARD_LABEL}_{DATE_FROM}_{DATE_TO}.xlsx"
OUTPUT = BASE / f"unique_venues_{BOARD_LABEL}_{DATE_FROM}_{DATE_TO}.xlsx"

# 경기장명 → 시 수동 확정 매핑
VENUE_CITY = {
    "YMCA 축구장":                               "고양시",
    "감일축구장":                                 "하남시",
    "강남세곡체육공원축구장":                      "서울특별시",
    "걸포중앙공원축구장":                          "김포시",
    "경민대학교대운동장":                          "의정부시",
    "경복대학교 남양주캠퍼스운동장":               "남양주시",
    "고양고등학교운동장":                          "고양시",
    "교하체육공원 인조잔디축구장":                 "파주시",
    "구리시민스포츠센터축구장":                    "구리시",
    "구리왕숙체육공원 축구장":                     "구리시",
    "금남축구장":                                 "남양주시",
    "김포시종합운동장":                            "김포시",
    "남양주체육문화센터(종합운동장)메인스타디움":   "남양주시",
    "남양주체육문화센터(종합운동장)축구장 A구장":   "남양주시",
    "남양주체육문화센터(종합운동장)축구장 B구장":   "남양주시",
    "남양주체육문화센터(종합운동장)축구장 C구장":   "남양주시",
    "농협대학교운동장":                            "고양시",
    "다락원체육공원축구장":                        "의정부시",
    "다산체육공원 축구장":                         "남양주시",
    "대화동레포츠공원인조잔디축구장":              "고양시",
    "둔치축구":                                    "고양시",
    "먹골구장":                                   "남양주시",
    "문원체육공원운동장":                          "과천시",
    "불암산스포츠타운축구장":                      "서울특별시",
    "서울어린이대공원잔디축구장":                  "서울특별시",
    "성내유수지축구장":                            "서울특별시",
    "수도전기공업고등학교축구장":                  "서울특별시",
    "신내차량기지축구장":                          "서울특별시",
    "아차산배수지체육공원축구장":                  "서울특별시",
    "연세대학교 신촌캠퍼스대운동장":               "서울특별시",
    "와부공설운동장":                              "남양주시",
    "용마폭포공원축구장":                          "서울특별시",
    "운정건강공원(가온) 인조잔디축구장":            "파주시",
    "원능수질복원센터":                            "파주시",
    "은평구립축구장":                              "서울특별시",
    "인덕대학교운동장":                            "서울특별시",
    "진건푸른물센터인조잔디구장":                  "남양주시",
    "중랑구립잔디운동장":                          "서울특별시",
    "지금푸른물센터축구장":                        "구리시",
    "지영체육공원축구장":                          "고양시",
    "직동근린공원축구장":                          "의정부시",
    "초안산스포츠타운축구장":                      "서울특별시",
    "충장근린체육공원축구장":                      "고양시",
    "파주스타디움보조경기장":                      "파주시",
    "하남종합운동장 주경기장":                     "하남시",
    "하남종합운동장보조경기장":                    "하남시",
    "한국항공대학교운동장":                        "고양시",
    "활기체육공원축구장":                          "의정부시",
}


def main():
    if not INPUT.exists():
        print(f"파일 없음: {INPUT}")
        print("Step 3(수동 작업) 완료 후 파일명을 확인하세요.")
        return

    df = pd.read_excel(INPUT)

    df_out = (
        df[["conflict_name"]]
        .dropna(subset=["conflict_name"])
        .loc[lambda d: d["conflict_name"].astype(str).str.strip() != "-"]
        .drop_duplicates(subset="conflict_name")
        .sort_values("conflict_name")
        .reset_index(drop=True)
    )

    df_out["city"] = df_out["conflict_name"].map(VENUE_CITY).fillna("미확인")

    missing = df_out[df_out["city"] == "미확인"]
    if len(missing):
        print(f"⚠ city 미확인 {len(missing)}개 — VENUE_CITY 딕셔너리에 추가 필요:")
        for name in missing["conflict_name"]:
            print(f'    "{name}": "",')
    else:
        print("모든 경기장 city 매핑 완료")

    df_out.to_excel(OUTPUT, index=False)
    print(f"\nunique 경기장: {len(df_out)}개")
    print(f"저장: {OUTPUT}")


if __name__ == "__main__":
    main()
