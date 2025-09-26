# API Documentation

## Overview

The RAG-based AI SQL Assistant provides a REST API for interacting with the system. The API is built using Django REST Framework and provides endpoints for chat interactions, database queries, and embedding management.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API allows anonymous access for development purposes. In production, implement proper authentication mechanisms.

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {...},
  "message": "Optional message",
  "error": "Error message if success is false"
}
```

## Chat API

### Send Chat Message

Send a message to the AI assistant and receive a response.

**Endpoint:** `POST /chat/`

**Request Body:**
```json
{
  "message": "How many customers do we have?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-session-id",
  "message": {
    "id": 123,
    "message_type": "assistant",
    "content": "Based on the query results, you have 1,200 customers in the database.",
    "sql_query": "SELECT COUNT(*) FROM customers;",
    "sql_result": {
      "success": true,
      "data": [["1200"]],
      "columns": ["count"],
      "row_count": 1
    },
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### Get Chat Session

Retrieve a chat session with all messages.

**Endpoint:** `GET /chat/sessions/{session_id}/`

**Response:**
```json
{
  "id": 1,
  "session_id": "uuid-session-id",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z",
  "messages": [
    {
      "id": 1,
      "message_type": "user",
      "content": "How many customers do we have?",
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "id": 2,
      "message_type": "assistant",
      "content": "You have 1,200 customers in the database.",
      "sql_query": "SELECT COUNT(*) FROM customers;",
      "sql_result": {...},
      "created_at": "2024-01-01T12:00:30Z"
    }
  ]
}
```

### List Chat Sessions

Get a list of recent chat sessions.

**Endpoint:** `GET /chat/sessions/`

**Response:**
```json
[
  {
    "id": 1,
    "session_id": "uuid-session-id-1",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:05:00Z",
    "messages": [...]
  },
  {
    "id": 2,
    "session_id": "uuid-session-id-2",
    "created_at": "2024-01-01T11:00:00Z",
    "updated_at": "2024-01-01T11:15:00Z",
    "messages": [...]
  }
]
```

## Database API

### Execute SQL Query

Execute a safe SQL query against the database.

**Endpoint:** `POST /database/execute/`

**Request Body:**
```json
{
  "query": "SELECT name, email FROM customers LIMIT 5;"
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    ["John Doe", "john.doe@email.com"],
    ["Jane Smith", "jane.smith@email.com"],
    ["Bob Johnson", "bob.johnson@email.com"]
  ],
  "columns": ["name", "email"],
  "row_count": 3,
  "query": "SELECT name, email FROM customers LIMIT 5;"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Query contains potentially unsafe operations",
  "query": "DROP TABLE customers;"
}
```

### Test Database Connection

Test the database connection.

**Endpoint:** `GET /database/test/`

**Response:**
```json
{
  "success": true,
  "message": "Database connection successful",
  "result": 1
}
```

### List Tables

Get a list of available database tables.

**Endpoint:** `GET /database/tables/`

**Response:**
```json
{
  "success": true,
  "tables": [
    "branches",
    "customers",
    "accounts",
    "transactions",
    "credit_cards",
    "credit_card_transactions",
    "loans",
    "loan_payments"
  ],
  "count": 8
}
```

### Get Table Information

Get detailed information about a specific table.

**Endpoint:** `GET /database/tables/{table_name}/`

**Response:**
```json
{
  "success": true,
  "table_name": "customers",
  "columns": [
    {
      "name": "customer_id",
      "type": "integer",
      "nullable": false,
      "default": null
    },
    {
      "name": "first_name",
      "type": "character varying",
      "nullable": false,
      "default": null
    },
    {
      "name": "email",
      "type": "character varying",
      "nullable": false,
      "default": null
    }
  ]
}
```

## Embeddings API

### Create Schema Embedding

Create an embedding for a database schema.

**Endpoint:** `POST /embeddings/embed/`

**Request Body:**
```json
{
  "table_name": "customers",
  "ddl_statement": "CREATE TABLE customers (id INT, name VARCHAR(100));",
  "description": "Customer information and demographics"
}
```

**Response:**
```json
{
  "success": true,
  "embedding_id": "uuid-embedding-id",
  "message": "Schema for customers embedded successfully"
}
```

### Search Similar Schemas

Search for schemas similar to a given query.

**Endpoint:** `POST /embeddings/search/`

**Request Body:**
```json
{
  "query": "customer information",
  "limit": 3
}
```

**Response:**
```json
{
  "success": true,
  "query": "customer information",
  "results": [
    {
      "table_name": "customers",
      "ddl_statement": "CREATE TABLE customers (id INT, name VARCHAR(100));",
      "description": "Customer information and demographics",
      "score": 0.95
    },
    {
      "table_name": "accounts",
      "ddl_statement": "CREATE TABLE accounts (id INT, customer_id INT);",
      "description": "Customer bank accounts",
      "score": 0.72
    }
  ]
}
```

### List All Schemas

Get all embedded schemas.

**Endpoint:** `GET /embeddings/schemas/`

**Response:**
```json
{
  "success": true,
  "schemas": [
    {
      "table_name": "customers",
      "ddl_statement": "CREATE TABLE customers (...);",
      "description": "Customer information",
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "table_name": "accounts",
      "ddl_statement": "CREATE TABLE accounts (...);",
      "description": "Bank accounts",
      "created_at": "2024-01-01T12:01:00Z"
    }
  ],
  "count": 2
}
```

### Delete Schema Embedding

Delete an embedded schema.

**Endpoint:** `DELETE /embeddings/schemas/{table_name}/`

**Response:**
```json
{
  "success": true,
  "message": "Schema for customers deleted successfully"
}
```

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid request format or parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error

### Error Response Format

```json
{
  "success": false,
  "error": "Detailed error message",
  "details": {
    "field": ["Specific field validation error"]
  }
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting based on:
- IP address
- Session ID
- User authentication

## Security Considerations

### SQL Execution Security

The database API implements several security measures:

1. **Read-only queries**: Only SELECT statements are allowed
2. **Query timeout**: Queries timeout after 30 seconds (configurable)
3. **Result limits**: Maximum 1000 rows returned (configurable)
4. **SQL injection prevention**: Query parsing and validation

### Unsafe Operations

The following operations are blocked:
- INSERT, UPDATE, DELETE statements
- DDL operations (CREATE, ALTER, DROP)
- System functions and procedures
- File operations

## Example Usage

### Python Client Example

```python
import requests

# Send a chat message
response = requests.post('http://localhost:8000/api/chat/', json={
    'message': 'How many customers do we have?'
})

data = response.json()
print(f"Response: {data['message']['content']}")

# Execute a direct SQL query
response = requests.post('http://localhost:8000/api/database/execute/', json={
    'query': 'SELECT COUNT(*) FROM customers;'
})

data = response.json()
print(f"Customer count: {data['data'][0][0]}")
```

### JavaScript Client Example

```javascript
// Send a chat message
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Show me recent transactions'
  })
});

const data = await response.json();
console.log('Response:', data.message.content);

// Search for similar schemas
const searchResponse = await fetch('http://localhost:8000/api/embeddings/search/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'transaction data',
    limit: 2
  })
});

const searchData = await searchResponse.json();
console.log('Similar schemas:', searchData.results);
```

### cURL Examples

```bash
# Send a chat message
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many customers do we have?"}'

# Execute SQL query
curl -X POST http://localhost:8000/api/database/execute/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) FROM customers;"}'

# List tables
curl http://localhost:8000/api/database/tables/

# Search schemas
curl -X POST http://localhost:8000/api/embeddings/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "customer information", "limit": 3}'
```

## Testing the API

Use the provided test script to verify API functionality:

```bash
python scripts/test_system.py
```

This script tests all API endpoints and verifies system integration.