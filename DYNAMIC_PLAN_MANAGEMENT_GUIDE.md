# Dynamic Hosting Plan Management API Usage Guide

This guide demonstrates how to use the new dynamic hosting plan management API endpoints.

## Authentication

All admin endpoints require authentication with a Bearer token:

```bash
Authorization: Bearer <your_jwt_token>
```

## Category Management

### 1. Create a New Category

```bash
POST /api/admin/categories
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "WordPress Containers",
  "type": "container",
  "description": "Containerized WordPress hosting with automatic scaling and management",
  "features": [
    "Auto-scaling",
    "Managed WordPress",
    "SSL Certificates",
    "CDN Integration",
    "Staging Environment"
  ],
  "resource_specs": {
    "required_fields": ["cpu_limit", "memory_limit", "storage", "traffic_limit"],
    "optional_fields": ["wordpress_sites", "staging_sites", "cdn_bandwidth", "ssl_certificates"],
    "field_types": {
      "cpu_limit": "string",
      "memory_limit": "string",
      "storage": "string",
      "traffic_limit": "string",
      "wordpress_sites": "integer",
      "staging_sites": "integer"
    }
  }
}
```

### 2. List All Categories

```bash
GET /api/admin/categories
Authorization: Bearer <token>
```

### 3. Update a Category

```bash
PUT /api/admin/categories/{category_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "description": "Updated description for the category",
  "features": ["Updated Feature 1", "Updated Feature 2"]
}
```

### 4. Delete a Category

```bash
DELETE /api/admin/categories/{category_id}
Authorization: Bearer <token>
```

## Plan Management

### 1. Create a New Plan

```bash
POST /api/admin/plans
Content-Type: application/json
Authorization: Bearer <token>

{
  "category": "category_id_here",
  "name": "WordPress Starter",
  "description": "Perfect for small WordPress sites with moderate traffic",
  "price": 15.99,
  "resources": {
    "cpu_limit": "1 vCPU",
    "memory_limit": "2 GB RAM",
    "storage": "20 GB SSD",
    "traffic_limit": "100 GB/month",
    "wordpress_sites": 1,
    "staging_sites": 1
  },
  "features": [
    "1 WordPress Site",
    "Free SSL Certificate",
    "Daily Backups",
    "24/7 Support"
  ],
  "billing_cycle": "monthly"
}
```

### 2. List All Plans (Admin)

```bash
GET /api/admin/plans
Authorization: Bearer <token>

# Filter by category
GET /api/admin/plans?category={category_id}
Authorization: Bearer <token>
```

### 3. Update a Plan

```bash
PUT /api/admin/plans/{plan_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "price": 19.99,
  "description": "Updated plan description",
  "is_popular": true
}
```

### 4. Delete a Plan

```bash
DELETE /api/admin/plans/{plan_id}
Authorization: Bearer <token>
```

## Public Endpoints (No Authentication Required)

### Get All Public Plans

```bash
GET /api/hosting-plans

# Filter by type
GET /api/hosting-plans?plan_type=container

# Filter by category
GET /api/hosting-plans?category={category_id}
```

## Example Workflow: Setting up WordPress Container Hosting

### Step 1: Create the Category

```bash
curl -X POST "https://your-domain.com/api/admin/categories" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WordPress Containers",
    "type": "container",
    "description": "Containerized WordPress hosting with automatic scaling",
    "features": ["Auto-scaling", "Managed WordPress", "SSL Certificates"],
    "resource_specs": {
      "required_fields": ["cpu_limit", "memory_limit", "storage"],
      "optional_fields": ["wordpress_sites", "staging_sites"],
      "field_types": {
        "cpu_limit": "string",
        "memory_limit": "string",
        "storage": "string",
        "wordpress_sites": "integer"
      }
    }
  }'
```

### Step 2: Create Plans in the Category

```bash
# Starter Plan
curl -X POST "https://your-domain.com/api/admin/plans" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "CATEGORY_ID_FROM_STEP_1",
    "name": "WordPress Starter",
    "description": "Perfect for small WordPress sites",
    "price": 15.99,
    "resources": {
      "cpu_limit": "1 vCPU",
      "memory_limit": "2 GB RAM", 
      "storage": "20 GB SSD",
      "wordpress_sites": 1
    },
    "features": ["1 WordPress Site", "Free SSL", "Daily Backups"],
    "billing_cycle": "monthly"
  }'

# Professional Plan
curl -X POST "https://your-domain.com/api/admin/plans" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "CATEGORY_ID_FROM_STEP_1",
    "name": "WordPress Professional",
    "description": "For growing WordPress sites with higher traffic",
    "price": 39.99,
    "resources": {
      "cpu_limit": "2 vCPU",
      "memory_limit": "4 GB RAM",
      "storage": "50 GB SSD", 
      "wordpress_sites": 5,
      "staging_sites": 1
    },
    "features": ["5 WordPress Sites", "Staging Environment", "Priority Support"],
    "billing_cycle": "monthly"
  }'
```

## Validation Rules

The API automatically validates:

1. **Resource Specifications**: Ensures all required fields are present and no invalid fields are included
2. **Price Constraints**: Enforces minimum/maximum price limits defined in the category
3. **Billing Cycles**: Only allows billing cycles specified in the category validation rules
4. **Duplicate Names**: Prevents duplicate plan names within the same category
5. **Category Dependencies**: Prevents deletion of categories that have associated plans

## Error Responses

The API returns detailed error messages for validation failures:

```json
{
  "detail": "Resources do not match category specifications; Price must be at least $1.0"
}
```

## Integration with Existing Plans

The system maintains backward compatibility with existing plans:

- Legacy plans continue to work through existing endpoints
- Public API `/api/hosting-plans` returns both legacy and dynamic plans
- Dynamic plans are clearly marked with `"plan_source": "dynamic"`
- Legacy plans are marked with `"plan_source": "legacy"`