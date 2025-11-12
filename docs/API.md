# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

## Authentication

Most endpoints require authentication using JWT Bearer tokens.

### Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+27123456789"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "mfa_token": "123456"  // Optional, if MFA enabled
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Authentication

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Health Checks

#### GET /health
Basic health check endpoint.

#### GET /health/ready
Readiness check (verifies database connectivity).

#### GET /health/live
Liveness check.

### User Endpoints

#### GET /api/v1/users/me
Get current user information.

**Authentication:** Required

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/users/{user_id}
Get user by ID (admin/auditor only).

**Authentication:** Required (admin/auditor role)

### Transaction Endpoints

#### POST /api/v1/transactions
Create a new transaction.

**Authentication:** Required

**Request:**
```json
{
  "transaction_type": "deposit",
  "amount": "1000.00",
  "currency": "ZAR",
  "description": "Initial deposit",
  "recipient_account": null
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "transaction_type": "deposit",
  "status": "pending",
  "amount": "1000.00",
  "currency": "ZAR",
  "reference": "TXN-ABC123DEF456",
  "description": "Initial deposit",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": null
}
```

#### GET /api/v1/transactions
List user's transactions.

**Authentication:** Required

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100, max: 1000)

#### GET /api/v1/transactions/{transaction_id}
Get transaction by ID.

**Authentication:** Required

### Data Subject Rights (POPIA)

#### GET /api/v1/data-subject/access
Access all personal information (POPIA Section 23).

**Authentication:** Required

**Response:**
```json
{
  "user_data": {...},
  "transactions": [...],
  "consents": [...],
  "audit_logs": [...],
  "exported_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/v1/data-subject/correct
Correct personal information (POPIA Section 24).

**Authentication:** Required

**Request:**
```json
{
  "field": "first_name",
  "new_value": "Jane"
}
```

#### DELETE /api/v1/data-subject/delete
Request deletion of personal information (POPIA Section 25).

**Authentication:** Required

#### GET /api/v1/data-subject/export
Export personal data in machine-readable format (POPIA: Data Portability).

**Authentication:** Required

### Compliance Endpoints

#### GET /api/v1/compliance/data-inventory
Get data inventory (POPIA: Openness requirement).

**Authentication:** Required (admin/auditor role)

#### GET /api/v1/compliance/audit-logs
Get audit logs.

**Authentication:** Required (admin/auditor role)

**Query Parameters:**
- `skip`: Number of records to skip
- `limit`: Maximum number of records
- `user_id`: Filter by user ID
- `action`: Filter by action type

#### GET /api/v1/compliance/compliance-status
Get POPIA compliance status.

**Authentication:** Required (admin role)

### MFA Endpoints

#### POST /api/v1/auth/mfa/setup
Setup MFA for user account.

**Authentication:** Required

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KG...",
  "backup_codes": []
}
```

#### POST /api/v1/auth/mfa/verify
Verify and enable MFA.

**Authentication:** Required

**Request:**
```json
{
  "token": "123456"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: ['admin']"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per user

## OpenAPI Documentation

Interactive API documentation available at:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

