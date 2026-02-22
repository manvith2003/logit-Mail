# Logit Mail 

A modern, AI-powered email client re-imagined for productivity. Built with React (Vite) and FastAPI.

## Features

- **Standard Email Actions**: Compose, Reply, Star, Trash, Archive.
- **Fast Full-Text Search**: Instantly find emails.
- **AI Analysis**: Automatically detects Events, Deadlines, and Action Items (RAG pipeline in progress).
- **Persistent Sync**: Robust syncing engine with Gmail API.

## Tech Stack

- **Frontend**: React, Tailwind CSS, Lucide Icons, Vite
- **Backend**: Python FastAPI, SQLAlchemy (Async), Pydantic
- **Database**: PostgreSQL (with pgvector support planned)
- **Integration**: Gmail API (OAuth2)

## Getting Started

### Prerequisites

- Node.js & npm
- Python 3.10+
- PostgreSQL
- Google Cloud Project with Gmail API enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/manvith2003/magic-Mail.git
   cd magic-Mail
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Setup .env (see backend/.env.example)
   # Run Migrations (if any)
   # alembic upgrade head
   
   # Start Server
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
