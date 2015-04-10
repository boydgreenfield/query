set -e

source venv/bin/activate
nosetests
echo "Tests successful. Pushing to PyPI..."
python setup.py sdist upload
