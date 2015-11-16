import gensim, logging, sys
import itertools
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
import json
import re
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
    model = gensim.models.doc2vec.Doc2Vec.load('docs_tmp.bin')
    doc = request.json["doc"] 
    new_doc_vec = model.infer_vector(doc.split())
    similar_docs = model.docvecs.most_similar([new_doc_vec])
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
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    lines = []
    d = {}
    for line in f.xreadlines():
        if re.match(url_regex,line):
            d['url'] = line.strip()
        elif not line.isspace():
            d['doc'] = line
            lines.append(d)
             
            d = {}      
    f.close()  
    logging.info("finished processing document file")
    processLines(lines)      

def processLines(lines):
    logging.info("processing the docs")
    i = 0
    ls = lines[:len(lines)/4]
    for l in ls:
        url = l.get('url', None)
        doc = l.get('doc', None)
        if url and doc:
            # print "i is %s" %i
            doc = gensim.models.doc2vec.LabeledSentence(words=doc.split(), tags=[url])
            DOCS.append(doc)
        i = i + 1  
    model = gensim.models.Doc2Vec(DOCS, size=100, window=8, min_count=5, workers=4)      
    model.save('docs_tmp.bin')
    logging.info("finished processing the docs")        

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

    # app.config['MODEL'] = loadModel(sys.argv[1])
    if sys.argv[2]:
        logging.info('document set')
        app.config['DOCS'] = loadDocuments(sys.argv[2])
    app.run(host='0.0.0.0', port=9000, threaded=True)
