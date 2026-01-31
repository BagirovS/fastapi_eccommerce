# FastAPI E-commerce API

A modern, asynchronous e-commerce REST API built with FastAPI, SQLAlchemy, and PostgreSQL. This API provides comprehensive functionality for managing users, categories, products, and reviews with role-based access control.

## Features

- **User Management**: Registration, authentication with JWT tokens (access & refresh), role-based access control
- **Category Management**: Hierarchical categories with full CRUD operations
- **Product Management**: Product catalog with category filtering, seller-specific operations
- **Review System**: Product reviews with automatic rating calculation
- **Authentication**: Secure JWT-based authentication with refresh token support
- **Role-Based Access**: Different permissions for buyers and sellers
- **Soft Delete**: All entities support soft deletion (is_active flag)

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - Async ORM for database operations
- **PostgreSQL** - Relational database (via asyncpg)
- **Alembic** - Database migrations
- **Pydantic** - Data validation using Python type annotations
- **JWT** - JSON Web Tokens for authentication
- **bcrypt** - Password hashing
- **Docker** - Containerization support

## Project Structure

```
fastapi_ecommerce/
├── app/
│   ├── routers/          # API route handlers
│   │   ├── users.py      # User authentication and management
│   │   ├── categories.py # Category CRUD operations
│   │   ├── products.py   # Product CRUD operations
│   │   └── reviews.py    # Review CRUD operations
│   ├── models/           # SQLAlchemy database models
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   └── reviews.py
│   ├── schemas.py        # Pydantic models for request/response validation
│   ├── auth.py           # Authentication utilities and dependencies
│   ├── database.py       # Database configuration
│   ├── config.py         # Application configuration
│   ├── db_depends.py     # Database dependency injection
│   ├── main.py           # FastAPI application entry point
│   └── migrations/       # Alembic database migrations
├── docker-compose.yml    # Docker configuration for PostgreSQL
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 17+
- Docker and Docker Compose (optional, for database)

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd fastapi_ecommerce
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://ecommerce_user:GG@localhost:5432/ecommerce_db
```

5. **Start PostgreSQL database**

Using Docker Compose:

```bash
docker-compose up -d
```

Or use your own PostgreSQL instance and update the `DATABASE_URL` in `app/database.py`.

6. **Run database migrations**

```bash
alembic upgrade head
```

7. **Start the development server**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Users (`/users`)

#### Register User
- **POST** `/users/`
  - Creates a new user account
  - Roles: `buyer` or `seller`
  - Returns: User object

#### Login
- **POST** `/users/token`
  - Authenticates user and returns access & refresh tokens
  - Uses OAuth2 password flow
  - Returns: `access_token`, `refresh_token`, `token_type`

#### Refresh Access Token
- **POST** `/users/access-token`
  - Generates a new access token using refresh token
  - Body: `{"refresh_token": "..."}`
  - Returns: New `access_token`

#### Refresh Token
- **POST** `/users/refresh-token`
  - Generates a new refresh token
  - Body: `{"refresh_token": "..."}`
  - Returns: New `refresh_token`

### Categories (`/categories`)

#### Get All Categories
- **GET** `/categories/`
  - Returns list of all active categories
  - Public endpoint

#### Create Category
- **POST** `/categories/`
  - Creates a new category
  - Supports hierarchical categories via `parent_id`
  - Public endpoint

#### Update Category
- **PUT** `/categories/{category_id}`
  - Updates an existing category
  - Validates parent category if `parent_id` is provided
  - Public endpoint

#### Delete Category
- **DELETE** `/categories/{category_id}`
  - Soft deletes a category (sets `is_active=False`)
  - Public endpoint

### Products (`/products`)

#### Get All Products
- **GET** `/products/`
  - Returns list of all active products
  - Public endpoint

#### Create Product
- **POST** `/products/`
  - Creates a new product
  - **Authentication**: Required (Seller role)
  - Automatically assigns product to current seller
  - Validates category exists and is active

