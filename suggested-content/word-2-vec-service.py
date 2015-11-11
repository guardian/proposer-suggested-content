import gensim, logging, sys
import itertools
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
import json

import helpers.ngrams, helpers.tfidf

# needs to be defined


app = Flask(__name__)
CORS(app, resources=r'/*',
     allow_headers='*')

DOCS = []

## Logger magic
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def checkPhrases(phrases):
    vector = map(checkProximity, phrases)
    filtered = filter(lambda x: True if x else False, vector)
    return list(filtered)

@app.route('/document/check-phrases', methods=['POST'])
def documentCheckPhrases():
    document = request.json['document']
    grams = set(helpers.ngrams.bigrams(document))
    response = checkPhrases(grams)
    return jsonify(results = response)

@app.route('/doc', methods=['POST'])
def similarDocs():
    doc = request.json["doc"]   
    DOCS.append(gensim.models.doc2vec.LabeledSentence(words=doc.split(), tags=['current_doc']))    
    model = gensim.models.Doc2Vec(DOCS, size=100, window=8, min_count=5, workers=4)
    similar_docs = model.docvecs.most_similar('current_doc')
    return jsonify(similar_docs)


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

def loadDocuments(filename):
    f = open(filename, 'r')
    logging.info("processing the document file")
    tmp = []
    d = {}
    i = 0
    while i < 4:
        for line in f:
            print line
            i = i + 1    
            lines.append(line)
    # for line1,line2 in itertools.izip_longest(*[f]*2):
        # DOCS.append(gensim.models.doc2vec.LabeledSentence(words=line2.split(), tags=[line1]))
    logging.info("finished processing document file")

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
    if len(sys.argv) < 2:
        print("./word-2-vec-service <training-set> <document-set>")
        sys.exit(1)

    app.config['MODEL'] = loadModel(sys.argv[1])
    if sys.argv[2]:
        logging.info('document set')
        app.config['DOCS'] = loadDocuments(sys.argv[2])
    app.run(host='0.0.0.0', port=9000, threaded=True)
