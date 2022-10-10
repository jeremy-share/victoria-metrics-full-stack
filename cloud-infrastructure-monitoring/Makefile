up:
	docker-compose up -d --build

down:
	docker-compose down

stop:
	make down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

watch-alerts-sink:
	docker-compose logs -f alertsink

watch-alerting-all:
	docker-compose logs -f vmalert alertmanager alertsink

ps:
	docker-compose ps
