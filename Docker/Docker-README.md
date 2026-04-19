Download docker Desktop from: https://www.docker.com/products/docker-desktop/

Create an account and login

In your terminal now, cd to OpenTickets

1. 
`Docker Login`
2. 
`Docker\generate-secrets.sh`
3. 
`docker-compose build --no-cache`
4. 
`docker-compose up -d`

To test after making changes
`docker-compose down ; docker-compose build --no-cache ; docker-compose up -d`
To see the running containers 
`docker ps`