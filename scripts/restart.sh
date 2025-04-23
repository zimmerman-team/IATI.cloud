echo "Restarting IATI.cloud (iaticloud, flower, workers, scheduler and revoke)"
echo "Shutting down"
sudo docker stop iaticloud celeryflower celeryworker celeryscheduler celeryrevokeworker celeryaidaworker
echo "Starting up..."
sudo docker compose up -d iaticloud celeryflower celeryworker celeryscheduler celeryrevokeworker celeryaidaworker
echo "..."
sleep 5
echo "..."
sleep 5
echo "..."
sleep 5
echo "Done restarting."
