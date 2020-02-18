# Build the base docker image for katana that builds WindNinja
docker build --rm -t usdaarsnwrc/katana_base:latest -f docker-base/Dockerfile .

# push the Docker image to docker hub
docker login
docker push usdaarsnwrc/katana_base:latest