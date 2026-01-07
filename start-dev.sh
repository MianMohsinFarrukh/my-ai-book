#!/bin/bash

# Startup script for AI Book with RAG Chatbot development environment

echo "Starting AI Book with RAG Chatbot development environment..."
echo

# Function to start backend
start_backend() {
    echo "Starting backend server..."
    cd backend
    uv run python run_server.py &
    BACKEND_PID=$!
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "Starting frontend development server..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
}

# Check if both backend and frontend directories exist
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found!"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found!"
    exit 1
fi

# Start backend
start_backend

# Wait a moment for backend to start
sleep 3

# Start frontend
start_frontend

# Function to handle cleanup on exit
cleanup() {
    echo
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID