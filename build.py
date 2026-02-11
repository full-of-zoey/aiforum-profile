#!/usr/bin/env python3
"""
사이좋은 AI 포럼 - 프로필 보드 빌드 스크립트
Google Sheets에서 데이터를 가져와 로컬 정적 자산으로 변환합니다.

사용법: python3 build.py
"""

import csv
import json
import os
import re
import urllib.request
import urllib.error
import time
import hashlib

# === 설정 ===
SHEET1_URL = "https://docs.google.com/spreadsheets/d/1O2Ya7XqKJpFaJScJp1fbPR6Y3Rgjn_qsVYgIy9E-k2M/gviz/tq?tqx=out:csv&gid=1551428892"
SHEET2_URL = "https://docs.google.com/spreadsheets/d/1u6TjlTKfBH5_9MnGCEG6C3NrjazX77tslbe3BxGN498/gviz/tq?tqx=out:csv&gid=225355410"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DATA_DIR = os.path.join(BASE_DIR, "data")

# === CSV 다운로드 ===
def download_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def parse_csv(text):
    reader = csv.reader(text.strip().splitlines())
    headers = next(reader)
    rows = []
    for row in reader:
        if any(cell.strip() for cell in row):
            rows.append(row)
    return headers, rows


# === Google Drive 이미지 ID 추출 ===
def extract_drive_id(url):
    if not url or not url.strip():
        return None
    m = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    return None


# === 이미지 다운로드 ===
def download_image(drive_id, filename):
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return True  # 이미 다운로드됨

    # Google Drive thumbnail URL (고화질)
    url = f"https://drive.google.com/thumbnail?id={drive_id}&sz=w400"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) < 500:  # 너무 작으면 실패로 간주
                print(f"  ⚠ {filename}: 이미지가 너무 작음 ({len(data)} bytes), 스킵")
                return False
            with open(filepath, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"  ✗ {filename}: 다운로드 실패 - {e}")
        return False


