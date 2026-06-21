import streamlit as st
import google.generativeai as genai
import os

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="세컨드라이프 상담일지 AI 자동화", page_icon="📝", layout="wide")

st.title("📝 세컨드라이프팀 취업상담 일지 AI 입력기")
st.markdown("수기 메모한 상담 일지 사진(최대 3장)이나 PDF를 올리면, AI가 내용을 통합 분석하여 표준 양식에 맞게 변환해 줍니다.")
st.markdown("---")

# 2. API 키 설정
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

if GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.sidebar.warning("⚠️ API 키를 입력해주세요.")
    api_key_input = st.sidebar.text_input("Gemini API Key", type="password")
    if api_key_input:
        GOOGLE_API_KEY = api_key_input

if GOOGLE_API_KEY and GOOGLE_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.info("왼쪽 사이드바에 Gemini API Key를 입력하면 기능이 활성화됩니다.")
    st.stop()

# 3. 레이아웃 분할
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 수기상담 컨설턴트 업로드")
    uploaded_files = st.file_uploader(
        "상담일지 파일들을 선택하세요 (PNG, JPG, JPEG, PDF / 최대 3장)", 
        type=["png", "jpg", "jpeg", "pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files and len(uploaded_files) > 3:
        st.error("⚠️ 파일은 최대 3장까지만 업로드할 수 있습니다. 초과된 파일은 제외하고 분석을 시작해 주세요.")
        st.stop()

    image_parts = []
    if uploaded_files:
        for idx, file in enumerate(uploaded_files):
            file_bytes = file.getvalue()
            image_parts.append({
                "mime_type": file.type,
                "data": file_bytes
            })
            if file.type != "application/pdf":
                st.image(file_bytes, caption=f"업로드된 파일 {idx+1}: {file.name}", use_container_width=True)
            else:
                st.success(f"📄 PDF 파일 업로드 완료 ({idx+1}): {file.name}")

with col2:
    st.subheader("✨ AI 변환 및 구조화 결과")
    # 요구사항 반영: 상단의 빨간색 안내 박스를 제거하여 상담사 화면을 깔끔하게 유지합니다.

    if uploaded_files:
        if st.button("🚀 모든 메모 통합 분석 및 자동 입력 시작"):
            with st.spinner("AI가 모든 업로드 자료를 읽고 통합하여 최신 양식을 정리하는 중입니다..."):
                try:
                    # AI 프롬프트 (전달받은 모든 최신 필드 포함)
                    prompt = """
                    당신은 중장년 취업 지원 전문 기관인 '상상우리 세컨드라이프팀'의 스마트 업무 비서입니다.
                    제공된 파일들(최대 3장의 사진 또는 PDF)은 상담사가 상담 중에 필기한 '취업상담 일지' 메모 자료입니다.
                    여러 장에 나뉘어 있더라도 내용을 유기적으로 결합하고 정확히 판독(OCR)하여, 아래의 최신 '상담일지앱 표준 양식'에 맞게 채워서 출력해 주세요.

                    [작성 규칙]
                    1. 메모에 적힌 수기 글씨와 인쇄 텍스트를 모두 분석하여 정확하게 추출하세요.
                    2. 체크박스([ ]) 항목은 메모에 해당한다고 표시되어 있다면 [■] 또는 [v]로 변경하여 표시하세요.
                    3. 언급되지 않은 빈 칸이나 항목은 공란(빈칸)으로 유지하세요.

                    ---
                    [출력 양식 틀]
                    
                    ■ 1. 내담자 기본 정보
                    - 상담 일자: 
                    - 상담 회차: 
                    - 내담자명 / 출생년도: 
                    - 연락처 / 이메일: 
                    - 교육과정명: 
                    - 담당 상담사: 
                    - 현재 상태: [ ] 구직 중 [ ] 재직 중 [ ] 프리랜서 [ ] 개인사업자 [ ] 기타
                    
                    ■ 2. 교육 참여 동기 & 기대사항
                    - 참여 동기: 
                    - 기대하는 것: 
                    - 취업 의지: [ ] 매우 적극적 [ ] 적극적 [ ] 보통 [ ] 소극적 [ ] 취업 의향 없음 (교육 목적)
                    
                    ■ 3. 경력 및 역량
                    - 최종 직장 업종 / 직위: 
                    - 퇴직/이직 시점: 
                    - 경력 단절 여부: [ ] 없음 [ ] 있음 (기간: )
                    - 최근 5년 주요 업무 및 성과: 
                    - 보유 자격증 및 수료 교육: 
                    
                    ■ 4. 진로 방향 및 개인 상황
                    - 희망 방향: [ ] 동일직무 [ ] 유사분야 [ ] 완전전직 [ ] 창업/프리랜서 [ ] 미결정
                    - 희망 근무 형태: [ ] 정규직 [ ] 파트타임 [ ] 계약직 [ ] 프리랜서·긱워커 [ ] 상관없음
                    - 희망 분야/직무 (구체적으로): 
                    - 재미·흥미 느끼는 활동: 
                    - 경제적 시급성: [ ] 매우 시급 [ ] 시급 [ ] 보통 [ ] 여유 있음
                    - 건강 상태: [ ] 풀타임 가능 [ ] 하루 4~6시간 적합 [ ] 단시간·단발성 선호 [ ] 건강 이슈로 제한
                    - 특이사항 메모 (건강, 가족 지지 등): 
                    - 기타: 이전 상담·교육 이력
                    
                    ■ 5. 회차별 상담 내용 (메모가 해당하는 회차만 채우기)
                    - 주요 상담 주제: 
                    - 현재 상태 및 주요 내용: 
                    - 제공한 솔루션 / 정보: 
                    - 내담자 반응: 
                    - 다음 회차 계획: 
                    - 서류/지원 현황: 이력서 취합 [ ]완료 [ ]미완료 / 지원 ( )건 / 면접 ( )건
                    
                    ■ 6. 사후 관리 및 특이사항
                    - 취업 여부: [ ] 취업 완료 [ ] 구직 중 [ ] 구직 중단 [ ] 개인사업 [ ] 기타
                    - 취업처명 / 직무: 
                    - 취업 확인서: [ ] 수령 [ ] 미수령
                    - 사후 관리 메모: 
                    ---
                    """
                    
                    content_payload = [prompt] + image_parts
                    response = model.generate_content(content_payload)
                    ai_result = response.text
                    
                    st.success("✅ 모든 파일 통합 분석 완료!")
                    
                    st.text_area(
                        "아래 내용을 복사(Ctrl+A -> Ctrl+C)하여 통합 문서에 붙여넣으세요.", 
                        value=ai_result, 
                        height=580
                    )
                    
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                    st.caption("API 키가 올바른지, 혹은 파일에 문제가 없는지 확인해 주세요.")
    else:
        st.info("왼쪽 화면에서 파일(최대 3개)을 업로드해 주세요.")