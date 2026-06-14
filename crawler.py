import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.feelpoem.com"
BOARD_URL = "https://www.feelpoem.com/m11"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TARGET_COUNT = 100
OUTPUT_FILE = "poems.csv"


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_poem_content(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    fixed_lines = []

    for line in lines:
        # 숫자 한 글자, 한글/영문 한 글자, 구두점만 있는 줄은 앞줄에 붙이기
        if fixed_lines and re.match(r"^[가-힣A-Za-z0-9.,!?，。、]+$", line) and len(line) <= 2:
            fixed_lines[-1] += line
        else:
            fixed_lines.append(line)

    text = "\n".join(fixed_lines)

    # 쉼표/마침표 앞에 생기는 줄바꿈 제거
    text = re.sub(r"\s+\n\s*([,.!?，。、])", r"\1", text)

    return text.strip()

def get_soup(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def is_post_url(href):
    full_url = urljoin(BASE_URL, href)
    path = urlparse(full_url).path
    return re.match(r"^/m11/\d+$", path) is not None

def get_post_links(page_num):
    if page_num == 1:
        url = BOARD_URL
    else:
        url = f"{BOARD_URL}?page={page_num}"

    soup = get_soup(url)
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = clean_text(a.get_text())

        if is_post_url(href):
            full_url = urljoin(BASE_URL, href)

            # 공지 제외
            if "오늘의 시 등록 관련 안내" not in title:
                links.append(full_url)

    # 중복 제거
    links = list(dict.fromkeys(links))
    print(f"  찾은 게시글 링크 수: {len(links)}")
    return links

def split_poet_and_title(raw_title):
    raw_title = clean_text(raw_title)

    raw_title = raw_title.replace("> 오늘의 시 | 시와 그리움이 있는 마을", "")
    raw_title = raw_title.replace("오늘의 시 | 시와 그리움이 있는 마을", "")
    raw_title = raw_title.strip()

    poet = ""
    title = raw_title

    # 서효인 시 <친척과 천적>
    match1 = re.search(r"(.+?)\s*시\s*<(.+?)>", raw_title)
    if match1:
        poet = clean_text(match1.group(1))
        title = clean_text(match1.group(2))
        return poet, title
    
    return clean_text(poet), clean_text(title)  # 혹시 제목 형식이 이상하게 들어올 것 대비 중복 정제

def get_poem_detail(url):
    soup = get_soup(url)

    # 제목
    h2_tags = soup.find_all("h2")
    raw_title = ""

    for h2 in h2_tags:
        text = clean_text(h2.get_text())
        if "시 <" in text:
            raw_title = text
            break

    if not raw_title:
        page_title = soup.find("title")
        raw_title = clean_text(page_title.get_text()) if page_title else ""

    poet, title = split_poet_and_title(raw_title)

    # 본문 추출
    body_text = ""

    content_area = soup.find(id="bo_v_con")

    if content_area:
        body_text = content_area.get_text("\n", strip=True)
    else:
        text = soup.get_text("\n", strip=True)
        if "본문" in text:
            body_text = text.split("본문", 1)[1]

    body_text = clean_poem_content(body_text)

    # 너무 짧거나 목록 텍스트가 섞인 경우 제외하기 위함
    if len(body_text) < 30:
        return None

    return {
        "title": title,
        "poet": poet,
        "content": body_text,
        "url": url,
        "source": "시와 그리움이 있는 마을 - 오늘의 시"
    }


def crawl_poems(target_count=TARGET_COUNT):
    poems = []
    visited = set()
    page = 1

    while len(poems) < target_count:
        print(f"\n[목록 수집] {page}페이지 확인 중...")
        post_links = get_post_links(page)

        if not post_links:
            print("게시글 링크를 찾지 못했습니다. 종료합니다.")
            break

        for link in post_links:
            if link in visited:
                continue

            visited.add(link)

            try:
                poem = get_poem_detail(link)

                if poem:
                    poems.append(poem)
                    print(f"{len(poems)}/{target_count} 수집 완료: {poem['poet']} - {poem['title']}")

                if len(poems) >= target_count:
                    break

                time.sleep(1)

            except Exception as e:
                print(f"오류 발생: {link}")
                print(e)
                continue

        page += 1
        time.sleep(1)

    return poems


if __name__ == "__main__":
    poems = crawl_poems(TARGET_COUNT)

    df = pd.DataFrame(poems)
    df.drop_duplicates(subset=["url"], inplace=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\n크롤링 완료!")
    print(f"저장 파일: {OUTPUT_FILE}")
    print(f"수집 개수: {len(df)}개")