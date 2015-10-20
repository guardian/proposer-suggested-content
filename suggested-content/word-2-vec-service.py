import gensim, logging, sys, os.path
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
import boto
from boto.s3.connection import S3Connection

# needs to be defined


app = Flask(__name__)
app.config.from_object('config')
CORS(app, resources=r'/*',
     allow_headers='*')

## Logger magic
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


@app.route('/check-phrases', methods=['POST'])
def check():
    phrases = request.json["phrases"]
    vector = map(checkProximity, phrases)
    transformed = map(lambda xy: {'name': xy[0], 'distance': xy[1]},
                      [val for sublist in vector for val in sublist])
    return jsonify(results = list(transformed))


@app.route('/query', methods=['GET'])
def query():
    searchword = request.args.get('word', '')
    notwords = request.args.get('not', '')
    vector = checkProximity(searchword, notwords)
    return jsonify(vector)

def loadModel(binary_name):
    if os.path.isfile(binary_name):
        logging.info("Loading binary file from local filesystem...")
        return gensim.models.Word2Vec.load_word2vec_format(binary_name, binary=True)
    else:
        logging.info("Loading binary file from S3...")
        path = read_from_s3()
        # get it from S3
        return gensim.models.Word2Vec.load_word2vec_format(path, binary=True)

def checkProximity(phrase, notwords = None):
    __MODEL__ = app.config['MODEL']
    if not notwords:
        try:
            result = __MODEL__.most_similar(positive=phrase)
            return result
        except KeyError:
            logging.warn("No matches found for: %s", phrase)
            return []
    else:
        try:
            result = __MODEL__.most_similar(positive=phrase.split(),negative=notwords.split())
            return result
        except KeyError:
            logging.warn("No matches found for: %s", phrase)
            return []

def read_from_s3():
    conn = S3Connection()
    b = conn.get_bucket('proposer-capi-snapshots')
    logging.info('found bucket')
    key = b.get_key('2015-10-15T10:44:08+00:00/capi-phrases.bin')
    logging.info('persisting file name')
    key.get_contents_to_filename('capi-phrases.bin')
    return 'capi-phrases.bin'


if __name__ == "__main__":
    app.config['MODEL'] = loadModel(app.config['TRAINING_SET_BINARY'])
    app.run()
