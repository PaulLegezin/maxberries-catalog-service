set -e

echo "Выполнение миграций..."
alembic upgrade head

echo "Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000