docker compose down

docker build -t passportcommon -f Docker/Common/Dockerfile .
docker compose up -d