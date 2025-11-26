import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="오늘 뭐 먹지?", page_icon="🍳", layout="wide")

st.title("메뉴 추천기")
st.markdown("---")
st.subheader("상황을 알려주시면, 딱 맞는 메뉴와 맛집(또는 레시피)을 알려드려요.")

with st.sidebar:
    st.header("맞춤 옵션")
    
    # 집밥 모드 체크박스
    is_home_cook = st.checkbox("오늘은 집에서 만들어 먹을래요!")
    
    # [동적 UI 1] 외식일 때만 장소를 물어봄
    if not is_home_cook:
        location = st.text_input("어디서 드시나요? (예: 강남역,회사 근처,집)")
    else:
        location = "집"
    
    who = st.text_input("누구랑 먹나요? (예: 혼자, 연인, 부장님)")
    mood = st.text_input("오늘 기분은? (예: 배고파, 꿀꿀해)")
    weather = st.text_input("날씨는? (예: 비와, 맑음)")
    taste = st.text_input("땡기는 맛은? (예: 매콤한거, 국물)")
    favorite = st.text_input("평소 좋아하는 음식? (예: 고기, 면)")
    blocked = st.text_input("못 먹는 음식? (예: 오이, 해산물)")
    
    # [동적 UI 2] 외식일 때만 예산을 물어봄 (집밥은 예산 생략)
    if not is_home_cook:
        price = st.text_input("예산은? (예: 만원 이하, 법카)")
    else:
        price = "집에 있는 재료 활용" 

    st.markdown("---")
    submit_btn = st.button("메뉴 추천 받기")

if submit_btn:
    # 유효성 검사
    if submit_btn:
    # 무조건 적어야 하는 것들 (기분, 날씨, 누구랑, 맛, 취향)
        essentials = [mood, weather, who, taste, favorite]
    
    # 외식 모드일 때만 필요한 것들 (장소, 예산) 추가
    if not is_home_cook:
        essentials.extend([location, price])
        
    # 하나라도 비어있으면(False면) 경고하고 멈춤!
    if not all(essentials):
        st.warning("옵션이 완성되지 않았어요! (싫어하는 음식 빼고) 모든 빈칸을 채워주세요.")
        st.stop()
        
    GOOGLE_API_KEY = 'AIzaSyCJSp7tAEMT4vtagCyX_4PKGuI1NZGBykI'.strip()
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 페르소나 설정
    if is_home_cook:
        role_prompt = """
        당신은 요리 연구가 '백종원'입니다.
        복잡한 요리 말고, 집에서 뚝딱 만들 수 있는 현실적인 메뉴를 추천해줘야 해.
        [답변 양식]
        1. 메뉴 이름:
        2. 추천 이유: (누구랑 먹는지 고려해서)
        3. 필요 재료: (냉장고에 있을 법한 재료 위주)
        4. 초간단 레시피: (간단하게 단계별로 요약)
        """
    else:
        role_prompt = """
        당신은 미슐랭 가이드 평가원입니다.
        [답변 양식]
        1. 메뉴 이름:
        2. 추천 이유: (누구랑 먹는지, 예산은 맞는지 고려해서)
        3. 예상 칼로리:
        4. 맛집 검색 팁: (실패 없는 메뉴 고르는 팁)
        """

    # 프롬프트
    prompt = f"""
    {role_prompt}
    
    상황: 장소='{location}', 누구랑='{who}', 예산='{price}'
    기분='{mood}', 날씨='{weather}', 땡기는맛='{taste}'
    평소취향='{favorite}', 제외음식='{blocked}'
    
    위 8가지 조건을 모두 고려해서 가장 완벽한 점심 메뉴 1개를 추천해줘.
    
    [아주 중요한 명령]
    답변 맨 마지막 줄에 검색용 키워드를 한 줄만 적어줘.
    SEARCH_KEYWORD: {{메뉴이름}}
    (예: SEARCH_KEYWORD: 김치찌개)
    """

    with st.spinner("메뉴는 선정이 딸입니다..."):
        try:
            response = model.generate_content(prompt)
            
            full_text = response.text
            if "SEARCH_KEYWORD:" in full_text:
                parts = full_text.split("SEARCH_KEYWORD:")
                display_text = parts[0]
                menu_name = parts[1].strip()
            else:
                display_text = full_text
                menu_name = f"{taste} 음식"

            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.success("완벽한 메뉴를 찾았습니다!")
                st.markdown(display_text)
            
            with col2:
                st.info(f"'{menu_name}' 더 알아보기")
                
                # 이미지 버튼
                img_url = f"https://www.google.com/search?q={menu_name}&tbm=isch"
                st.link_button("음식 사진 보기", img_url)
                
                # 상황별 버튼 (지도 vs 유튜브)
                if not is_home_cook:
                    map_url = f"https://map.naver.com/v5/search/{location} {menu_name} 맛집"
                    st.link_button(f"{location} 맛집 찾기", map_url)
                else:
                    youtube_url = f"https://www.youtube.com/results?search_query={menu_name} 만들기"
                    st.link_button("유튜브 레시피 보기", youtube_url)

        except Exception as e:
            st.error(f"오류: {e}")

else:
    st.info("👈 왼쪽 사이드바에서 옵션을 선택해주세요.")