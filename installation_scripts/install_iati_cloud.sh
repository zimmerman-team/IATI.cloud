# Install dependencies
sudo bash install_dependencies.sh

# Set up requirements
cd ../OIPA
touch .env
echo "OIPA_DB_NAME=oipa
OIPA_DB_USER=oipa
OIPA_DB_PASSWORD=oipa
DJANGO_SETTINGS_MODULE=OIPA.development_settings" >> .env

cd OIPA
touch local_settings.py
echo "SOLR = {
  'indexing': True,
  'url': 'http://localhost:8983/solr',
  'cores': {
       'activity': 'activity',
       'budget': 'budget',
       'dataset': 'dataset',
       'organisation': 'organisation',
       'publisher': 'publisher',
       'result': 'result',
       'transaction': 'transaction',
  }
}
DOWNLOAD_DATASETS = False

# Update the local solr connections:
SOLR_URL = http://localhost:8983/solr
SOLR_PUBLISHER = f'{SOLR_URL}/publisher'
SOLR_PUBLISHER_URL = f'{SOLR_PUBLISHER}/update'
SOLR_DATASET = f'{SOLR_URL}/dataset'
SOLR_DATASET_URL = f'{SOLR_DATASET}/update'
SOLR_ACTIVITY = f'{SOLR_URL}/activity'
SOLR_ACTIVITY_URL = f'{SOLR_ACTIVITY}/update'
SOLR_TRANSACTION = f'{SOLR_URL}/transaction'
SOLR_TRANSACTION_URL = f'{SOLR_TRANSACTION}/update'
SOLR_BUDGET = f'{SOLR_URL}/budget'
SOLR_BUDGET_URL = f'{SOLR_BUDGET}/update'
SOLR_RESULT = f'{SOLR_URL}/result'
SOLR_RESULT_URL = f'{SOLR_RESULT}/update'
SOLR_ORGANISATION = f'{SOLR_URL}/organisation'
SOLR_ORGANISATION_URL = f'{SOLR_ORGANISATION}/update'

# Validator
VALIDATOR_API_KEY = '<replace with IATI Validator api key>'

# Specify if we want to download new metadata and datasets. only use for local development
FRESH = True

# Mongo connection string
MONGO_CONNECTION_STRING = localhost:27017
" >> local_settings.py
cd ..

source env/bin/activate
python manage.py migrate

echo "ACTION! Please create a django administrator user with a username and a password."
python manage.py createsuperuser
echo "Continuing installation..."

cd ../installation_scripts
