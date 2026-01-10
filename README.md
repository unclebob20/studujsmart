# ŠtúdujSmart.sk

AI-powered study platform for Slovak students preparing for matura and exams.

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Redis

### Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd studujsmart
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate  # On Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database
```bash
createdb studujsmart
```

5. Copy environment file
```bash
cp .env.example .env
# Edit .env with your actual values
```

6. Initialize database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. Run the application
```bash
python run.py
```

The app should now be running at `http://localhost:5000`

## Project Structure

```
studujsmart/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # URL routes/views
│   ├── services/        # Business logic
│   ├── templates/       # Jinja2 templates
│   ├── static/          # CSS, JS, images
│   └── utils/           # Helper functions
├── migrations/          # Database migrations
├── tests/              # Unit tests
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
└── run.py             # Application entry point
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Test locally
4. Commit and push
5. Create pull request

## Testing

```bash
pytest
```

## Deployment

See deployment guide in docs/deployment.md