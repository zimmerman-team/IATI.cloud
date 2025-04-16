echo "Clearing celery queue"
sudo docker exec -it rabbitmq rabbitmqctl purge_queue celery
