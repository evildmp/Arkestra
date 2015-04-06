# create virtual environment
.env:
	virtualenv .env

# install all needed for development
develop: .env
	.env/bin/pip install -e .[test] -r REQUIREMENTS.txt tox

# clean the development envrironment
clean:
	-rm -rf .env
