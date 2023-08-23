# ask the user if they ran this bash script as sudo, if not exit
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Ask the user if they are sure they want to copy these schemas, if not exit
read -p "Are you sure you want to copy the schemas? (y/N) " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting..."
    exit 1
fi
echo "Continuing..."

echo "Active docker containers"
docker ps

echo "Please enter your docker 'CONTAINER ID' for the active Solr container with the image bitnami/solr:"
read solr_container_id

echo "The ID is: $solr_container_id"

docker cp ./direct_indexing/solr/cores/activity/managed-schema $solr_container_id:/bitnami/solr/server/solr/activity/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/budget/managed-schema $solr_container_id:/bitnami/solr/server/solr/budget/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/dataset/managed-schema $solr_container_id:/bitnami/solr/server/solr/dataset/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/organisation/managed-schema $solr_container_id:/bitnami/solr/server/solr/organisation/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/publisher/managed-schema $solr_container_id:/bitnami/solr/server/solr/publisher/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/result/managed-schema $solr_container_id:/bitnami/solr/server/solr/result/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/transaction/managed-schema $solr_container_id:/bitnami/solr/server/solr/transaction/conf/managed-schema.xml
docker cp ./direct_indexing/solr/cores/activity/xslt $solr_container_id:/bitnami/solr/server/solr/activity/conf/

# Ask the user if this is mounted locally, default to no. If it is, chown the files to 1001:root
read -p "Is this mounted locally? (y/N) " -n 1 -r


echo "Done!"
