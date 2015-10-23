import gensim, logging, sys
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
import os
from itertools import izip
from itertools import count

# needs to be defined


app = Flask(__name__)
CORS(app, resources=r'/*',
     allow_headers='*')

## Logger magic
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def train_docs():

    f = open('technology/technology-1.txt', 'r')
    docs = []
    for line_no,line in izip(count(),f):
        words = line.split()
        docs.append(gensim.models.doc2vec.LabeledSentence(words=words, tags=['SENT_%s' % line_no]))
    # sentence = gensim.models.doc2vec.LabeledSentence(words=f.readline(), tags=['SENT_1'])
    model = gensim.models.Doc2Vec(docs, size=100, window=8, min_count=5, workers=4)
    # tmp = model.docvecs.most_similar('SENT_1')
    # tmp1 = model.most_similar('technology')
    origin = model.docvecs['SENT_1']
    word_sims = [('technology', word, score) for word, score in model.most_similar([origin],topn=20)]
    tag_sims = [('SENT_2', tag, score) for tag, score in model.docvecs.most_similar([origin],topn=20)]
    results = sorted((tag_sims + word_sims),key=lambda tup: -tup[2])
    print results[:20]

@app.route('/check-phrases', methods=['POST'])
def check():
    phrases = request.json["phrases"]
    vector = map(checkProximity, phrases)
    transformed = map(lambda xy: {'name': xy[0], 'distance': xy[1]},
                      [val for sublist in vector for val in sublist])
    return jsonify(results = list(transformed))

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


if __name__ == "__main__":
    # if len(sys.argv) != 2:
        # print("./word-2-vec-service <training-set>")
        # sys.exit(1)
    train_docs()
    # app.config['MODEL'] = loadModel(sys.argv[1])
    app.run(host='0.0.0.0', port=9000, threaded=True)
