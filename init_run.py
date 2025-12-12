import os
import zipfile
import shutil
import subprocess
import sys

# ตั้งชื่อโปรเจ็กต์
PROJECT_NAME = "PhoneTel"
ROOT = os.path.join(os.getcwd(), PROJECT_NAME)

# สร้างโฟลเดอร์ใหม่
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT, exist_ok=True)

# ฟังก์ชันเขียนไฟล์
def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

# ----------------------------
# Backend
# ----------------------------
write("backend/app/main.py", """
from fastapi import FastAPI, WebSocket
from backend.app.ws_server import ws_manager

app = FastAPI()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.websocket("/ws/status")
async def ws_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            msg = await ws.receive_text()
    finally:
        ws_manager.disconnect(ws)
""")

write("backend/app/ws_server.py", """
class WSManager:
    def __init__(self): self.active=[]
    async def connect(self, ws): await ws.accept(); self.active.append(ws)
    def disconnect(self, ws): self.active.remove(ws) if ws in self.active else None
    async def broadcast(self, msg):
        for c in list(self.active):
            try: await c.send_text(msg)
            except: self.disconnect(c)

ws_manager = WSManager()
""")

write("backend/requirements.txt", "fastapi\nuvicorn[standard]\n")

write("backend/Dockerfile", """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""")

# ----------------------------
# Frontend
# ----------------------------
write("frontend/pages/index.js", """
export default function Home(){ return (<div style={{textAlign:'center', fontFamily:'Arial, sans-serif'}}>
  <h1>📞 Phone(Tel) Platform 🌟</h1>
  <p>Welcome to your all-in-one communication hub with AI-powered tools 🚀🤖</p>
  <ul style={{textAlign:'left', display:'inline-block'}}>
    <li>🔹 Chat, Calls, Video Integration</li>
    <li>🔹 Real-time Notifications</li>
    <li>🔹 AI Assisted Features</li>
    <li>🔹 Fully Modular & Extensible</li>
  </ul>
</div>) }
""")

write("frontend/package.json", """
{
  "name": "frontend",
  "version": "0.1.0",
  "scripts":{"dev":"next dev","build":"next build","start":"next start"}
}
""")

# ----------------------------
# AI stubs
# ----------------------------
write("ai_generators/web_builder.py", "# 🌐 AI Web Builder Stub\n")
write("ai_generators/desktop_builder.py", "# 🖥️ AI Desktop Builder Stub\n")
write("ai_generators/mobile_builder.py", "# 📱 AI Mobile Builder Stub\n")

# ----------------------------
# Docker Compose
# ----------------------------
write("docker-compose.yml", """
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
""")

# ----------------------------
# Vercel config
# ----------------------------
write("vercel.json", """
{
  "version": 2,
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/next" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "frontend/$1" }
  ]
}
""")

# ----------------------------
# init_run.py
# ----------------------------
write("init_run.py", """
import threading, subprocess, os, sys, time

def run_backend():
    os.chdir(os.path.join(os.getcwd(), "backend"))
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def run_frontend():
    os.chdir(os.path.join(os.getcwd(), "frontend"))
    subprocess.run(["npm", "install"])
    subprocess.run(["npm", "run", "dev"])

t1 = threading.Thread(target=run_backend)
t2 = threading.Thread(target=run_frontend)
t1.start()
time.sleep(5)
t2.start()
t1.join()
t2.join()
""")

# ----------------------------
# README.md
# ----------------------------
write("README.md", """
# Phone(Tel) Platform 📞

## Overview 🌟
Phone(Tel) เป็นแพลตฟอร์มสื่อสารและการจัดการ AI ที่ครบวงจร
- Backend: FastAPI + WebSocket
- Frontend: Next.js UI รองรับมือถือและเดสก์ท็อป
- AI Generators: Stub สำหรับสร้างเว็บ, Desktop, Mobile ด้วย AI
- Deployment: Docker + Vercel-ready

## Quick Start 🚀
python init_run.py

Backend: http://localhost:8000
Frontend: http://localhost:3000

## Contact 📧
Email: rufiodinoto244@gmail.com
WhatsApp: +660823727103
""")

# ----------------------------
# สร้าง ZIP
# ----------------------------
ZIP_PATH = f"{PROJECT_NAME}.zip"
with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
    for folder, _, files in os.walk(ROOT):
        for f in files:
            full = os.path.join(folder, f)
            zf.write(full, os.path.relpath(full, ROOT))

print(f"✅ ZIP ready at {ZIP_PATH}")
