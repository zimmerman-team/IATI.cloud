python-codacy-coverage
======================

Credits to Ryan for creating this! Python coverage reporter for Codacy https://www.codacy.com

.. image:: https://api.codacy.com/project/badge/grade/3a8cf06a9db94d0ab3d55e0357bc8f9d
   :target: https://www.codacy.com/app/Codacy/python-codacy-coverage
   :alt: Codacy Badge
.. image:: https://api.codacy.com/project/badge/coverage/3a8cf06a9db94d0ab3d55e0357bc8f9d
   :target: https://www.codacy.com/app/Codacy/python-codacy-coverage
   :alt: Codacy Badge
.. image:: https://circleci.com/gh/codacy/python-codacy-coverage.png?style=shield&circle-token=:circle-token
   :target: https://circleci.com/gh/codacy/python-codacy-coverage
   :alt: Build Status
.. image:: https://badge.fury.io/py/codacy-coverage.svg
   :target: https://badge.fury.io/py/codacy-coverage
   :alt: PyPI version

Setup
-----

Codacy assumes that coverage is previously configured for your project.

To generate the required coverage XML file, calculate coverage for your project as normal, by running:

``coverage xml``

Install codacy-coverage
~~~~~~~~~~~~~~~~~~~~~~~

You can install the coverage reporter by running:

``pip install codacy-coverage``

Updating Codacy
---------------

To update Codacy, you will need your project API token. You can create the token in `Project -> Settings -> Integrations -> Add Integration -> Project API`

Then set it in your terminal, replacing %Project_Token% with your own token:

``export CODACY_PROJECT_TOKEN=%Project_Token%``

**Enterprise only** (Skip this step if you are using https://www.codacy.com)

To send coverage in the enterprise version you should:

``export CODACY_API_BASE_URL=<Codacy_instance_URL>:16006``

**Upload Coverage**

Next, simply run the Codacy reporter. It will find the current commit and send all details to your project dashboard:

``python-codacy-coverage -r coverage.xml``

Note: You should keep your API token well **protected**, as it grants owner permissions to your projects.

Troubleshoot
---------------

If you are using any CI that does not have .git information, you can specify the commit with -c and the clone directory with -d. For example if you are using AppVeyor you can:

``python-codacy-coverage -c $APPVEYOR_REPO_COMMIT -d $APPVEYOR_BUILD_FOLDER -r coverage.xml``


