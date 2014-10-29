#! /bin/bash
wget https://pypi.python.org/packages/source/p/pysqlite/pysqlite-2.6.3.tar.gz
tar xzf pysqlite-2.6.3.tar.gz
cd pysqlite-2.6.3
sed -i'' '6,6 s/^/#/' setup.cfg
python setup.py install
