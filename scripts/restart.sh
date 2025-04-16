echo "Restarting IATI.cloud (iaticloud, flower, workers, scheduler and revoke)"
echo "Shutting down"
sudo docker compose down iaticloud celeryflower celeryworker celeryscheduler celeryrevokeworker
echo "Starting up..."
sudo docker compose up -d iaticloud celeryflower celeryworker celeryscheduler celeryrevokeworker
echo "..."
sleep 5
echo "..."
sleep 5
echo "..."
sleep 5
echo "Done restarting."
