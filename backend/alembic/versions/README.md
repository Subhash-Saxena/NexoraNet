# Alembic Database Migrations

Migration scripts for database schema evolution will reside in this directory.
Migrations are generated with:
`alembic revision --autogenerate -m "description"`
and applied with:
`alembic upgrade head`
