<project_specification>

<project_name>사이좋은 AI 포럼 프로필 보드 - AI Forum 2026 Participant Profile Board</project_name>

<overview>
사이좋은 AI 포럼 2026 참여자 프로필 보드는 카카오임팩트와 푸른나무재단이 공동 주최하는 교육 포럼의 참여자 148명의 프로필을 시각적으로 보여주는 정적 웹사이트이다. 참여자의 이름, 소속, 직함, 자기소개, 프로필 이미지를 카드 형태로 그리드에 배치하고, 카테고리 필터와 이름 검색 기능을 제공한다.

데이터는 두 개의 Google Sheets에서 수집된다. 시트1(사전등록 폼 응답)에서 참여자의 상세 정보(이름, 소속, 직함, 자기소개, 프로필 이미지)를, 시트2(운영 관리 시트)에서 카테고리 분류(중구분)를 가져온다. Python 빌드 스크립트가 두 시트를 병합하고, 중복 제출 제거, 취소자 필터링, 프로필 이미지 로컬 다운로드를 수행하여 정적 자산(JSON/JS + 이미지)을 생성한다.

CRITICAL: 이 프로젝트는 순수 정적 사이트이다. 백엔드 서버, 데이터베이스, 실시간 API 호출이 없다. 모든 데이터는 빌드 타임에 정적 파일로 생성되며, file:// 프로토콜에서도 동작해야 한다. Google Sheets에 대한 런타임 의존성이 없어야 한다. 배포는 Vercel(GitHub 연동 자동 배포)을 통해 이루어진다.
</overview>

