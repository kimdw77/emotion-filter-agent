import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-opus-4-6"
PROFILE_PATH = "character_profile.json"

PRESETS = {
    "팩트형 직장인": "나는 논리와 사실 중심으로 말하는 편이다. 감정 표현은 절제하고, 핵심을 간결하게 전달하려 한다. 감정보다 상황과 사실에 집중한다.",
    "따뜻한 공감형": "나는 상대방의 감정을 중요하게 생각하고 관계를 소중히 여긴다. 부드럽고 배려 있는 표현을 선호하며, 갈등보다 화합을 추구한다.",
    "냉철한 비즈니스형": "나는 간결하고 중립적이며 전문적인 톤을 유지한다. 개인 감정을 드러내지 않고 업무적 관점에서 소통한다.",
    "유머감각 있는 편": "나는 가끔 가벼운 유머나 친근한 표현을 섞어 분위기를 부드럽게 만든다. 딱딱하지 않고 인간적인 소통을 선호한다.",
}
