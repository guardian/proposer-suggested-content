import gensim, logging, sys
from flask import Flask, request, jsonify
from flask.ext.cors import CORS

# needs to be defined


app = Flask(__name__)
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

    return jsonify(results = transformed)


@app.route('/query', methods=['GET'])
def query():
    searchword = request.args.get('word', '')
    notwords = request.args.get('not', '')
    vector = checkProximity(searchword, notwords)
    return jsonify(vector)

def loadModel(filename):
    return gensim.models.Word2Vec.load_word2vec_format(filename, binary=True)

def checkProximity(phrase, notwords = None):
    __MODEL__ = app.config['MODEL']
    if not notwords:
        try:
            result = __MODEL__.most_similar(positive=phrase)
            return result
        except KeyError:
            logging.warn("No matches found for: %s", extra=phrase)
            return []
    else:
        try:
            result = __MODEL__.most_similar(positive=phrase.split(),negative=notwords.split())
            return result
        except KeyError:
            logging.warn("No matches found for: %s", extra=phrase)
            return []


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("./word-2-vec-service <training-set>")
        sys.exit(1)

    app.config['MODEL'] = loadModel(sys.argv[1])
    app.run()
