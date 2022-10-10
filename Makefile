fake-internet-network:
	docker network create vm-full-stack-main || true

up:
	make fake-internet-network
	(cd cloud-infrastructure-storage/ && make up)
	(cd cloud-infrastructure-monitoring/ && make up)
	(cd cloud-applications/ && make up)
	(cd servers/ && make up)

down:
	(cd cloud-infrastructure-storage/ && make down)
	(cd cloud-infrastructure-monitoring/ && make down)
	(cd cloud-applications/ && make down)
	(cd servers/ && make down)

watch-alerts-sink:
	(cd cloud-infrastructure-monitoring/ && make watch-alerts-sink)

ps:
	@echo ""
	@echo "-----------------------------------------------------------------"
	@echo "cloud-infrastructure-storage"
	(cd cloud-infrastructure-storage/ && make ps)
	@echo "-----------------------------------------------------------------"
	@echo ""
	@echo "cloud-infrastructure-monitoring"
	(cd cloud-infrastructure-monitoring/ && make ps)
	@echo "-----------------------------------------------------------------"
	@echo ""
	@echo "cloud-applications"
	(cd cloud-applications/ && make ps)
	@echo "-----------------------------------------------------------------"
	@echo ""
	@echo "servers"
	(cd servers/ && make ps)
	@echo "-----------------------------------------------------------------"
	@echo ""
