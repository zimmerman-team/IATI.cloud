if [[ $(systemctl list-units --all -t service --full --no-legend "mongod.service" | sed 's/^\s*//g' | cut -f1 -d' ') == mongod.service ]];
then 
    echo "MongoDB is already installed..."
else
   echo "Installing MongoDB"

   echo "Adding apt key"
   wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

   echo "Creating list file"
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

   echo "Updating"
   sudo apt-get update

   echo "Installing"
   sudo apt-get install -y mongodb-org

   echo "Starting mongod Service"
   sudo service mongod stop
   sudo service mongod start

   echo "Creating database user with name: zimmerman, what would you like the password to be?"
   read -sp 'Password: ' password
   echo "Creating the user"
   mongosh activities --quiet --eval "db.createUser({user: 'zimmerman', pwd: '${password}', roles: [{ role: 'readWrite', db: 'activities' }]})"
fi

# Enable authentication
echo "Ensuring mongo authorization is enabled."
sudo grep -q 'authorization: "enabled"' /etc/mongod.conf && echo "Authorization is already enabled, please use your appropriate username and password."
sudo grep -q 'authorization: "disabled"' /etc/mongod.conf && sudo sed -i 's/authorization: "disabled"/authorization: "enabled"/g' /etc/mongod.conf
sudo grep -q 'authorization: "enabled"' /etc/mongod.conf || echo -e 'security:\n authorization: "enabled"' >> /etc/mongod.conf

echo "Restarting MongoDB"
sudo service mongod stop  # stop/start to ensure that the config is updated
sudo service mongod start

echo "Installation Complete"
