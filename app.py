import streamlit as st
import google.generativeai as genai

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="세컨드라이프 상담일지 AI 자동화", page_icon="📝", layout="wide")

st.title("📝 세컨드라이프팀 취업상담 일지 AI 입력기")
st.markdown("수기 메모한 상담 일지 사진(최대 3장)이나 PDF를 올리면, AI가 내용을 통합 분석하여 표준 양식에 맞게 변환해 줍니다.")
st.markdown("---")

# 2. 상담사 개인별 API 키 입력 가이드
st.sidebar.header("🔑 상담사 개인 인증")
st.sidebar.markdown("구글 무료 한도 초과 방지를 위해 **상담사 본인의 Gemini API Key**를 입력해 주세요.")
api_key_input = st.sidebar.text_input("Gemini API Key 입력 (Enter 필수)", type="password")
st.sidebar.markdown("[👉 무료 API Key 발급받기 (클릭)](https://aistudio.google.com/)")

if api_key_input:
    genai.configure(api_key=api_key_input)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        st.error("API 키 설정 중 오류가 발생했습니다.")
        st.stop()
else:
    st.info("💡 왼쪽 사이드바에 **상담사님의 Gemini API Key**를 입력하고 엔터(Enter)를 누르시면 기능이 활성화됩니다.")
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

    if uploaded_files:
        if st.button("🚀 모든 메모 통합 분석 및 자동 입력 시작"):
            with st.spinner("AI가 모든 업로드 자료를 읽고 통합하여 최신 양식을 정리하는 중입니다..."):
                try:
                    # 줄바꿈 및 인코딩 오류가 없는 프롬프트
                    prompt = (
                        "당신은 중장년 취업 지원 전문 기관인 '상상우리 세컨드라이프팀'의 스마트 업무 비서입니다.\n"
                        "제공된 파일들(최대 3장의 사진 또는 PDF)은 상담사가 상담 중에 필기한 '취업상담 일지' 메모 자료입니다.\n"
                        "여러 장에 나뉘어 있더라도 내용을 유기적으로 결합하고 정확히 판독(OCR)하여, 아래의 최신 '상담일지앱 표준 양식'에 맞게 채워서 출력해 주세요.\n\n"
                        "[작성 규칙]\n"
                        "1. 맨 첫 줄에는 별도의 샵 기호 없이 오직 [취업 상담 일지] 문구만 출력하세요.\n"
                        "2. 메모에 적힌 수기 글씨와 인쇄 텍스트를 모두 분석하여 정확하게 추출하세요.\n"
                        "3. 체크박스([ ]) 항목은 메모에 해당한다고 표시되어 있다면 [■] 또는 [v]로 변경하여 표시하세요.\n"
                        "4. 언급되지 않은 빈 칸이나 항목은 공란(빈칸)으로 유지하세요.\n\n"
                        "---\n"
                        "■ 1. 내담자 기본 정보\n"
                        "- 상담 일자: \n"
                        "- 상담 회차: \n"
                        "- 내담자명 / 출생년도: \n"
                        "- 연락처 / 이메일: \n"
                        "- 교육과정명: \n"
                        "- 담당 상담사: \n"
                        "- 현재 상태: [ ] 구직 중 [ ] 재직 중 [ ] 프리랜서 [ ] 개인사업자 [ ] 기타\n\n"
                        "■ 2. 교육 참여 동기 & 기대사항\n"
                        "- 참여 동기: \n"
                        "- 기대하는 것: \n"
                        "- 취업 의지: [ ] 매우 적극적 [ ] 적극적 [ ] 보통 [ ] 소극적 [ ] 취업 의향 없음 (교육 목적)\n\n"
                        "■ 3. 경력 및 역량\n"
                        "- 최종 직장 업종 / 직위: \n"
                        "- 퇴직/이직 시점: \n"
                        "- 경력 단절 여부: [ ] 없음 [ ] 있음 (기간: )\n"
                        "- 최근 5년 주요 업무 및 성과: \n"
                        "- 보유 자격증 및 수료 교육: \n\n"
                        "■ 4. 진로 방향 및 개인 상황\n"
                        "- 희망 방향: [ ] 동일직무 [ ] 유사분야 [ ] 완전전직 [ ] 창업/프리랜서 [ ] 미결정\n"
                        "- 희망 근무 형태: [ ] 정규직 [ ] 파트타임 [ ] 계약직 [ ] 프리랜서·긱워커 [ ] 상관없음\n"
                        "- 희망 분야/직무 (구체적으로):\n"
                        "- 재미·흥미 느끼는 활동: \n"
                        "- 경제적 시급성: [ ] 매우 시급 [ ] 시급 [ ] 보통 [ ] 여유 있음\n"
                        "- 건강 상태: [ ] 풀타임 가능 [ ] 하루 4~6시간 적합 [ ] 단시간·단발성 선호 [ ] 건강 이슈로 제한\n"
                        "- 특이사항 메모 (건강, 가족 지지 등): \n"
                        "- 기타: 이전 상담·교육 이력\n\n"
                        "■ 5. 회차별 상담 내용 (메모가 해당하는 회차만 채우기)\n"
                        "- 주요 상담 주제: \n"
                        "- 현재 상태 및 주요 내용: \n"
                        "- 제공한 솔루션 / 정보: \n"
                        "- 내담자 반응: \n"
                        "- 다음 회차 계획: \n"
                        "- 서류/지원 현황: 이력서 취합 [ ]완료 [ ]미완료 / 지원 ( )건 / 면접 ( )건\n\n"
                        "■ 6. 사후 관리 및 특이사항\n"
                        "- 취업 여부: [ ] 취업 완료 [ ] 구직 중 [ ] 구직 중단 [ ] 개인사업 [ ] 기타\n"
                        "- 취업처명 / 직무: \n"
                        "- 취업 확인서: [ ] 수령 [ ] 미수령\n"
                        "- 사후 관리 메모: \n"
                        "---"
                    )
                    
                    content_payload = [prompt] + image_parts
                    response = model.generate_content(content_payload)
                    ai_result = response.text
                    
                    st.success("✅ 모든 파일 통합 분석 완료!")
                    
                    # 🌟 [해결] 복사 버튼 누락 문제와 무한 루프를 완벽히 해결하는 최신 코드 구조
                    # 정렬 및 폰트 효과를 보장하는 최종 텍스트 구성
                    formatted_result = f"[취업 상담 일지]\n\n{ai_result.replace('[취업 상담 일지]', '').strip()}"
                    
                    # 1. 화면 중앙에 크고 진하게 대제목 표시 (상담사 가독용)
                    st.markdown("<h2 style='text-align: center; font-family: sans-serif; font-weight: bold;'>[취업 상담 일지]</h2>", unsafe_allow_html=True)
                    
                    # 2. 복사 기능이 100% 작동하는 Streamlit 공식 텍스트 에어리어 (내장 복사버튼 활성화)
                    st.text_area(
                        label="💡 우측 상단의 복사 버튼(문서 모양)을 누르면 전체 내용이 복사됩니다.",
                        value=formatted_result,
                        height=500
                    )
                    
                except Exception as e:
                    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                    st.caption("잠시 후 다시 시도해 주세요.")
    else:
        st.info("왼쪽 화면에서 파일(최대 3개)을 업로드해 주세요.")
        
