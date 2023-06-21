# api-dataDocker

docker build -t consulta-api .

docker run -d -p 5000:5000 --network="equatorialsmartgrid_default" --name consulta-container consulta-api



