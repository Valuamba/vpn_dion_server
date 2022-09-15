#ifneq (,$(wildcard ./.env))
#include .env
#export
#ENV_FILE_PARAM = --env-file .env

#endif

send-script:
	sshpass -p "Qq654321" scp ./scripts/wireguard.sh  root@194.87.140.181:/root

wg:
	sudo bash ./scripts/wireguard.sh profile add --name Lol_2 --ipv4 10.66.66.119 --ipv6 fd42:42:42

build:
	docker build -t vpn-debian .

run:
	docker run -p 5050:5000 -tid --name vpn-debian-container -t vpn-debian

down:
	docker stop vpn-debian-container
	docker rm vpn-debian-container
	docker ps --filter "status=exited" | grep 'weeks ago' | awk '{print $1}' | xargs --no-run-if-empty docker rm
	docker rmi $(docker images --filter "dangling=true" -q --no-trunc)

sh:
	docker exec -it vpn-debian-container /bin/bash

logs:
	docker logs -t  vpn-debian-container


