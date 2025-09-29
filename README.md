# RAG-based AI SQL Assistant

A modern AI-powered SQL assistant that leverages RAG (Retrieval-Augmented Generation) to help users query banking databases using natural language. The system combines a locally running open-source LLM via Ollama with containerized services for a hybrid deployment architecture.

## 🌟 Features

- **Natural Language to SQL**: Ask questions in plain English and get SQL queries automatically generated
- **RAG Implementation**: Uses vector embeddings of database schemas for intelligent query generation
- **Secure Execution**: Read-only SQL execution with timeout and result limits
- **Modern UI**: React-based chat interface with syntax highlighting and result visualization
- **Hybrid Architecture**: Local Ollama LLM with containerized supporting services
- **Banking Domain**: Pre-configured with comprehensive banking database schema

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │     Ollama      │
│   (React)       │◄──►│    (Django)      │◄──►│   (Local LLM)   │
│   Port: 3000    │    │   Port: 8000     │    │  Port: 11434    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼───┐  ┌────▼────┐  ┌──▼──────┐
            │PostgreSQL │  │ Qdrant  │  │ Redis   │
            │Port: 5432 │  │Port:6333│  │Port:6379│
            └───────────┘  └─────────┘  └─────────┘
```

### Core Components

- **Frontend**: React TypeScript application with modern chat interface
- **Backend**: Django REST API with secure SQL execution and RAG pipeline
- **Ollama**: Local LLM service for SQL generation and natural language responses
- **Qdrant**: Vector database for schema embeddings and similarity search
- **PostgreSQL**: Banking database with sample data
- **Redis**: Caching and session management

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Ollama installed locally ([ollama.ai](https://ollama.ai))
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd rag-sql-assistant
   ```

2. **Run the automated setup:**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Qdrant Dashboard: http://localhost:6333/dashboard

### Manual Setup (Alternative)

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start Ollama and pull model:**
   ```bash
   ollama serve
   ollama pull llama3.2  # or your preferred model
   ```

3. **Start services:**
   ```bash
   docker-compose up -d --build
   ```

4. **Initialize database and embeddings:**
   ```bash
   # Run migrations
   docker-compose exec backend python manage.py migrate

   # Create schema embeddings
   python scripts/embed_schemas.py
   ```

5. **Test the system:**
   ```bash
   python scripts/test_system.py
   ```

## 💬 Usage Examples

Once the system is running, try these natural language queries:

### Customer Queries
- "How many customers do we have?"
- "Show me customers from New York"
- "List customers with high credit scores"
- "Find customers by employment status"

### Account Queries
- "What's the total balance across all accounts?"
- "Show me the top 10 customers by account balance"
- "List all business accounts"
- "Find accounts with negative balances"

### Transaction Queries
- "Show recent transactions"
- "What are the largest transactions this month?"
- "Find all ATM transactions"
- "Show transactions by merchant category"

### Loan Queries
- "How many active loans do we have?"
- "What's the average loan amount?"
- "Show customers with delinquent loans"
- "List mortgage loans over $300,000"

## 🗄️ Database Schema

The system includes a comprehensive banking database with:

- **branches**: Bank branch locations and information
- **customers**: Customer demographics, employment, and risk data
- **accounts**: Bank accounts with balances and types
- **transactions**: Transaction history with amounts and descriptions
- **credit_cards**: Credit card information and limits
- **credit_card_transactions**: Credit card transaction history
- **loans**: Loan products with terms and status
- **loan_payments**: Loan payment history

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run Django development server
python manage.py runserver
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npx playwright test

# System integration tests
python scripts/test_system.py
```

## 🔒 Security Features

- **Read-only SQL execution**: Only SELECT statements allowed
- **Query timeout protection**: Configurable timeout for long-running queries
- **Result size limits**: Maximum number of rows returned
- **SQL injection prevention**: Query parsing and validation
- **Schema-only embedding**: No actual data embedded, only table structures

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/banking_db

# AI Services
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
QDRANT_URL=http://localhost:6333

# Security
SQL_QUERY_TIMEOUT=30
MAX_RESULT_ROWS=1000

# Django
DEBUG=True
SECRET_KEY=your-secret-key
```

### Ollama Models

Recommended models for different use cases:

- **Development**: `llama3.2` (balanced performance/speed)
- **Production**: `llama3.1:70b` (better accuracy)
- **Resource-constrained**: `llama3.2:1b` (faster responses)

## 🐳 Docker Configuration

### Services

- **postgres**: PostgreSQL database with banking schema
- **qdrant**: Vector database for embeddings
- **redis**: Caching and session storage
- **backend**: Django API server
- **frontend**: React development server

### Volumes

- `postgres_data`: Persistent database storage
- `qdrant_data`: Vector database storage
- `redis_data`: Cache storage

## 📊 API Endpoints

### Chat API
- `POST /api/chat/` - Send chat message
- `GET /api/chat/sessions/` - List chat sessions
- `GET /api/chat/sessions/{id}/` - Get session details

### Database API
- `POST /api/database/execute/` - Execute SQL query
- `GET /api/database/test/` - Test database connection
- `GET /api/database/tables/` - List available tables
- `GET /api/database/tables/{name}/` - Get table information

### Embeddings API
- `POST /api/embeddings/embed/` - Create schema embedding
- `POST /api/embeddings/search/` - Search similar schemas
- `GET /api/embeddings/schemas/` - List all schemas

## 🧪 Testing

The project includes comprehensive testing:

- **Unit Tests**: Django models, services, and utilities
- **Integration Tests**: API endpoints and database operations
- **E2E Tests**: Frontend user interactions with Playwright
- **System Tests**: Full stack integration testing

Run tests with:
```bash
# All backend tests
pytest

# Specific test file
pytest tests/test_chat_api.py

# With coverage
pytest --cov=apps

# E2E tests
npx playwright test
```

## 🚀 Deployment

### Production Considerations

1. **Environment Configuration**:
   - Use production database credentials
   - Set `DEBUG=False`
   - Configure proper `ALLOWED_HOSTS`
   - Use strong `SECRET_KEY`

2. **Security**:
   - Enable HTTPS
   - Configure CORS properly
   - Use environment-specific secrets
   - Set up proper authentication

3. **Scaling**:
   - Use production WSGI server (gunicorn)
   - Configure reverse proxy (nginx)
   - Set up load balancing if needed
   - Monitor resource usage

4. **Ollama Deployment**:
   - Ensure adequate GPU/CPU resources
   - Consider model size vs. performance tradeoffs
   - Set up model caching and persistence

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**:
   ```bash
   # Check if Ollama is running
   ollama serve

   # Test connection
   curl http://localhost:11434/api/tags
   ```

2. **Database Connection Issues**:
   ```bash
   # Check PostgreSQL container
   docker-compose logs postgres

   # Test database connection
   docker-compose exec postgres psql -U postgres -d banking_db
   ```

3. **Qdrant Not Responding**:
   ```bash
   # Check Qdrant container
   docker-compose logs qdrant

   # Test Qdrant API
   curl http://localhost:6333/health
   ```

4. **Frontend Build Errors**:
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Logs and Debugging

```bash
# View all container logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Django debug mode
# Set DEBUG=True in .env for detailed error messages
```


