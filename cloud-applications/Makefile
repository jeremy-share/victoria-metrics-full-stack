build:
	(cd frontend-service && make docker-build)
	docker-compose build --pull

up:
	make build
	docker-compose up -d

up-no-apps:
	docker-compose up -d vmauth vmagent

down:
	docker-compose down

stop:
	make down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

ps:
	docker-compose ps
