echo "Ensure this is run from the IATI.cloud root directory."
echo "Current directory:"
pwd
read -p "Continue? [Y/n] " response
response=${response:-Y}
if [[ "$response" =~ ^[Nn]$ ]]; then
  exit 1
fi

cd ./direct_indexing/data_sources/datasets/iati-data-main/data/fcdo
wget http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-1.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-2.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-3.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-4.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-5.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-6.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-7.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-8.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-9.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-10.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-11.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-12.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-13.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-14.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-15.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-16.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-17.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-18.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-19.xml http://iati.fcdo.gov.uk/iati_files/solr/FCDO-set-20.xml 

rm fcdo-set-1.xml fcdo-set-2.xml fcdo-set-3.xml fcdo-set-4.xml fcdo-set-5.xml fcdo-set-6.xml fcdo-set-7.xml fcdo-set-8.xml fcdo-set-9.xml fcdo-set-10.xml fcdo-set-11.xml fcdo-set-12.xml fcdo-set-13.xml fcdo-set-14.xml fcdo-set-15.xml fcdo-set-16.xml fcdo-set-17.xml fcdo-set-18.xml fcdo-set-19.xml fcdo-set-20.xml

mv FCDO-set-1.xml fcdo-set-1.xml
mv FCDO-set-2.xml fcdo-set-2.xml
mv FCDO-set-3.xml fcdo-set-3.xml
mv FCDO-set-4.xml fcdo-set-4.xml
mv FCDO-set-5.xml fcdo-set-5.xml
mv FCDO-set-6.xml fcdo-set-6.xml
mv FCDO-set-7.xml fcdo-set-7.xml
mv FCDO-set-8.xml fcdo-set-8.xml
mv FCDO-set-9.xml fcdo-set-9.xml
mv FCDO-set-10.xml fcdo-set-10.xml
mv FCDO-set-11.xml fcdo-set-11.xml
mv FCDO-set-12.xml fcdo-set-12.xml
mv FCDO-set-13.xml fcdo-set-13.xml
mv FCDO-set-14.xml fcdo-set-14.xml
mv FCDO-set-15.xml fcdo-set-15.xml
mv FCDO-set-16.xml fcdo-set-16.xml
mv FCDO-set-17.xml fcdo-set-17.xml
mv FCDO-set-18.xml fcdo-set-18.xml
mv FCDO-set-19.xml fcdo-set-19.xml
mv FCDO-set-20.xml fcdo-set-20.xml

cd ~/IATI.cloud
