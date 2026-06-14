import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

df = pd.read_excel(
    BASE_DIR / "poems_tagged.xlsx"
)


def calculate_mixed_score(row, user_emotions):
    score = 0

    # 기쁨 → 희망, 사랑
    score += user_emotions["기쁨"] * (
        row["희망"] * 0.55 + row["사랑"] * 0.45
    )

    # 슬픔 → 위로, 슬픔, 섬세함
    score += user_emotions["슬픔"] * (
        row["위로"] * 0.45 + row["슬픔"] * 0.25 + row["섬세함"] * 0.30
    )

    # 외로움 → 위로, 사랑, 섬세함
    score += user_emotions["외로움"] * (
        row["위로"] * 0.40 + row["사랑"] * 0.35 + row["섬세함"] * 0.25
    )

    # 희망 → 희망
    score += user_emotions["희망"] * (
        row["희망"] * 1.0
    )

    # 절망 → 희망, 위로, 낮은 슬픔
    score += user_emotions["절망"] * (
        row["희망"] * 0.55 + row["위로"] * 0.45 - row["슬픔"] * 0.30
    )

    return score


def recommend_poems(user_emotions, top_n=1):
    temp = df.copy()

    if sum(user_emotions.values()) == 0:
        user_emotions = {
            "기쁨": 0,
            "슬픔": 30,
            "외로움": 30,
            "희망": 20,
            "절망": 0,
        }

    temp["score"] = temp.apply(
        lambda row: calculate_mixed_score(row, user_emotions),
        axis=1
    )

    temp = temp.sort_values("score", ascending=False)

    candidates = temp.head(15)

    return candidates.sample(
        n=min(top_n, len(candidates))
    )