# === 메인 빌드 ===
def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    print("📥 시트1 (사전등록) 다운로드 중...")
    sheet1_text = download_csv(SHEET1_URL)
    h1, rows1 = parse_csv(sheet1_text)
    print(f"  → {len(rows1)}행 로드")

    print("📥 시트2 (카테고리 분류) 다운로드 중...")
    sheet2_text = download_csv(SHEET2_URL)
    h2, rows2 = parse_csv(sheet2_text)
    print(f"  → {len(rows2)}행 로드")

    # --- 시트1 파싱: 사전등록 데이터 (리스트 기반, 동명이인 지원) ---
    # 컬럼: 타임스탬프, 이메일, ① 성함, ② 소속, ③ 직함, ④ 자기소개, ⑤ 프로필 이미지, ..., [13] Column 14 (취소/중복 표시)
    all_entries = []
    for row in rows1:
        name = row[2].strip() if len(row) > 2 else ""
        if not name:
            continue
        # 중복 표시된 이름 스킵
        if "(중복)" in name:
            continue
        # 테스트 데이터 스킵
        if len(name) < 2 or not re.match(r"^[가-힣a-zA-Z\s]+$", name.replace(" ", "")):
            print(f"  스킵 (유효하지 않은 이름): '{name}'")
            continue

        col14 = row[13].strip() if len(row) > 13 else ""
        all_entries.append({
            "name": name,
            "organization": row[3].strip() if len(row) > 3 else "",
            "title": row[4].strip() if len(row) > 4 else "",
            "intro": row[5].strip() if len(row) > 5 else "",
            "image_url": row[6].strip() if len(row) > 6 else "",
            "col14": col14,
        })

    # 중복 제출 처리: 같은 이름+소속이면 내용이 더 충실한 것을 유지
    seen = {}
    for entry in all_entries:
        key = (entry["name"], entry["organization"])
        if key in seen:
            prev = seen[key]
            # 자기소개가 더 충실한 쪽을 유지 (빈 값이나 ~~ 같은 건 버림)
            prev_score = len(prev["intro"]) if prev["intro"] not in ("", "~~", "-") else 0
            curr_score = len(entry["intro"]) if entry["intro"] not in ("", "~~", "-") else 0
            if curr_score > prev_score:
                print(f"  중복 제출: {entry['name']} ({entry['organization']}) → 최신 유지")
                seen[key] = entry
            else:
                print(f"  중복 제출: {entry['name']} ({entry['organization']}) → 기존 유지")
        else:
            seen[key] = entry

    # 취소자 제외
    registration_list = []
    cancelled_count = 0
    for entry in seen.values():
        if "취소" in entry["col14"]:
            print(f"  제외 (참석 취소): {entry['name']}")
            cancelled_count += 1
            continue
        registration_list.append(entry)

    print(f"\n✅ 시트1 유효 등록자: {len(registration_list)}명")
    print(f"❌ 취소/중복 제외: {cancelled_count}명")

    # --- 시트2 파싱: 카테고리 분류 (이름+소속으로 매칭) ---
    # 컬럼: (빈), 연번, 대구분, 중구분, 명찰구분, 유입구분, 성함, 사전등록, 연락처, 이메일, 소속, 직함, ...
    category_by_name = {}       # name → category (단일 매칭용)
    category_by_name_org = {}   # (name, org) → category (동명이인용)
    for row in rows2:
        name = row[6].strip() if len(row) > 6 else ""
        if not name:
            continue
        mid_cat = row[3].strip() if len(row) > 3 else ""
        org = row[10].strip() if len(row) > 10 else ""

        # 카카오 → AI・기술로 통합
        if mid_cat == "카카오":
            mid_cat = "AI・기술"
        if mid_cat:
            category_by_name[name] = mid_cat
            category_by_name_org[(name, org)] = mid_cat

    print(f"✅ 시트2 분류자: {len(category_by_name)}명")

    # --- 시트1 기반 프로필 생성 (동명이인 포함, 전원 포함) ---
    profiles = []
    no_category = []

    for reg in registration_list:
        name = reg["name"]
        org = reg["organization"]
        # 카테고리 매칭: 이름+소속 → 이름만 → 미분류
        category = category_by_name_org.get((name, org), "")
        if not category:
            category = category_by_name.get(name, "")

        profile = {
            "name": name,
            "organization": org,
            "title": reg["title"],
            "intro": reg["intro"],
            "image_url": reg["image_url"],
            "category": category,
        }

        if not category:
            no_category.append(name)

        profiles.append(profile)

    # 이름순 정렬
    profiles.sort(key=lambda p: p["name"])

    print(f"\n📊 결과: 총 {len(profiles)}명")
    if no_category:
        print(f"  ⚠ 카테고리 미분류: {len(no_category)}명 → '기타'로 분류")
        for n in no_category:
            print(f"    - {n}")
        for p in profiles:
            if not p["category"]:
                p["category"] = "기타"

    # --- 카테고리 통계 ---
    cat_counts = {}
    for p in profiles:
        c = p["category"]
        cat_counts[c] = cat_counts.get(c, 0) + 1

    print("\n📋 카테고리 분포:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}명")

    # --- 이미지 다운로드 (기존 이미지 폴더 초기화) ---
    import glob as glob_mod
    old_images = glob_mod.glob(os.path.join(IMAGES_DIR, "*.jpg"))
    if old_images:
        print(f"\n🗑️  기존 이미지 {len(old_images)}개 삭제...")
        for f in old_images:
            os.remove(f)

    print(f"\n🖼️  프로필 이미지 다운로드 중...")
    success = 0
    fail = 0
    for i, p in enumerate(profiles):
        drive_id = extract_drive_id(p["image_url"])
        if drive_id:
            # 파일명: Google Drive ID 기반 (사람-이미지 매핑 안정적)
            filename = f"{drive_id}.jpg"
            ok = download_image(drive_id, filename)
            if ok:
                p["image"] = f"images/{filename}"
                success += 1
            else:
                p["image"] = None
                fail += 1
            time.sleep(0.3)  # Rate limit 방지
        else:
            p["image"] = None

    print(f"  ✅ 성공: {success}  ✗ 실패: {fail}")

    # --- JSON 출력 ---
    output = []
    for i, p in enumerate(profiles):
        output.append({
            "id": i + 1,
            "name": p["name"],
            "organization": p["organization"],
            "title": p["title"],
            "intro": p["intro"],
            "category": p["category"],
            "image": p["image"],
        })

    # 카테고리 순서 정의 (필터 버튼 순서)
    category_order = [
        "교원",
        "장학사",
        "정책・연구",
        "교육혁신・에듀테크",
        "AI・기술",
        "사디세 강사",
    ]

    output_data = {
        "categories": category_order,
        "profiles": output,
        "total": len(output),
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    json_path = os.path.join(DATA_DIR, "profiles.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # JS 파일도 함께 생성 (file:// 프로토콜 호환)
    js_path = os.path.join(DATA_DIR, "profiles.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("const PROFILE_DATA = ")
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        f.write(";")

    print(f"\n🎉 빌드 완료!")
    print(f"  📄 {json_path}")
    print(f"  📄 {js_path}")
    print(f"  🖼️  {IMAGES_DIR}/ ({success}개 이미지)")
    print(f"  👥 총 {len(output)}명 프로필")


if __name__ == "__main__":
    main()
