run_crawler:
	@echo "===== Run microservice crawler ====="
	docker build --build-arg MICROSERVICE=crawler -f dev.Dockerfile -q -t crawler:latest .
	kubectl apply -f microservices/crawler/deployment_dev.yaml
	@echo "\n"

run_converter:
	@echo "===== Run microservice converter ====="
	docker build --build-arg MICROSERVICE=converter -f dev.Dockerfile -q -t converter:latest .
	kubectl apply -f microservices/converter/deployment_dev.yaml
	@echo "\n"

run_storer:
	@echo "===== Run microservice storer ====="
	docker build --build-arg MICROSERVICE=storer -f dev.Dockerfile -q -t storer:latest .
	kubectl apply -f microservices/storer/deployment_dev.yaml
	@echo "\n"

run_microservices: run_storer run_converter run_crawler

run_influx:
	@echo "===== Run InfluxDB ====="
	docker volume create test-task-influx
	docker image pull influxdb:latest
	docker run -d -p 8086:8086 --name influx -v test-task-influx:/var/lib/influxdb influxdb:latest
	@echo "\n"

run_grafana:
	@echo "===== Run Grafana ====="
	docker volume create test-task-grafana
	docker image pull influxdb:latest
	docker run -d -p 3000:3000 --name grafana grafana/grafana:latest
	@echo "\n"

stop:
	@echo "===== Stop and remove running containers and services ====="
	docker stop grafana || true && docker rm grafana || true
	docker stop influx || true && docker rm influx || true
	kubectl delete deployment.apps/crawler || true
	kubectl delete deployment.apps/converter service/converter-service || true
	kubectl delete deployment.apps/storer service/storer-service || true
	@echo "\n"

all: stop run_influx run_grafana run_microservices
