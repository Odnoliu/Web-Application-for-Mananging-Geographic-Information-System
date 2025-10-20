# 🌐 Web Application for Mananging Geographic Information System — Vue 3 + FastAPI

## Giới thiệu
Dự án này là một ứng dụng web fullstack bao gồm:
- Frontend: xây dựng bằng Vue 3 + TypeScript + Vite
- Backend: phát triển với FastAPI (Python)

Ứng dụng hướng đến việc xây dựng hệ thống web quản trị dữ liệu địa lý hiện đại, hiệu năng cao, dễ mở rộng và có thể triển khai độc lập từng phần.

---

## Yêu cầu hệ thống

| Thành phần | Phiên bản khuyến nghị |
|-------------|------------------------|
| Node.js     | >= 18.0.0 |
| npm / yarn  | npm 9+ hoặc yarn 3+ |
| Python      | >= 3.10 |
| pip         | >= 23.0 |

---

## Cách cài đặt và chạy hệ thống

### 1. Cài đặt Frontend (Vue)
cd frontend
npm install
npm run dev

### 2. Cài đặt Backend (FastAPI)
cd backend
python -m venv venv
source venv/bin/activate    # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn main:app --reload

## Công nghệ chính
🖥️ Frontend

Vue 3 + TypeScript

Vite

TailwindCSS

Axios (gọi API)

⚡ Backend

FastAPI

Uvicorn 

SQLAlchemy / Pydantic

PostgreSQL (qua psycopg2)

python-dotenv