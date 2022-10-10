up:
	vagrant up --parallel

re-provision:
	vagrant up --provision

down:
	vagrant destroy --force

cleanup:
	make down || true

up-clean:
	make cleanup
	make up

ssh:
	vagrant ssh vm-jammy-1

ps:
	echo "pass"
