@echo off
echo Starting AI Book with RAG Chatbot development environment...
echo.

REM Function to start backend in a new window
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && uv run python run_server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Function to start frontend in a new window
echo Starting frontend development server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo Both servers are now starting in separate windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000 (or as shown in the frontend window)
echo.
echo Press Ctrl+C in each window to stop the servers.


http://localhost:8000/docs           (Yahan tum API documentation dekh saktay ho.)
http://localhost:6333/dashboard    (Yahan tum collections aur vectors dekh saktay ho.)
http://localhost:6333/               ("HTTP/1.1 200 OK")  


______________________________________________________________________________________________


for stop or closing servers:
netstat -ano | findstr :3000   (find PID for frontend)
taskkill /PID <PID> /F

eg :
[WARNING] Something is already running on port 3000.
TCP    [::1]:3000             [::]:0                 LISTENING       7812

taskkill /PID 7812 /F

npm start

______________________________________________________________________________________________

for backend server:

netstat -ano | findstr :8000   (find PID for backend)





______________________________________________________________________________________________
______________________________________________________________________________________________


qutions about rag chat bot :

 what are the main modules in the course?
 what is Module 1: Physical AI Foundations
 What is the course structure of the Physical AI & Robotics


______________________________________________________________________________________________
______________________________________________________________________________________________



Docker container Run:

1️⃣ Qdrant server RUN nahi ho raha ?

docker ps

Agar qdrant container list me nahi:
➡️ Qdrant band hai ❌


docker ps -a

Agar dikhe: qdrant

docker start qdrant
