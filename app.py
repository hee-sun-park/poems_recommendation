import streamlit as st
from recommender import recommend_poems
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
from pathlib import Path

BASE_DIR = Path(__file__).parent

# 부정적인 감정을 위로하는 데 초점을 맞추기 위해 기본 상태를 "슬픔"으로 설정
def get_main_emotion(user_emotions):
    if sum(user_emotions.values()) == 0:
        return "슬픔"
    return max(user_emotions, key=user_emotions.get)


def make_mini_comment(user_emotions, poem):
    main_emotion = get_main_emotion(user_emotions)

    if main_emotion == "기쁨":
        return "기쁜 마음을 더 밝게 확장해 줄 수 있는 구절이에요. 희망과 사랑의 결이 함께 느껴져서 오늘의 감정과 잘 어울려요."

    if main_emotion == "슬픔":
        return "슬픔을 억지로 지우기보다 조용히 바라보게 해주는 구절이에요. 지금 마음에 작은 위로가 될 수 있어요."

    if main_emotion == "외로움":
        return "혼자 있는 마음을 다정하게 감싸는 구절이에요. 외로움 속에서도 누군가와 연결되어 있다는 느낌을 줄 수 있어요."

    if main_emotion == "희망":
        return "다시 앞으로 걸어가고 싶은 마음과 잘 맞는 구절이에요. 작지만 분명한 회복감을 전해줘요."

    if main_emotion == "절망":
        return "너무 깊이 가라앉지 않도록 붙잡아주는 구절이에요. 지금은 이 문장이 조용한 버팀목처럼 느껴질 수 있어요."

    return "입력한 감정 조합과 가장 잘 맞는 시 구절을 골랐어요."


MUSIC_BY_EMOTION = {
    "기쁨": "https://www.youtube.com/watch?v=V9PVRfjEBTI",
    "슬픔": "https://www.youtube.com/watch?v=IpFX2vq8HKw",
    "외로움": "https://www.youtube.com/watch?v=7ihLv8_Vd-4",
    "희망": "https://www.youtube.com/watch?v=6LDg0YGYVw4",
    "절망": "https://www.youtube.com/watch?v=5a-tqIQc8RM",
}

def create_emotion_card(poem, memo, main_emotion):
    width, height = 900, 2500

    bg_colors = {
        "기쁨": (255, 245, 210),
        "슬픔": (220, 230, 245),
        "외로움": (230, 225, 240),
        "희망": (225, 245, 225),
        "절망": (215, 215, 225),
    }

    bg_color = bg_colors.get(main_emotion, (245, 240, 235))

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font_path = BASE_DIR / "나눔손글씨 다행체.ttf"

        title_font = ImageFont.truetype(
            str(font_path),
            40
        )

        body_font = ImageFont.truetype(
            str(font_path),
            32
        )

        small_font = ImageFont.truetype(
            str(font_path),
            26
        )

    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 카드 테두리
    margin = 60
    draw.rounded_rectangle(
        [margin, margin, width - margin, height - margin],
        radius=35,
        outline=(120, 120, 120),
        width=3
    )

    y = 120

    draw.text((90, y), "오늘의 감정 카드", font=title_font, fill=(50, 50, 50))
    y += 90

    draw.text((90, y), f"{poem['title']} - {poem['poet']}", font=small_font, fill=(70, 70, 70))
    y += 70

    quote = str(poem["대표 구절"]).replace("//", "\n\n")
    wrapped_quote = []

    for line in quote.split("\n"):
        wrapped_quote.extend(textwrap.wrap(line, width=24) if line.strip() else [""])

    for line in wrapped_quote[:18]:
        draw.text((90, y), line, font=body_font, fill=(30, 30, 30))
        y += 48

    y += 40

    draw.line((90, y, width - 90, y), fill=(150, 150, 150), width=2)
    y += 50

    draw.text((90, y), "오늘의 내 생각", font=small_font, fill=(70, 70, 70))
    y += 50

    memo = memo.strip() if memo else "오늘의 마음을 기록해 보세요."
    wrapped_memo = textwrap.wrap(memo, width=25)

    for line in wrapped_memo[:8]:
        draw.text((90, y), line, font=body_font, fill=(50, 50, 50))
        y += 48

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

