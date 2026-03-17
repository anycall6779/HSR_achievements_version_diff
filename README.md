# ⭐ 붕괴: 스타레일 — 버전별 신규 업적 비교기

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**Honkai: Star Rail** 의 버전별로 새롭게 추가된 업적을 비교하고, 보기 좋은 HTML 리포트로 생성해주는 도구입니다.

## ✨ 주요 기능

- 🔄 **버전별 업적 비교** — 두 버전 사이에 새로 추가된 업적만 확인  
- 🎨 **HTML 리포트 생성** — 다크 테마 기반의 보기 좋은 리포트를 자동 생성  
- 🏷️ **시리즈별 분류** — 업적을 카테고리(시리즈)별로 그룹핑하여 표시  
- 🖼️ **시리즈 아이콘** — 각 업적 카테고리에 해당하는 공식 아이콘 이미지 포함  
- 💎 **보상 정보** — 업적별 성옥 보상량 (5 / 10 / 20) 및 총합 표시  
- 🖥️ **GUI 지원** — Tkinter 기반 GUI로 드롭다운 선택 또는 직접 버전 입력 가능  

## 🚀 실행 방법

### 요구 사항

- **Python 3.8 이상** (외부 라이브러리 불필요, 표준 라이브러리만 사용)

### 실행

```bash
python compare_achievements_gui.py
```

1. **이전 버전**과 **새 버전**을 드롭다운에서 선택하거나 직접 입력합니다.
2. **비교하기** 버튼을 클릭합니다.
3. HTML 결과 파일이 생성되고, 기본 브라우저에서 자동으로 열립니다.

## 📖 사용 예시

| 비교 | 설명 |
|------|------|
| `4.0` → `4.0.52` | 4.0 버전 이후 추가된 업적 확인 |
| `4.0` → `4.1.51` | 4.0부터 4.1.51까지 전체 신규 업적 확인 |
| `4.0.54` → `4.1.51` | 최근 패치에서 추가된 업적만 확인 |

## 🗂️ 업적 보상 기준

| 희귀도 | 성옥 보상 |
|--------|----------|
| High   | 💎 20    |
| Mid    | 💎 10    |
| Low    | 💎 5     |

## 📁 프로젝트 구조

```
HSR_achievements/
├── compare_achievements_gui.py   # 메인 GUI 스크립트 (이 파일 하나로 동작)
└── README.md
```

## 📌 데이터 출처

- **업적 데이터**: [nanoka.cc](https://hsr.nanoka.cc/achievement)
- **시리즈 아이콘**: [Honey Hunter World](https://starrail.honeyhunterworld.com)
- **성옥 아이콘**: [nanoka.cc static assets](https://static.nanoka.cc/assets/hsr/itemfigures/900001.webp)

> ⚠️ 이 프로젝트는 팬 메이드 도구이며, HoYoverse와 공식적인 관련이 없습니다.  
> 모든 게임 관련 이미지 및 데이터의 저작권은 HoYoverse에 있습니다.

## 📝 License

MIT License
