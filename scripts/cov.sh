pytest --cov=direct_indexing --cov-report html:./coverage_report tests

echo $(pwd)/coverage_report/index.html
