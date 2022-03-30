echo "------------------------------------------------------"
echo "------------------------------------------------------"
echo "------------------------------------------------------"
echo "Installing dependencies..."

sudo bash install_mongo.sh
sudo bash install_postgis.sh
sudo bash install_postgres.sh
sudo bash install_python.sh
sudo bash install_rabbitmq.sh
sudo bash install_solr.sh
sudo bash install_nginx.sh

echo "Dependencies installed"
echo "------------------------------------------------------"
echo "------------------------------------------------------"
echo "------------------------------------------------------"