#### Get Product by ID
- **GET** `/products/{product_id}`
  - Returns detailed product information
  - Validates product and category are active
  - Public endpoint

#### Get Products by Category
- **GET** `/products/category/{category_id}`
  - Returns all products in a specific category
  - Validates category exists and is active
  - Public endpoint

#### Update Product
- **PUT** `/products/{product_id}`
  - Updates product information
  - **Authentication**: Required (Seller role)
  - Only product owner can update
  - Validates category exists and is active

#### Delete Product
- **DELETE** `/products/{product_id}`
  - Soft deletes a product (sets `is_active=False`)
  - **Authentication**: Required (Seller role)
  - Only product owner can delete

#### Get Product Reviews
- **GET** `/products/{product_id}/reviews`
  - Returns all active reviews for a product
  - Public endpoint

### Reviews (`/reviews`)

#### Get All Reviews
- **GET** `/reviews/`
  - Returns list of all active reviews
  - Public endpoint

#### Create Review
- **POST** `/reviews/`
  - Creates a new product review
  - **Authentication**: Required (Buyer role)
  - Validates product exists and is active
  - Prevents duplicate reviews (one review per buyer per product)
  - Grade must be between 1 and 5
  - Automatically calculates and updates product rating

#### Delete Review
- **DELETE** `/reviews/{review_id}`
  - Soft deletes a review (sets `is_active=False`)
  - **Authentication**: Required (Buyer role)
  - Only review owner can delete (or admin)
  - Automatically recalculates product rating

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. There are two types of tokens:

- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

### Using Authentication

Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Flow

1. Register a user via `POST /users/`
2. Login via `POST /users/token` to get access and refresh tokens
3. Use access token for authenticated requests
4. When access token expires, use `POST /users/access-token` with refresh token to get a new access token
5. Optionally refresh the refresh token via `POST /users/refresh-token`

## User Roles

### Buyer
- Can create and delete their own reviews
- Can view all products, categories, and reviews

### Seller
- Can create, update, and delete their own products
- Can view all products, categories, and reviews

## Data Models

### User
- `id`: Integer (Primary Key)
- `email`: String (Unique, Indexed)
- `hashed_password`: String
- `is_active`: Boolean
- `role`: String (`buyer` or `seller`)

### Category
- `id`: Integer (Primary Key)
- `name`: String (3-50 characters)
- `parent_id`: Integer (Optional, Foreign Key to Category)
- `is_active`: Boolean

### Product
- `id`: Integer (Primary Key)
- `name`: String (3-100 characters)
- `description`: String (Optional, max 500 characters)
- `price`: Decimal (2 decimal places, > 0)
- `image_url`: String (Optional, max 200 characters)
- `stock`: Integer (≥ 0)
- `category_id`: Integer (Foreign Key to Category)
- `seller_id`: Integer (Foreign Key to User)
- `rating`: Integer (Optional, calculated from reviews)
- `is_active`: Boolean

### Review
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key to User)
- `product_id`: Integer (Foreign Key to Product)
- `comment`: String (Optional, min 2 characters)
- `comment_date`: DateTime
- `grade`: Integer (1-5)
- `is_active`: Boolean

## Rating System

Product ratings are automatically calculated:

- When a review is created, the product's rating is updated to the average of all active reviews
- When a review is deleted, the product's rating is recalculated
- Rating is stored as an integer (rounded average)

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Successful GET, PUT, DELETE requests
- `201 Created` - Successful POST requests
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource (e.g., duplicate review)
- `422 Unprocessable Entity` - Validation error

## Database Migrations

The project uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Development

### Running Tests

(Add test instructions when tests are implemented)

### Code Style

The project follows PEP 8 style guidelines.

## License

(Add license information)

## Contributing

(Add contributing guidelines)

## Support

For issues and questions, please open an issue in the repository.
