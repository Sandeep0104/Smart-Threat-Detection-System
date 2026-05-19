# Smart Threat Detection System (AI Security Analyst)

A full-stack AI-powered cybersecurity assistant that scans server logs, detects suspicious activity, explains threats in plain language, suggests fixes, and generates incident report PDFs — all through a premium dark-themed dashboard.

## 🚀 Features

- **Intelligent Log Parsing**: Automatically detects and parses `auth.log`, `syslog`, and `access.log` formats.
- **Threat Detection Engine**: Identifies brute-force attacks, port scanning, unusual hour access, and privilege escalation attempts.
- **AI-Powered Analysis**: Uses LangChain and OpenAI to summarize attacks, explain threats in plain English, and provide actionable remediation steps.
- **RAG Chat Interface**: Chat with your logs! Ask questions like *"Why was IP 192.168.1.100 blocked?"* and get answers backed by log evidence.
- **Incident Reporting**: Automatically generate professional PDF incident reports with executive summaries, threat breakdowns, and risk scores.
- **Premium Dashboard**: A modern, responsive React frontend featuring a dark cybersecurity theme, glassmorphism, and interactive data visualizations.

## 🏗️ Architecture

- **Frontend**: React (Vite), CSS Modules, CSS Grid, Custom Design System
- **Backend**: FastAPI (Python), REST API
- **AI & ML**: LangChain, OpenAI API (GPT-4o-mini), FAISS Vector Store
- **PDF Generation**: ReportLab

## 📂 Project Structure

- `frontend/`: React application (Dashboard, Log Upload, Threat Timeline, Chat Panel)
- `backend/`: FastAPI server (Log Parser, Threat Detector, AI Analyzer, Vector Store, PDF Generator)
- `backend/sample_logs/`: Realistic sample log files for immediate testing.

## 🛠️ Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.9+)
- OpenAI API Key

### Backend Setup
1. Navigate to the `backend` directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file from `.env.example` and add your `OPENAI_API_KEY`.
6. Start the FastAPI server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to the `frontend` directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the Vite development server: `npm run dev`

## 🔒 Security Note
This application requires an OpenAI API key for AI features. Ensure your API key is stored securely in the `.env` file and never committed to version control.

## 📄 License
This project is licensed under the MIT License.