<technology_stack>
  <frontend>
    <language>Vanilla HTML/CSS/JavaScript (프레임워크 없음)</language>
    <font>Pretendard v1.3.9 (CDN: cdn.jsdelivr.net/gh/orioncactus/pretendard)</font>
    <styling>인라인 CSS (single-file HTML)</styling>
    <data_loading>정적 JS 파일을 script 태그로 로드 (fetch 사용하지 않음, file:// 호환)</data_loading>
    <analytics>Google Analytics 4 (gtag.js, ID: G-ZQY33M2VEJ)</analytics>
  </frontend>
  <build_tool>
    <language>Python 3.9+ (표준 라이브러리만 사용, 외부 패키지 없음)</language>
    <modules>csv, json, os, re, urllib.request, time, glob</modules>
    <command>python3 build.py</command>
  </build_tool>
  <data_sources>
    <sheet1>Google Sheets CSV Export - 사전등록 폼 응답 (gid=1551428892)</sheet1>
    <sheet2>Google Sheets CSV Export - 참여자 카테고리 분류 (gid=225355410)</sheet2>
    <images>Google Drive Thumbnail API (sz=w400)</images>
  </data_sources>
  <deployment>
    <hosting>Vercel (GitHub 연동 자동 배포)</hosting>
    <repository>github.com/full-of-zoey/aiforum-profile</repository>
    <branch>main</branch>
  </deployment>
</technology_stack>

<prerequisites>
  <environment_setup>
    - Python 3.9 이상
    - Git
    - GitHub CLI (gh) - 선택사항, repo 관리용
    - 인터넷 연결 (빌드 시 Google Sheets/Drive 접근 필요)
  </environment_setup>
  <accounts>
    - GitHub 계정 (배포용)
    - Vercel 계정 (GitHub 연동)
    - Google Analytics 계정 (트래킹용, 선택사항)
  </accounts>
</prerequisites>

<core_data_entities>
  <profile>
    - id: number (1부터 순차 증가, 빌드 시 자동 할당)
    - name: string (required, 한글 이름 2자 이상)
    - organization: string (소속 기관명)
    - title: string (직함)
    - intro: string (자기소개, 한 줄 문장)
    - category: enum (교원, 장학사, 정책・연구, 교육혁신・에듀테크, AI・기술, 사디세 강사, 기타)
    - image: string|null (로컬 이미지 경로, e.g. "images/{drive_id}.jpg")
  </profile>

  <profile_data_json>
    - categories: string[] (카테고리 표시 순서 배열)
    - profiles: Profile[] (전체 프로필 배열)
    - total: number (전체 프로필 수)
    - built_at: string (빌드 시각, "YYYY-MM-DD HH:MM:SS")
  </profile_data_json>

  <sheet1_row>
    시트1 컬럼 매핑 (사전등록 폼):
    - [0] 타임스탬프
    - [1] 이메일 주소
    - [2] ① 성함
    - [3] ② 소속
    - [4] ③ 직함
    - [5] ④ 자기소개
    - [6] ⑤ 프로필 이미지 (Google Drive URL)
    - [7-12] 교통, 셔틀, 접근성, 공문, 동의 등
    - [13] Column 14 (취소/중복 표시: "참석 취소", "중복응답으로 삭제" 등)
  </sheet1_row>

  <sheet2_row>
    시트2 컬럼 매핑 (카테고리 분류):
    - [0] (빈)
    - [1] 연번
    - [2] 대구분
    - [3] 중구분 (필터에 사용되는 카테고리)
    - [4] 명찰구분 (색상: 노란색, 분홍색, 파란색, 초록색 등)
    - [5] 유입구분
    - [6] 성함
    - [7] 사전등록
    - [10] 소속
    - [11] 직함
  </sheet2_row>
</core_data_entities>

<pages_and_interfaces>
  <single_page_layout>
    전체가 단일 HTML 파일(index.html)로 구성된다. 섹션 순서:
    1. Header Banner
    2. Filter Section (검색 + 카테고리 필터)
    3. Profile Grid (카드 그리드)
    4. Footer (로고 + 저작권)
    5. Modal Overlay (카드 클릭 시 상세보기)
  </single_page_layout>

  <header_banner>
    - 전체 너비 이미지 배너 (assets/header-banner-v2.png)
    - 배경: white (#FFFFFF)
    - 이미지: width 100%, height auto
    - 모바일(768px 이하): max-height 300px, object-fit cover
  </header_banner>

  <filter_section>
    - max-width: 1800px, 중앙 정렬
    - padding: 36px 40px 20px
    - 배경: #f8fbfd

    <search_box>
      - flex: 1, min-width: 280px, max-width: 400px
      - 입력 필드: padding 14px 20px 14px 50px, border-radius 50px
      - 테두리: 2px solid #B2EBF2
      - 포커스: border-color #00B8D4, box-shadow 0 0 0 4px rgba(0,184,212,0.1)
      - 검색 아이콘: 왼쪽 20px 위치에 돋보기 이모지
      - placeholder: "이름으로 검색하세요"
      - 실시간 필터링 (input 이벤트)
    </search_box>

    <filter_buttons>
      - display: flex, gap: 8px, flex-wrap: wrap
      - "전체" 버튼 기본 포함 (data-filter="all")
      - 카테고리 순서: 교원, 장학사, 정책・연구, 교육혁신・에듀테크, AI・기술, 사디세 강사
      - 버튼 스타일: padding 10px 20px, border-radius 50px, font-weight 600
      - 비활성: background white, border 2px solid #B2EBF2, color #546E7A
      - 호버: border-color #00B8D4, color #00B8D4
      - 활성: background #00B8D4, border-color #00B8D4, color white
      - 툴팁(title): "{카테고리} ({인원수}명)"
      - 모바일(768px 이하): 가로 스크롤, flex-wrap nowrap
    </filter_buttons>
  </filter_section>

  <profile_grid_section>
    - 배경: linear-gradient(180deg, #E0F7FA 0%, #B2EBF2 50%, #80DEEA 100%)
    - padding: 40px, min-height: 60vh
    - 상단 구름 장식: SVG wave pseudo-element (::before, height 60px)

    <grid_layout>
      - max-width: 1800px, 중앙 정렬
      - display: grid, gap: 20px
      - 반응형 컬럼 수:
        - 기본: repeat(8, 1fr)
        - 1600px 이하: repeat(6, 1fr)
        - 1200px 이하: repeat(4, 1fr)
        - 900px 이하: repeat(3, 1fr)
        - 768px 이하: repeat(2, 1fr), gap 16px
        - 480px 이하: 1fr (단일 컬럼)
    </grid_layout>

    <profile_card>
      - background: white (#FFFFFF)
      - border: 3px solid #1a1a1a, border-radius: 20px
      - padding: 20px 16px
      - display: flex, flex-direction: column, align-items: center
      - min-width: 0 (그리드 오버플로 방지)
      - 그림자: pseudo-element (::before) top 5px left 5px, rgba(0,0,0,0.1)
      - 호버: transform translate(-3px, -3px), 그림자 확장 (top 8px left 8px)
      - transition: all 0.3s ease
      - cursor: pointer

      <card_profile_image>
        - width: 80px, height: 80px, border-radius: 50%
        - border: 3px solid #1a1a1a
        - 이미지 있음: img 태그, object-fit cover, object-position top
        - 이미지 없음: 이름 첫 글자, font-size 2rem, font-weight 800, color white
        - 이미지 로드 실패: onerror로 첫 글자 아바타 폴백
        - 아바타 배경색: ID 기반 10색 순환 (avatar-color-1 ~ 10)
          - 1: linear-gradient(135deg, #E91E63, #F48FB1)
          - 2: linear-gradient(135deg, #66BB6A, #A5D6A7)
          - 3: linear-gradient(135deg, #FFD54F, #FFECB3)
          - 4: linear-gradient(135deg, #BA68C8, #E1BEE7)
          - 5: linear-gradient(135deg, #42A5F5, #90CAF9)
          - 6: linear-gradient(135deg, #00B8D4, #80DEEA)
          - 7: linear-gradient(135deg, #FF7043, #FFAB91)
          - 8: linear-gradient(135deg, #26A69A, #80CBC4)
          - 9: linear-gradient(135deg, #7E57C2, #B39DDB)
          - 10: linear-gradient(135deg, #EC407A, #F8BBD9)
      </card_profile_image>

      <card_name>
        - font-size: 1.1rem, font-weight: 800, color: #1a1a1a
        - white-space: nowrap, overflow: hidden, text-overflow: ellipsis
      </card_name>

      <card_organization>
        - font-size: 0.8rem, color: #546E7A
        - white-space: nowrap, overflow: hidden, text-overflow: ellipsis
      </card_organization>

      <card_title_badge>
        - display: inline-block
        - background: #1a1a1a, color: white
        - padding: 4px 12px, border-radius: 16px
        - font-size: 0.75rem, font-weight: 600
        - max-width: 100%, text-overflow: ellipsis
      </card_title_badge>

      <card_intro>
        - height: 58px (고정), border-radius: 10px, padding: 12px
        - font-size: 0.85rem, font-weight: 500
        - display: flex, align-items: center, justify-content: center
        - 텍스트: -webkit-line-clamp 2 (최대 2줄, 넘치면 ... 처리)
        - margin-top: auto (카드 하단에 정렬)
        - 카테고리별 배경색:
          - 교원/장학사 (intro-yellow): rgba(255, 219, 0, 0.2) — CMYK C0 M14 Y100 K0
          - AI・기술 (intro-pink): rgba(240, 120, 255, 0.18) — CMYK C6 M53 Y0 K0
          - 교육혁신・에듀테크/사디세 강사 (intro-blue): rgba(38, 201, 255, 0.18) — CMYK C85 M21 Y0 K0
          - 정책・연구 (intro-green): rgba(64, 255, 74, 0.18) — CMYK C75 M0 Y71 K0
          - 기타 (intro-purple): rgba(122, 158, 255, 0.2) — CMYK C52 M38 Y0 K0
      </card_intro>
    </profile_card>

    <loading_state>
      - grid-column: 1 / -1, text-align: center, padding: 60px 20px
      - 스피너: 50px, border 4px solid #e0f7fa, border-top-color #00B8D4
      - animation: spin 1s linear infinite
    </loading_state>

    <empty_state>
      - 돋보기 이모지 (4rem) + "검색 결과가 없습니다" 메시지
      - 메시지: white 배경, border 3px solid #1a1a1a, border-radius 16px
    </empty_state>
  </profile_grid_section>

  <modal_detail_view>
    <overlay>
      - position: fixed, 전체 화면 커버
      - background: rgba(0, 0, 0, 0.5)
      - display: flex, align-items: center, justify-content: center
      - 비활성: opacity 0, visibility hidden
      - 활성: opacity 1, visibility visible
      - transition: all 0.3s ease
    </overlay>

    <modal_panel>
      - background: white, border: 4px solid #1a1a1a, border-radius: 28px
      - max-width: 420px, width: 100%, padding: 44px 36px
      - box-shadow: 8px 8px 0 rgba(0,0,0,0.15)
      - 진입 애니메이션: transform scale(0.9) → scale(1), 0.3s ease

      <close_button>
        - position: absolute, top 16px right 16px
        - 40px 원형, border 3px solid #1a1a1a
        - background: #00B8D4, color: white, font-weight: 800
        - 호버: rotate(90deg), background #E91E63
      </close_button>

      <modal_image>
        - width: 120px, height: 120px, border-width: 4px
        - 동일한 아바타 색상 로직 적용
      </modal_image>

      <modal_name>font-size: 1.8rem</modal_name>
      <modal_org>font-size: 1rem, white-space normal (줄바꿈 허용)</modal_org>
      <modal_title>font-size: 0.9rem, padding 6px 18px</modal_title>

      <modal_intro>
        - font-size: 1.05rem, padding: 18px 20px
        - border: 2px solid #1a1a1a
        - height: auto (전문 표시, 줄 수 제한 없음)
        - display: flex, align-items: center, justify-content: center
        - 카테고리별 배경색 적용 (카드와 동일)
      </modal_intro>
    </modal_panel>

    <interactions>
      - 닫기: X 버튼 클릭, 오버레이 배경 클릭, Escape 키
      - 열림 시: body overflow hidden (스크롤 방지)
    </interactions>
  </modal_detail_view>

  <footer>
    - background: #1a1a1a, padding: 50px 40px, text-align: center
    - 로고 3개: 카카오, 카카오임팩트, 푸른나무재단
    - 로고 스타일: height 28px, filter brightness(0) invert(1), opacity 0.7
    - 저작권: "© 2026 사이좋은 AI 포럼. All rights reserved."
    - 텍스트 색상: rgba(255, 255, 255, 0.4)
  </footer>

  <keyboard_shortcuts>
    - Escape: 모달 닫기
  </keyboard_shortcuts>
</pages_and_interfaces>

<core_functionality>
  <build_pipeline>
    빌드 스크립트 (build.py) 실행 흐름:
    1. Google Sheets 시트1, 시트2를 CSV로 다운로드
    2. 시트1 파싱: 유효한 등록자 추출 (이름 2자 이상, 한글/영문만)
    3. 중복 제출 처리: 같은 이름+소속 → 자기소개가 더 충실한 쪽 유지
    4. 취소자 제외: 14열에 "취소" 포함된 행 제거
    5. 시트2 파싱: 카테고리(중구분) 매핑 생성
    6. 카테고리 통합: "카카오" → "AI・기술"으로 병합
    7. 병합: 시트1 등록자에 시트2 카테고리 매칭 (이름+소속 우선, 이름만 폴백)
    8. 미분류자: "기타" 카테고리 할당
    9. 이미지: 기존 이미지 폴더 초기화 → Google Drive thumbnail 다운로드
    10. 파일명: Google Drive ID 기반 ({drive_id}.jpg) — 리빌드 시 안정적 매핑
    11. 출력: data/profiles.json + data/profiles.js 생성
    12. 이름순 정렬
  </build_pipeline>

  <deduplication_logic>
    - 동명이인 지원: 이름+소속 복합키로 구분 (예: 김정선/인천새말초 vs 김정선/동삭초)
    - 중복 제출 판별: 같은 이름+같은 소속 → 자기소개 길이 비교
    - 자기소개가 빈 값("", "~~", "-")이면 score 0으로 처리
    - score가 높은(더 충실한) 쪽을 유지
    - 시트1 14열 마커와 독립적으로 작동 (마커 유무와 관계없이 최적 데이터 선택)
  </deduplication_logic>

  <category_filtering>
    - "전체" 버튼: 모든 프로필 표시
    - 카테고리 버튼: 해당 카테고리 프로필만 표시
    - 활성 버튼 하이라이트 (한 번에 하나만 활성)
    - 검색과 필터 동시 적용 가능
  </category_filtering>

  <name_search>
    - 실시간 입력 필터링 (debounce 없음)
    - 대소문자 무시
    - 이름 필드만 검색 대상
    - 카테고리 필터와 AND 조건으로 결합
  </name_search>

  <profile_detail_modal>
    - 카드 클릭 시 모달 오픈
    - 프로필 이미지, 이름, 소속, 직함, 자기소개 전문 표시
    - 자기소개 줄 수 제한 없음 (카드에서는 2줄 제한)
    - 카테고리별 배경색 적용
  </profile_detail_modal>

  <image_fallback>
    - 이미지 없는 프로필: 이름 첫 글자 + 그라데이션 배경 아바타
    - 이미지 로드 실패: onerror 이벤트로 첫 글자 아바타 폴백
    - 아바타 색상: profile ID 기반 10색 순환
  </image_fallback>
</core_functionality>

<aesthetic_guidelines>
  <design_philosophy>
    "사이좋은 AI 포럼" 브랜드 아이덴티티 기반. 친근하고 밝은 느낌의 교육 포럼 분위기.
    네오브루탈리즘 요소 (굵은 테두리, 오프셋 그림자)와 부드러운 파스텔 그라데이션의 조합.
  </design_philosophy>

  <color_palette>
    <brand_colors>
      - Primary Cyan: #00B8D4 — 주요 액센트, 필터 활성, 닫기 버튼
      - Primary Cyan Light: #4DD0E1 — 보조 하이라이트
      - Primary Cyan Dark: #0097A7 — 다크 변형
    </brand_colors>
    <accent_colors>
      - Accent Pink: #E91E63 — 호버 인터랙션
      - Accent Yellow: #FFD54F — 아바타 색상
      - Accent Green: #66BB6A — 아바타 색상
      - Accent Purple: #BA68C8 — 아바타 색상
      - Accent Blue: #42A5F5 — 아바타 색상
    </accent_colors>
    <background_colors>
      - Page Background: #f8fbfd
      - Background Gradient: linear-gradient(180deg, #e0f7fa 0%, #f8fbfd 100%)
      - Profile Section: linear-gradient(180deg, #E0F7FA 0%, #B2EBF2 50%, #80DEEA 100%)
      - Card Background: #FFFFFF
      - Footer: #1a1a1a
    </background_colors>
    <text_colors>
      - Dark (Primary): #1a1a1a
      - Gray (Secondary): #546E7A
      - Footer Text: rgba(255, 255, 255, 0.4)
    </text_colors>
    <category_intro_colors>
      명찰 색상 기반, CMYK → RGB 변환 후 18-20% 투명도 적용:
      - Yellow (교원/장학사): rgba(255, 219, 0, 0.2) — from CMYK C0 M14 Y100 K0
      - Pink (AI・기술): rgba(240, 120, 255, 0.18) — from CMYK C6 M53 Y0 K0
      - Blue (교육혁신・에듀테크/사디세 강사): rgba(38, 201, 255, 0.18) — from CMYK C85 M21 Y0 K0
      - Green (정책・연구): rgba(64, 255, 74, 0.18) — from CMYK C75 M0 Y71 K0
      - Purple (기타): rgba(122, 158, 255, 0.2) — from CMYK C52 M38 Y0 K0
    </category_intro_colors>
  </color_palette>

  <typography>
    <font_family>
      'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif
      CDN: cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9
    </font_family>
    <font_sizes>
      - Card Name: 1.1rem, weight 800
      - Card Org: 0.8rem, weight normal
      - Card Title Badge: 0.75rem, weight 600
      - Card Intro: 0.85rem, weight 500
      - Modal Name: 1.8rem, weight 800
      - Modal Org: 1rem
      - Modal Title: 0.9rem, weight 600
      - Modal Intro: 1.05rem
      - Filter Button: 0.9rem, weight 600
      - Search Input: 1rem
      - Footer: 0.9rem
    </font_sizes>
    <line_height>1.6 (body default), 1.5 (card intro)</line_height>
  </typography>

  <borders_and_shadows>
    <borders>
      - Card: 3px solid #1a1a1a, border-radius 20px
      - Modal: 4px solid #1a1a1a, border-radius 28px
      - Profile Image: 3px solid #1a1a1a (카드), 4px (모달)
      - Filter Button: 2px solid #B2EBF2, border-radius 50px
      - Search Input: 2px solid #B2EBF2, border-radius 50px
      - Modal Intro: 2px solid #1a1a1a
    </borders>
    <shadows>
      - Card: pseudo-element offset (5px, 5px), rgba(0,0,0,0.1)
      - Card Hover: offset grows to (8px, 8px)
      - Modal: 8px 8px 0 rgba(0,0,0,0.15) (hard shadow)
      - Search Focus: 0 0 0 4px rgba(0,184,212,0.1)
    </shadows>
  </borders_and_shadows>

  <animations>
    - Card Hover: transform translate(-3px, -3px), 0.3s ease
    - Modal Open: scale(0.9) → scale(1), 0.3s ease
    - Modal Overlay: opacity/visibility, 0.3s ease
    - Close Button Hover: rotate(90deg), 0.3s ease
    - Loading Spinner: rotate 360deg, 1s linear infinite
    - Filter/Search Transitions: all 0.3s ease
  </animations>
</aesthetic_guidelines>

<advanced_functionality>
  <build_script_features>
    - 기존 이미지 폴더 초기화 후 재다운로드 (stale 이미지 방지)
    - Google Drive ID 기반 파일명 (인덱스 기반이 아닌 콘텐츠 기반 매핑)
    - Rate limiting: 이미지 다운로드 간 0.3초 딜레이
    - 이미지 크기 검증: 500 bytes 미만이면 실패로 간주
    - 타임아웃: 이미지 다운로드 15초
    - profiles.json (API/도구용) + profiles.js (file:// 호환, script 태그 로드) 동시 생성
  </build_script_features>

  <data_update_workflow>
    데이터 업데이트 시:
    1. python3 build.py (데이터 갱신 + 이미지 다운로드)
    2. git add -A && git commit -m "update" && git push
    3. Vercel 자동 재배포
  </data_update_workflow>
</advanced_functionality>

<final_integration_test>
  <test_scenario_1>
    <description>전체 빌드 파이프라인</description>
    <steps>
      1. python3 build.py 실행
      2. 시트1, 시트2 다운로드 성공 확인
      3. 취소자 제외 로그 확인 (14열 "취소" 마커)
      4. 중복 제출 제거 로그 확인 (같은 이름+소속)
      5. 동명이인 보존 확인 (김정선 2건)
      6. images/ 폴더에 이미지 파일 생성 확인
      7. data/profiles.json 파일 생성 확인 (total 필드 = 이미지 수)
      8. data/profiles.js 파일 생성 확인 ("const PROFILE_DATA = " 접두사)
      9. 전체 프로필 수 = 시트1 유효 등록자 수 일치 확인
    </steps>
  </test_scenario_1>

  <test_scenario_2>
    <description>프로필 보드 로딩 및 표시</description>
    <steps>
      1. index.html을 브라우저에서 file://로 직접 열기
      2. 프로필 카드 그리드가 표시되는지 확인
      3. 카드에 이미지, 이름, 소속, 직함, 자기소개가 표시되는지 확인
      4. 이미지 없는 카드에 이름 첫 글자 아바타가 표시되는지 확인
      5. 카테고리별 자기소개 배경색이 다른지 확인
      6. 필터 버튼이 카테고리 순서대로 생성되는지 확인
      7. 각 필터 버튼 title에 인원수가 표시되는지 확인
    </steps>
  </test_scenario_2>

  <test_scenario_3>
    <description>필터링 및 검색</description>
    <steps>
      1. "교원" 필터 버튼 클릭
      2. 교원 카테고리 프로필만 표시되는지 확인
      3. "전체" 버튼 클릭하여 복원 확인
      4. 검색창에 이름 일부 입력
      5. 실시간 필터링이 작동하는지 확인
      6. 필터 + 검색 동시 적용 확인
      7. 존재하지 않는 이름 입력 시 "검색 결과가 없습니다" 메시지 확인
      8. 검색 텍스트 지우면 전체 표시 복원 확인
    </steps>
  </test_scenario_3>

  <test_scenario_4>
    <description>모달 상세보기</description>
    <steps>
      1. 프로필 카드 클릭
      2. 모달 오버레이가 fade-in 표시되는지 확인
      3. 모달에 프로필 이미지, 이름, 소속, 직함, 자기소개 전문이 표시되는지 확인
      4. 자기소개가 카테고리별 배경색으로 표시되는지 확인
      5. X 버튼 클릭으로 모달 닫기 확인
      6. 오버레이 배경 클릭으로 모달 닫기 확인
      7. Escape 키로 모달 닫기 확인
      8. 모달 열림 시 배경 스크롤 비활성화 확인
    </steps>
  </test_scenario_4>

  <test_scenario_5>
    <description>반응형 레이아웃</description>
    <steps>
      1. 데스크톱(1920px): 8열 그리드 확인
      2. 1600px: 6열 그리드 확인
      3. 1200px: 4열 그리드 확인
      4. 900px: 3열 그리드 확인
      5. 768px: 2열 그리드, 필터 세로 배치, 필터 가로 스크롤 확인
      6. 480px: 1열 그리드 확인
      7. 모바일에서 배너 이미지 300px 높이 제한 확인
      8. 모바일에서 모달 여백 적절한지 확인
    </steps>
  </test_scenario_5>
</final_integration_test>

<success_criteria>
  <functionality>
    - 빌드 스크립트 실행 시 148명 이상 프로필 생성
    - 이미지 다운로드 성공률 98% 이상
    - 전체/카테고리별 필터 6개 + 전체 = 7개 버튼 정상 작동
    - 이름 검색 실시간 필터링 정상 작동
    - 모달 열기/닫기 3가지 방법(X, 배경, Escape) 모두 작동
    - 중복 제출 자동 제거, 취소자 자동 필터링
  </functionality>
  <user_experience>
    - 페이지 로딩 2초 이내 (로컬 정적 파일)
    - file:// 프로토콜에서 정상 동작
    - 모든 카드 균일한 크기 (넓이, 높이 일치)
    - 모든 텍스트 오버플로 시 ellipsis 처리
  </user_experience>
  <technical_quality>
    - 외부 런타임 의존성 없음 (Pretendard CDN, GA 제외)
    - Python 빌드 스크립트: 표준 라이브러리만 사용
    - 단일 HTML 파일 + 정적 데이터 파일 구조
  </technical_quality>
  <visual_design>
    - 카테고리별 5색 구분 정확
    - 브랜드 컬러(#00B8D4) 일관 적용
    - 6단계 반응형 그리드 정상 작동
  </visual_design>
  <deployment>
    - GitHub push 시 Vercel 자동 배포
    - 배포 URL에서 정상 접근 가능
    - Google Analytics 데이터 수집 확인
  </deployment>
</success_criteria>

<build_output>
  <directory_structure>
    aiforum_profile/
    ├── .gitignore
    ├── index.html              (단일 HTML 파일, CSS/JS 인라인)
    ├── build.py                (Python 빌드 스크립트)
    ├── assets/
    │   ├── header-banner-v2.png
    │   ├── kakao-logo.png
    │   ├── kakao-impact-logo.png
    │   └── bluetree-logo.png
    ├── data/
    │   ├── profiles.json       (구조화된 데이터)
    │   └── profiles.js         (script 태그 로드용, "const PROFILE_DATA = {...};")
    └── images/
        ├── {drive_id_1}.jpg
        ├── {drive_id_2}.jpg
        └── ... (148개 프로필 이미지)
  </directory_structure>
  <deployment_notes>
    - Vercel: GitHub main 브랜치 연동, 프레임워크 설정 불필요
    - 커스텀 도메인 설정 가능 (Vercel 대시보드)
    - 데이터 갱신: python3 build.py → git push → 자동 재배포
  </deployment_notes>
</build_output>

<key_implementation_notes>
  <critical_paths>
    - CRITICAL: fetch() 사용 금지. file:// 프로토콜에서 CORS 에러 발생. 반드시 script 태그로 데이터 로드.
    - CRITICAL: 이미지 파일명은 Google Drive ID 기반. 인덱스 기반 파일명 사용 시 리빌드 때 매핑 오류 발생.
    - CRITICAL: 중복 제출 처리 시 14열(취소 마커)보다 먼저 내용 비교를 수행해야 함. 좋은 데이터가 취소 마커 행에 있을 수 있음.
  </critical_paths>

  <recommended_implementation_order>
    1. build.py: Google Sheets CSV 다운로드 + 파싱
    2. build.py: 시트1 데이터 정제 (중복 제거, 취소자 필터)
    3. build.py: 시트2 카테고리 매칭
    4. build.py: 이미지 다운로드
    5. build.py: JSON/JS 출력
    6. index.html: 기본 레이아웃 + CSS
    7. index.html: 프로필 카드 렌더링
    8. index.html: 필터 + 검색 기능
    9. index.html: 모달 상세보기
    10. index.html: 반응형 처리
    11. index.html: 카테고리별 색상 적용
    12. 배포: Git + GitHub + Vercel 연동
  </recommended_implementation_order>

  <category_to_color_mapping>
    시트2 명찰구분(badge color) → CSS 클래스 매핑:
    - 노란색 (교원, 장학사) → intro-yellow
    - 분홍색 (AI・기술, 카카오 통합) → intro-pink
    - 파란색 (교육혁신・에듀테크, 사디세 강사) → intro-blue
    - 초록색 (정책・연구) → intro-green
    - (기타) → intro-purple
  </category_to_color_mapping>

  <category_merge_rules>
    - "카카오" 중구분 → "AI・기술"로 통합
    - 시트2에 없는 등록자 → "기타" 할당
    - 카테고리 필터 순서: 교원, 장학사, 정책・연구, 교육혁신・에듀테크, AI・기술, 사디세 강사
    - 인원수가 0인 카테고리는 필터 버튼에서 제외
  </category_merge_rules>
</key_implementation_notes>

</project_specification>
