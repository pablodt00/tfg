build-dev:
	docker build -f docker/common/Dockerfile -t tfg-dev .

dev-shell:
	docker run -it tfg-dev /bin/bash
