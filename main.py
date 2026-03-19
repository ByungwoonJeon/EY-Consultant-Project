import os
import base64
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="Invoice Structured Data Extraction")

# Setup Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Define input directory for batch processing
INPUT_DIR = "input"
os.makedirs(INPUT_DIR, exist_ok=True)

# Configure Gemini API using the loaded API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    genai.configure(api_key=api_key)

# The user requested Gemini 3.1 Pro. The closest applicable flagship model
# for vision and structured JSON output is 'gemini-1.5-pro-latest' or 'gemini-1.5-flash'. 
MODEL_NAME = "gemini-3.1-pro-preview"

# System prompt configured as per the requirements to extract full text and structured JSON
SYSTEM_PROMPT = """[과업: 영수증/인보이스 데이터 추출 및 구조화]
다음 단계에 따라 이미지 정보를 처리하십시오:

[Full_Text]: 이미지에 포함된 모든 텍스트를 줄바꿈을 유지하며 정확히 추출하십시오.

[Structured_Data]: 추출된 정보를 바탕으로 다음 필드를 포함하는 JSON을 생성하십시오:
document_type: (영수증, 디지털 영수증, 인보이스 중 하나)
vendor_info: { "name": "상호명", "address": "주소", "tel": "전화번호" }
transaction_date: "YYYY-MM-DD"
line_items: [ { "item": "품목명", "quantity": 수량, "unit_price": 단가, "amount": 총금액 } ]
financial_summary: { "subtotal": 공급가액, "tax": 세액, "total_amount": 최종 결제 금액 }
currency: "통화 코드(예: KRW, USD)"

[출력 형식]: 반드시 아래 JSON 구조로만 응답하십시오.
{
  "full_text": "...",
  "structured_data": {
    "document_type": "...",
    "vendor_info": { "name": "...", "address": "...", "tel": "..." },
    "transaction_date": "...",
    "line_items": [ { "item": "...", "quantity": ..., "unit_price": ..., "amount": ... } ],
    "financial_summary": { "subtotal": ..., "tax": ..., "total_amount": ... },
    "currency": "..."
  }
}
"""

@app.get("/", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    """
    Render the main dashboard interface using HTML templates.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/files")
async def get_input_files():
    """
    Retrieve the list of valid image files from the input directory.
    """
    try:
        files = []
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        for filename in os.listdir(INPUT_DIR):
            if filename.lower().endswith(valid_extensions):
                files.append(filename)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/image/{filename}")
async def get_image_base64(filename: str):
    """
    Encode an image to base64 to display it in the frontend UI safely.
    Handles Korean filenames properly via Unicode parsing in FastAPI.
    """
    file_path = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Determine the MIME type
        ext = filename.split(".")[-1].lower()
        mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
            
        return {"filename": filename, "mime_type": mime_type, "data": encoded_string}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/{filename}")
async def analyze_receipt_image(filename: str):
    """
    Process the requested image through Gemini model and return structured JSON.
    """
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set correctly in .env file.")

    file_path = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Load the image for Gemini processing
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
            
        ext = filename.split(".")[-1].lower()
        mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        
        image_part = {
            "mime_type": mime_type,
            "data": image_data
        }

        # Setup generation model enforcing application/json MIME type constraint
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        # Prompt the model to analyze based on system instruction restrictions
        prompt = "이미지의 텍스트를 추출하고 지정된 JSON 구조로 결과를 반환하십시오."
        response = model.generate_content([prompt, image_part])
        
        # Parse output properly as pure JSON
        result_json = json.loads(response.text)
        
        return {"filename": filename, "status": "success", "result": result_json}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Gemini Model returned malformed JSON response.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
