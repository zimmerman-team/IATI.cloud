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

cp ./direct_indexing/solr/cores/activity/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/activity/conf/managed-schema.xml
cp ./direct_indexing/solr/cores/budget/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/budget/conf/managed-schema.xml
cp ./direct_indexing/solr/cores/dataset/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/dataset/conf/managed-schema.xml
cp ./direct_indexing/solr/cores/organisation/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/organisation/conf/managed-schema.xml
cp ./direct_indexing/solr/cores/publisher/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/publisher/conf/managed-schema.xml
cp ./direct_indexing/solr/cores/result/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/result/conf/managed-schema.xml
cp ./direct_indexing/solr/cores/transaction/managed-schema ./direct_indexing/solr_mount_dir/solr/server/solr/transaction/conf/managed-schema.xml
cp -r ./direct_indexing/solr/cores/activity/xslt ./direct_indexing/solr_mount_dir/solr/server/solr/activity/conf/
chown 1001 ./direct_indexing/solr_mount_dir/*

echo "Done!"
