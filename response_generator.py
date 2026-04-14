import json
import anthropic
from config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """당신은 한국 직장·대인관계 커뮤니케이션 전문 코치입니다.

주어진 원본 메시지, 감정 분석 결과, 답변자의 캐릭터 프로필, 상대방 프로필을 바탕으로
3가지 톤의 답변 초안을 생성합니다.

톤 정의:
1. 세련되게: 원래 의도는 살리되 감정을 빼고, 더 공식적이고 프로페셔널하게
2. 직접적으로: 감정을 솔직하게 표현하되 예의는 유지, 핵심 불만을 명확히 전달
3. 관계 유지: 감정을 최소화하고 부드럽게 조율, 관계 보존에 집중

중요:
- 답변자의 캐릭터 프로필이 있다면 그 말투와 성향을 최대한 반영하세요
- 상대방 프로필이 있다면 상대방의 성향을 고려해 답변 전략을 조정하세요
- 한국어로 자연스럽게 작성하세요
- 각 옵션은 실제로 보낼 수 있는 완성된 메시지여야 합니다

반드시 아래 JSON 배열 형식으로만 응답하세요 (설명 없이 JSON만):
[
  {
    "tone": "세련되게",
    "response": "실제 보낼 메시지 내용",
    "why": "이 톤을 선택했을 때의 효과 한 줄",
    "risk_level": "낮음 또는 보통 또는 높음"
  },
  {
    "tone": "직접적으로",
    "response": "실제 보낼 메시지 내용",
    "why": "이 톤을 선택했을 때의 효과 한 줄",
    "risk_level": "낮음 또는 보통 또는 높음"
  },
  {
    "tone": "관계 유지",
    "response": "실제 보낼 메시지 내용",
    "why": "이 톤을 선택했을 때의 효과 한 줄",
    "risk_level": "낮음 또는 보통 또는 높음"
  }
]"""


def generate_responses(
    original_text: str,
    emotion_result: dict,
    character_profile: str = "",
    opponent_profile: str = "",
) -> list[dict]:
    """3가지 톤의 답변 초안을 생성합니다."""

    profile_section = ""
    if character_profile.strip():
        profile_section = f"\n\n[내 캐릭터 프로필]\n{character_profile}"

    opponent_section = ""
    if opponent_profile.strip():
        opponent_section = f"\n\n[상대방 프로필]\n{opponent_profile}"

    emotions_summary = ""
    if emotion_result.get("emotions"):
        emotion_items = [
            f"{e['name']} ({e['intensity']}%)" for e in emotion_result["emotions"]
        ]
        emotions_summary = ", ".join(emotion_items)

    user_content = f"""[원본 메시지]
{original_text}

[감정 분석 결과]
- 감지된 감정: {emotions_summary}
- 전반적 상태: {emotion_result.get('overall_state', '')}
- 수신자 위험도: {emotion_result.get('receiver_risk', '')}
{profile_section}{opponent_section}

위 내용을 바탕으로 3가지 톤의 답변을 생성해주세요."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
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
        results = json.loads(cleaned.strip())
        if not isinstance(results, list):
            raise ValueError("Expected list")
        return results
    except (json.JSONDecodeError, ValueError):
        return [
            {
                "tone": "세련되게",
                "response": result_text,
                "why": "생성된 답변",
                "risk_level": "보통",
            }
        ]
