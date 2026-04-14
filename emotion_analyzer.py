import json
import anthropic
from config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """당신은 한국 직장·대인관계 문자/메신저 감정 분석 전문가입니다.

주어진 텍스트에서 보내는 사람의 감정 상태를 문맥적으로 분석합니다.

분석 원칙:
- 한국어 특유의 감정 표현에 민감하게 반응하십시오 (ㅎㅎ, ㅋㅋ, 암튼, ... 등)
- 표면적 예의와 실제 감정이 다를 수 있음을 고려하십시오
- 직장 내 위계관계, 업무 맥락을 반영하십시오
- 감정 강도를 0-100으로 수치화하십시오

반드시 아래 JSON 형식으로만 응답하십시오 (설명 없이 JSON만):
{
  "emotions": [
    {
      "name": "감정명(한국어)",
      "intensity": 숫자(0-100),
      "evidence": "근거가 된 문장/표현"
    }
  ],
  "overall_state": "전반적 감정 상태 한 줄 요약",
  "tone_alert": "특이한 어조/표현 분석 (없으면 null)",
  "receiver_risk": "상대방이 받았을 때 느낄 수 있는 감정"
}"""


def analyze_emotion(text: str) -> dict:
    """텍스트의 감정을 분석하여 구조화된 결과를 반환합니다."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"다음 메시지의 감정을 분석해주세요:\n\n{text}",
            }
        ],
    )

    # 텍스트 블록만 추출
    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text = block.text
            break

    # JSON 파싱
    try:
        # 마크다운 코드블록 제거
        cleaned = result_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        result = json.loads(cleaned.strip())
    except json.JSONDecodeError:
        # 파싱 실패 시 기본값 반환
        result = {
            "emotions": [{"name": "분석 불가", "intensity": 0, "evidence": result_text}],
            "overall_state": "분석 중 오류가 발생했습니다.",
            "tone_alert": None,
            "receiver_risk": "알 수 없음",
        }

    return result
