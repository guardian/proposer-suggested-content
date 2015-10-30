import gensim, logging, sys
from flask import Flask, request, jsonify
from flask.ext.cors import CORS

import helpers.ngrams

# needs to be defined


app = Flask(__name__)
CORS(app, resources=r'/*',
     allow_headers='*')

## Logger magic
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def checkPhrases(phrases):
    vector = map(checkProximity, phrases)
    filtered = filter(lambda x: True if x else False, vector)
    return list(filtered)

@app.route('/document/check-phrases', methods=['POST'])
def documentCheckPhrases():
    document = request.json['document']
    grams = helpers.ngrams.bigrams(document)
    response = checkPhrases(grams)
    return jsonify(results = response)


@app.route('/check-phrases', methods=['POST'])
def check():
    phrases = request.json["phrases"]
    logging.info('querying phrases %s', phrases)

    response = checkPhrases(phrases)
    return jsonify(results = response)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return "ok"

@app.route('/query', methods=['GET'])
def query():
    searchword = request.args.get('word', '')
    notwords = request.args.get('not', '')
    vector = checkProximity(searchword, notwords)
    return jsonify(vector)

def loadModel(filename):
    return gensim.models.Word2Vec.load_word2vec_format(filename, binary=True)

def checkProximity(phrase, notwords = None):

    def transformResult(result):
        tr = map(lambda xy: {'name': xy[0], 'distance': xy[1]}, result)
        return { phrase : list(tr)}

    __MODEL__ = app.config['MODEL']
    if not notwords:
        try:
            result = __MODEL__.most_similar(positive=phrase)
            logging.info("Matches for %s are %s", phrase, result)
            return transformResult(result)
        except KeyError:
            return {}
    else:
        try:
            result = __MODEL__.most_similar(positive=phrase.split(),negative=notwords.split())
            return transformResult(result)
        except KeyError:
            logging.warn("No matches found for: %s", phrase)
            return {}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("./word-2-vec-service <training-set>")
        sys.exit(1)

    app.config['MODEL'] = loadModel(sys.argv[1])
    app.run(host='0.0.0.0', port=9000, threaded=True)
