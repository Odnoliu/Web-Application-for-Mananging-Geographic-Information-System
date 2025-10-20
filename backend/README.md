# Backend (FastAPI)
## Giới thiệu
- Đây là phần API SERVER của ứng dụng, được xây dựng bằng FastAPI (Python)
- Cung cấp dữ liệu và xử lý dữ liệu logic cho frontend
- Giao tiếp với phía Database

## Yêu cầu hệ thống
- Python version 3.10+
- FastAPI
- Uvicorn

## Cài đặt hệ thống
cd backend
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

## Chạy Server
uvicorn main:app --reload
-> Server mặc định chạy ở: http://localhost:8000
