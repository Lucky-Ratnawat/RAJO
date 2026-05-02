# API Service

FastAPI service for:

- authentication and roles
- catalog and categories
- inventory
- orders
- notifications

Current API coverage includes:

- public category and product listing
- admin CRUD for categories and products
- admin inventory management
- buyer order creation and order lookup
- admin order status updates

## Local Setup

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env`.
3. Set `DATABASE_URL` to your local Postgres or Supabase connection string.
4. Run migrations with Alembic.
5. Start the API with Uvicorn.

## Useful Commands

```bash
alembic upgrade head
uvicorn app.main:app --reload
```
