# Sample Product Rest API using FastAPI

This project is a simple Product REST API built with Python FastAPI. It uses PostgreSQL as the database and Redis for caching to improve performance. The main focus is on building clean and efficient REST API endpoints that support data retrieval with filtering, sorting, pagination, and exception handling.

## Features

- FastAPI backend with async SQLAlchemy
- PostgreSQL database
- Redis caching (via fastapi-cache2)
- Filtering, sorting, and pagination for product listing
- Pydantic models and validation
- Centralized exception handling and logging
- Docker & docker-compose support

# Main Focus of development

- **Global Exception Handling:** All errors are caught and returned in a consistent, structured format, to make debugging and client integration easier.
- **Redis Caching:** Queries are cached, reducing latency and database load.

## Project Structure

```
.
├── docker-compose.yml
├── dockerfile
├── requirement.txt
├── .env.sample
├── src/
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── common/
│   └── constants/
```

## API Highlights

- `GET /products/` — List products with advanced filtering, sorting, and pagination
- `GET /products/{product_id}` — Retrieve a single product by ID
- `POST /products/` — Create a new product
- `PUT /products/{product_id}` — Update a product

## Dependencies

```txt
python==3.13.4
fastapi==0.116.1
uvicorn==0.35.0
sqlalchemy==2.0.41
asyncpg==0.30.0
pydantic==2.11.7
pydantic-settings==2.10.1
python-dotenv==1.1.1
fastapi-cache2==0.2.2
redis==6.2.0
aioredis==2.0.1
Faker==37.4.2
```

## Configuration & Setup

Below are the steps to run this project locally

### 1. Clone the Repository

```bash
git clone https://github.com/LinThitHtwe/dashboard-fastapi-backend
cd dashboard-fastapi-backend
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Setup Environment Variables

Create a `.env` file in the root directory and add the following variables:

```env
DATABASE_URL=postgresql+asyncpg://<username>:<password>@localhost:5432/<your_db_name>
REDIS_URL=redis://localhost:6379
```

---

### 4. Seed Sample Data (Optional)

```bash
python -m db.seed
```

---

### 5. Start the FastAPI Server

```bash
uvicorn src.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

---
