# Proposer Suggested Content

Get related content recommendations from Proposer, inside Composer


## About
In the suggested-content directory is a Python file that will run a
server at https:://localhost:5000 which will accept terms and phrases
and find related terms.


The service is written in Python. This is because the
[gensim](https://radimrehurek.com/gensim) library is far more
sophisticated than the equivalent in Scala or Java.

### Dependencies
You will need nginx installed and running as well as
[dev-nginx](https://github.com/guardian/dev-nginx) to setup the
correct domain for the tool.

All scripts are written using Python 3 so this is a hard
dependency. You will also need [pip](https://pypi.python.org/pypi/pip) installed in order to fetch dependencies.

It's highly recommended you use a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs) when
using the service as this will save you a lot of pain. I'd also
recommend using the
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest)
as this will make your life even easier.

### Setup
The instructions below assume you are using both virtualenv and
virtualenvwrapper.

1. Clone the repository.
2. ```cd``` into the cloned repo.
3. Setup the nginx mappings, using
   [dev-nginx](https://github.com/guardian/dev-nginx) and the
   mapping.yaml defined in the nginx directory.
3. Create a virtual environment with ```mkvirtualenv <name-of-virtualenv> --python=<path-to-python3>```
4. ```pip install -r requirements.txt```
5. Now run the ```word-2-vec-service.py``` and the service will be at https://suggested-content.local.dev-gutools.co.uk
6. You will need to the pass the service a trained binary file which
   you can find in the Composer's S3 or make yourself using the
   [word2vec](https://code.google.com/p/word2vec/) service.
