import json
import base64
import os
from io import BytesIO
import anthropic
from config import ANTHROPIC_API_KEY, MODEL, PROFILE_PATH, OPPONENT_PROFILE_PATH, PRESETS, OPPONENT_PRESETS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SCREENSHOT_SYSTEM = """당신은 카카오톡, 슬랙, 문자 등 메신저 대화 스크린샷을 분석하여
특정 사람의 말투와 소통 성향을 파악하는 전문가입니다.

이미지에서 한 사람의 말투를 분석하여 아래 형식으로만 응답하세요 (JSON):
{
  "style_summary": "말투 특성 2-3문장 요약",
  "characteristics": ["특성1", "특성2", "특성3"]
}"""


def analyze_chat_screenshot(image_bytes: bytes, media_type: str = "image/png") -> str:
    """채팅 스크린샷 이미지를 분석하여 말투 특성 텍스트를 반환합니다."""
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SCREENSHOT_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "이 대화에서 파란색(또는 오른쪽) 말풍선 주인의 말투와 소통 성향을 분석해주세요.",
                    },
                ],
            }
        ],
    )

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text = block.text
            break

    try:
        cleaned = result_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned.strip())
        summary = data.get("style_summary", "")
        characteristics = data.get("characteristics", [])
        if characteristics:
            summary += " 주요 특성: " + ", ".join(characteristics)
        return summary
    except (json.JSONDecodeError, KeyError):
        return result_text


def save_profile(profile_text: str) -> None:
    """캐릭터 프로필을 JSON 파일에 저장합니다."""
    data = {"profile": profile_text}
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_profile() -> str:
    """저장된 캐릭터 프로필을 불러옵니다. 없으면 빈 문자열 반환."""
    if not os.path.exists(PROFILE_PATH):
        return ""
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("profile", "")
    except (json.JSONDecodeError, IOError):
        return ""


def get_presets() -> dict:
    """사전 정의된 캐릭터 프리셋을 반환합니다."""
    return PRESETS


def save_opponent_profile(profile_text: str) -> None:
    """상대방 프로필을 JSON 파일에 저장합니다."""
    data = {"profile": profile_text}
    with open(OPPONENT_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_opponent_profile() -> str:
    """저장된 상대방 프로필을 불러옵니다. 없으면 빈 문자열 반환."""
    if not os.path.exists(OPPONENT_PROFILE_PATH):
        return ""
    try:
        with open(OPPONENT_PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("profile", "")
    except (json.JSONDecodeError, IOError):
        return ""


def get_opponent_presets() -> dict:
    """사전 정의된 상대방 프리셋을 반환합니다."""
    return OPPONENT_PRESETS
