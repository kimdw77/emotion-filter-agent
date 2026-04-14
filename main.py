import streamlit as st
from emotion_analyzer import analyze_emotion
from response_generator import generate_responses
from character_profile import (
    save_profile,
    load_profile,
    get_presets,
    save_opponent_profile,
    load_opponent_profile,
    get_opponent_presets,
)

st.set_page_config(
    page_title="내 눈에 필터!",
    page_icon="💬",
    layout="wide",
)

# ──────────────────────────────────────────────
# CSS 스타일
# ──────────────────────────────────────────────
st.markdown(
    """
<style>
.emotion-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #6c63ff;
}
.response-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    border: 1.5px solid #e0e0e0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.tone-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
}
.risk-low  { background: #d4edda; color: #155724; }
.risk-mid  { background: #fff3cd; color: #856404; }
.risk-high { background: #f8d7da; color: #721c24; }
.tone-elegant { background: #e8eaf6; color: #3949ab; }
.tone-direct  { background: #fce4ec; color: #c62828; }
.tone-relation{ background: #e8f5e9; color: #2e7d32; }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 세션 상태 초기화
# ──────────────────────────────────────────────
if "profile" not in st.session_state:
    st.session_state.profile = load_profile()
if "opponent_profile" not in st.session_state:
    st.session_state.opponent_profile = load_opponent_profile()
if "emotion_result" not in st.session_state:
    st.session_state.emotion_result = None
if "responses" not in st.session_state:
    st.session_state.responses = None


# ──────────────────────────────────────────────
# 사이드바 — 캐릭터 프로필 설정
# ──────────────────────────────────────────────
with st.sidebar:
    # ── 내 프로필 ──
    st.header("👤 내 프로필")
    st.caption("나의 말투·성향을 설정하면 답변 제안에 반영됩니다.")

    my_tab1, my_tab2 = st.tabs(["✏️ 직접 입력", "🎭 프리셋"])

    with my_tab1:
        text_input = st.text_area(
            "나의 말투·성향 묘사",
            value=st.session_state.profile,
            height=120,
            placeholder='예: "나는 논리적이고 직설적인 편이다. 감정보다 사실 중심으로 말하고 싶어한다."',
            key="profile_text_input",
        )
        if st.button("💾 저장", key="save_text"):
            st.session_state.profile = text_input
            save_profile(text_input)
            st.success("저장됐습니다!")

    with my_tab2:
        presets = get_presets()
        selected_preset = st.selectbox(
            "유형 선택",
            options=list(presets.keys()),
            key="preset_select",
        )
        st.caption(presets[selected_preset])
        if st.button("✅ 이 프리셋 사용", key="use_preset"):
            st.session_state.profile = presets[selected_preset]
            save_profile(presets[selected_preset])
            st.success(f"'{selected_preset}' 적용됐습니다!")

    if st.session_state.profile:
        st.info(st.session_state.profile[:80] + ("..." if len(st.session_state.profile) > 80 else ""))
    else:
        st.warning("미설정")

    st.divider()

    # ── 상대방 프로필 ──
    st.header("🧑‍🤝‍🧑 상대방 프로필")
    st.caption("상대방의 성향을 설정하면 더 정확한 답변을 제안합니다.")

    opp_tab1, opp_tab2 = st.tabs(["✏️ 직접 입력", "🎭 프리셋"])

    with opp_tab1:
        opp_text_input = st.text_area(
            "상대방 성향 묘사",
            value=st.session_state.opponent_profile,
            height=120,
            placeholder='예: "직장 상사로 권위적인 편이다. 감정 표현 없이 지시만 한다."',
            key="opponent_text_input",
        )
        if st.button("💾 저장", key="save_opp_text"):
            st.session_state.opponent_profile = opp_text_input
            save_opponent_profile(opp_text_input)
            st.success("저장됐습니다!")

    with opp_tab2:
        opp_presets = get_opponent_presets()
        selected_opp_preset = st.selectbox(
            "유형 선택",
            options=list(opp_presets.keys()),
            key="opp_preset_select",
        )
        st.caption(opp_presets[selected_opp_preset])
        if st.button("✅ 이 프리셋 사용", key="use_opp_preset"):
            st.session_state.opponent_profile = opp_presets[selected_opp_preset]
            save_opponent_profile(opp_presets[selected_opp_preset])
            st.success(f"'{selected_opp_preset}' 적용됐습니다!")

    if st.session_state.opponent_profile:
        st.info(st.session_state.opponent_profile[:80] + ("..." if len(st.session_state.opponent_profile) > 80 else ""))
    else:
        st.warning("미설정")


# ──────────────────────────────────────────────
# 메인 영역
# ──────────────────────────────────────────────
st.title("💬 내 눈에 필터!")
st.markdown("상대방 메시지를 붙여넣으면 **감정을 분석**하고 **내 캐릭터에 맞는 답변 3가지**를 제안합니다.")

message_input = st.text_area(
    "분석할 메시지를 입력하세요",
    height=160,
    placeholder="상대방이 보낸 문자·카톡·슬랙 메시지를 여기 붙여넣으세요...",
    key="message_input",
)

col1, col2 = st.columns([1, 5])
with col1:
    analyze_btn = st.button("🔍 분석하기", type="primary", use_container_width=True)

if analyze_btn:
    if not message_input.strip():
        st.warning("메시지를 입력해주세요.")
    else:
        # 감정 분석
        with st.spinner("감정 분석 중..."):
            st.session_state.emotion_result = analyze_emotion(message_input)

        # 답변 생성
        with st.spinner("답변 초안 생성 중..."):
            st.session_state.responses = generate_responses(
                original_text=message_input,
                emotion_result=st.session_state.emotion_result,
                character_profile=st.session_state.profile,
                opponent_profile=st.session_state.opponent_profile,
            )

# ──────────────────────────────────────────────
# 감정 분석 결과 표시
# ──────────────────────────────────────────────
if st.session_state.emotion_result:
    er = st.session_state.emotion_result
    st.divider()
    st.subheader("🧠 감정 분석 결과")

    # 감정 게이지
    emotions = er.get("emotions", [])
    if emotions:
        cols = st.columns(min(len(emotions), 4))
        for i, emotion in enumerate(emotions[:4]):
            with cols[i]:
                intensity = emotion.get("intensity", 0)
                name = emotion.get("name", "")
                evidence = emotion.get("evidence", "")
                st.metric(label=name, value=f"{intensity}%")
                st.progress(intensity / 100)
                if evidence:
                    st.caption(f'근거: "{evidence}"')

    # 전반적 상태
    overall = er.get("overall_state", "")
    if overall:
        st.markdown(
            f'<div class="emotion-card">📊 <b>전반적 상태:</b> {overall}</div>',
            unsafe_allow_html=True,
        )

    # 어조 경고
    tone_alert = er.get("tone_alert")
    if tone_alert:
        st.warning(f"⚠️ **어조 포인트:** {tone_alert}")

    # 수신자 위험도
    receiver_risk = er.get("receiver_risk", "")
    if receiver_risk:
        st.error(f"📩 **상대방이 받을 때:** {receiver_risk}")


# ──────────────────────────────────────────────
# 답변 제안 표시
# ──────────────────────────────────────────────
if st.session_state.responses:
    st.divider()
    st.subheader("✍️ 3가지 답변 제안")

    tone_styles = {
        "세련되게": ("tone-elegant", "💎"),
        "직접적으로": ("tone-direct", "🎯"),
        "관계 유지": ("tone-relation", "🤝"),
    }
    risk_styles = {
        "낮음": "risk-low",
        "보통": "risk-mid",
        "높음": "risk-high",
    }

    for i, resp in enumerate(st.session_state.responses):
        tone = resp.get("tone", f"옵션 {i+1}")
        response_text = resp.get("response", "")
        why = resp.get("why", "")
        risk = resp.get("risk_level", "보통")

        tone_class, tone_icon = tone_styles.get(tone, ("tone-elegant", "💬"))
        risk_class = risk_styles.get(risk, "risk-mid")

        st.markdown(
            f"""
<div class="response-card">
  <span class="tone-badge {tone_class}">{tone_icon} {tone}</span>
  <span class="tone-badge {risk_class}" style="margin-left:8px;">위험도: {risk}</span>
  <p style="margin:10px 0 6px 0; font-size:15px; line-height:1.6;">{response_text}</p>
  <p style="color:#888; font-size:13px; margin:0;">💡 {why}</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.code(response_text, language=None)

    st.caption("💡 코드 블록 오른쪽 상단 복사 버튼으로 바로 복사할 수 있습니다.")
