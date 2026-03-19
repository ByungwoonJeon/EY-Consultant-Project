# Invoice Structured Data Extraction System (Gemini 3.1)

본 프로젝트는 **Google Gemini 3.1 Pro (Vision)** 모델을 활용하여 영수증 및 인보이스(Invoice) 이미지에서 정확한 텍스트를 추출하고, 이를 비즈니스 로직에 즉시 활용 가능한 구조화된 JSON 데이터로 변환하는 PoC(Proof of Concept) 시스템입니다.

---

## 🚀 주요 기능 (Key Features)

- **이미지 텍스트 정밀 추출 (Full Text Extraction)**: 영수증 내의 모든 텍스트를 원형 그대로 보존하며 추출합니다.
- **데이터 구조화 (Structured JSON Output)**: 비정형 이미지를 다음과 같은 체계적인 필드로 변환합니다.
  - `document_type`: 영수증, 디지털 영수증, 인보이스 분류
  - `vendor_info`: 상호명, 주소, 연락처
  - `transaction_date`: 거래 일자 (YYYY-MM-DD)
  - `line_items`: 품목별 수량, 단가, 합계 금액
  - `financial_summary`: 공급가액, 세액, 최종 결제 금액
  - `currency`: 통화 (KRW, USD 등)
- **실시간 대시보드**: `input` 폴더의 이미지를 브라우저에서 즉시 확인하고 분석 결과를 시각화합니다.

---

## 🛠 기술 스택 (Tech Stack)

- **Backend**: Python 3.9+, FastAPI, Uvicorn
- **AI/ML**: Google Generative AI (Gemini 3.1 Pro)
- **Frontend**: Jinja2 Templates, Vanilla JS, CSS
- **Tools**: python-dotenv, Pydantic

---

## 📦 설치 및 환경 설정 (Setup Guide)

### 1. 가상 환경 구축 및 의존성 설치
```bash
# venv 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 본인의 Google AI Studio API 키를 입력합니다.
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 데이터 입력
분석하고자 하는 영수증 이미지를 `input/` 디렉토리에 저장합니다. 지원 형식: `.png`, `.jpg`, `.jpeg`, `.webp`.

---

## 🖥 실행 방법 (Usage)

서버를 구동한 후 웹 브라우저를 통해 대시보드에 접속합니다.
```bash
uvicorn main.py:app --reload
```
- **Dashboard URL**: `http://127.0.0.1:8000`

---

## 📊 데이터 추출 규격 (API Response Schema)

시스템은 `application/json` 형식으로 데이터를 반환하며, 규격은 다음과 같습니다.

```json
{
  "full_text": "추출된 전체 텍스트...",
  "structured_data": {
    "document_type": "영수증",
    "vendor_info": {
      "name": "OOO 상사",
      "address": "서울특별시...",
      "tel": "02-123-4567"
    },
    "transaction_date": "2024-03-20",
    "line_items": [
      {
        "item": "상품명",
        "quantity": 1,
        "unit_price": 10000,
        "amount": 10000
      }
    ],
    "financial_summary": {
      "subtotal": 9091,
      "tax": 909,
      "total_amount": 10000
    },
    "currency": "KRW"
  }
}
```

---

## ⚖️ 면책 사항 (Disclaimer)
이 프로젝트는 AI 모델의 비결정적 특성을 기반으로 하므로, 실제 비즈니스 환경 적용 시 최종 데이터에 대한 사람의 검수(Human-in-the-loop) 과정이 수반되어야 합니다.
