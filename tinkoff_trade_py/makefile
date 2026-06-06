# Запуск всех сервисов
up: postgres_up redis_up

# PostgreSQL
postgres_up:
	docker run -d --name postgres-local \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-e POSTGRES_DB=tinkoff_trade \
		-p 5432:5432 \
		-v postgres_data:/var/lib/postgresql/data \
		postgres:15

postgres_stop:
	docker stop postgres-local && docker rm postgres-local

# Redis
redis_up:
	docker run -d --name redis-local \
		-p 6379:6379 \
		-v redis_data:/data \
		redis:7.2 --appendonly yes

redis_stop:
	docker stop redis-local && docker rm redis-local

# Остановка всех
stop: postgres_stop redis_stop

# Очистка томов (удаляет все данные!)
clean:
	docker volume rm postgres_data redis_data