st.set_page_config(page_title="오늘의 시 구절", page_icon="🌙")

st.title("오늘의 마음에 어울리는 시 구절")
st.write("지금 마음에 가까운 감정을 조절해 주세요.")

joy = st.slider("기쁨", 0, 100, 0)
sadness = st.slider("슬픔", 0, 100, 0)
loneliness = st.slider("외로움", 0, 100, 0)
hope = st.slider("희망", 0, 100, 0)
despair = st.slider("절망", 0, 100, 0)

with st.expander("📚 데이터 설명"):
    st.write("""
    이 웹앱은 직접 수집한 현대시 100편을 활용합니다.

    각 시에는 희망, 위로, 사랑, 섬세함, 슬픔의 5개 감정 태그 점수를 부여했고,
    사용자에게 보여줄 대표 구절을 따로 추출했습니다.
    여기서의 섬세함은 '감각적 이미지, 사물 묘사, 미묘한 정서 표현이 두드러지는 정도'를 의미합니다.

    저작권 문제를 고려하여 시 전문은 화면에 출력하지 않고,
    추천 결과에는 대표 구절만 제공합니다.
    """)

with st.expander("⚙️ 분석 및 추천 방법"):
    st.write("""
    사용자는 기쁨, 슬픔, 외로움, 희망, 절망 슬라이더로 현재 감정을 입력합니다.

    입력된 감정은 시 데이터의 감정 태그와 연결됩니다.

    - 기쁨 → 희망, 사랑
    - 슬픔 → 위로, 슬픔, 섬세함
    - 외로움 → 위로, 사랑, 섬세함
    - 희망 → 희망
    - 절망 → 희망, 위로, 낮은 슬픔

    이후 각 시의 감정 태그 점수와 사용자 감정 수치를 비교하여\n
    가장 잘 어울리는 시 구절을 추천합니다.
    
    모든 슬라이더 값이 0인 경우,\n
    웹앱의 사용자 중 위로받고 싶은 사람들이 더 많을 것을 고려하여\n
    가장 높은 감정을 '슬픔'으로 설정하였습니다.
    """)

if st.button("오늘의 시 구절 추천받기"):

    user_emotions = {
        "기쁨": joy,
        "슬픔": sadness,
        "외로움": loneliness,
        "희망": hope,
        "절망": despair,
    }

    main_emotion = get_main_emotion(user_emotions)
    poem = recommend_poems(user_emotions, top_n=1).iloc[0]
    comment = make_mini_comment(user_emotions, poem)

    st.session_state["poem"] = poem
    st.session_state["comment"] = comment
    st.session_state["main_emotion"] = main_emotion

if "poem" in st.session_state:
    poem = st.session_state["poem"]
    comment = st.session_state["comment"]
    main_emotion = st.session_state["main_emotion"]

    left, right = st.columns(2)

    with left:
        st.subheader("추천 시 구절")
        st.markdown(f"""
### {poem['title']}
**{poem['poet']}**

{poem['대표 구절']}
""")

    with right:
        st.subheader("미니 코멘트")
        st.write(comment)

        st.subheader("어울리는 음악")
        st.video(MUSIC_BY_EMOTION[main_emotion])

    st.divider()

    st.subheader("📊 분석 결과")
    st.write(f"""
    현재 입력된 감정 중 가장 높은 감정은 **{main_emotion}** 입니다.

    추천된 시는 사용자의 감정 조합과 시의 감정 태그 점수가 가장 잘 맞는 작품입니다.
    이 추천은 직접 추출한 대표 구절과 감정 태그 점수를 기준으로 이루어졌습니다.
    """)

    memo = st.text_area("이 문장을 보고 떠오른 생각을 적어보세요")

    if st.button("감정 카드 만들기"):
        card_image = create_emotion_card(poem, memo, main_emotion)

        st.image(card_image, caption="생성된 감정 카드", use_container_width=True)

        st.download_button(
            label="감정 카드 다운로드하기",
            data=card_image,
            file_name="emotion_card.png",
            mime="image/png"
        )