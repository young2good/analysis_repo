"""게시글 제목에서 경기 날짜·시간을 추출하는 모듈.

parse_posts.py 파이프라인에서 사용한다.
"""
import re


def extract_date(title: str) -> str:
    m = re.search(r'(\d{1,2})월\s*(\d{1,2})일?', title)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.search(r'(\d{1,2})[./]\s*(\d{1,2})', title)
    if m:
        return f"{int(m.group(1))}/{int(m.group(2))}"
    m = re.search(r'(\d{1,2})월', title)
    if m:
        return f"{m.group(1)}월"
    return ""


def extract_time(title: str) -> str:
    m = re.search(r'(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})', title)
    if m:
        return f"{m.group(1)}~{m.group(2)}"
    m = re.search(r'(오전|오후)?\s*(\d{1,2})\s*[~\-]\s*(\d{1,2})\s*시', title)
    if m:
        prefix = m.group(1) or ""
        return f"{prefix}{m.group(2)}~{m.group(3)}시"
    m = re.search(r'(\d{1,2})시\s*[-~]\s*(\d{1,2})시', title)
    if m:
        return f"{m.group(1)}~{m.group(2)}시"
    m = re.search(r'\b(\d{1,2})\s*[~\-]\s*(\d{1,2})\b', title)
    if m and int(m.group(1)) <= 24 and int(m.group(2)) <= 24:
        return f"{m.group(1)}~{m.group(2)}시"
    m = re.search(r'(\d{1,2})시', title)
    if m:
        return f"{m.group(1)}시"
    return ""
