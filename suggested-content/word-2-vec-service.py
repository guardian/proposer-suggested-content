import gensim, logging, sys, itertools, argparse, json, re
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
import helpers.ngrams, helpers.tfidf


# needs to be defined

# set up the command line args
parser = argparse.ArgumentParser(description="Run word2vec and doc2vec in an HTTP service")
parser.add_argument('word2vec', type=str,
                    help="A pretrained word2vec binary file")
parser.add_argument('--doc2vec', type=str, required=False, dest="doc2vec",
                    help="Passing in document")
parser.add_argument('--doctrain', type=str, required=False, dest="doctrain",
                    help="Trains docs in the text format to doc to vec")


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
    model = app.config["DOCS"]
    new_doc_vec = model.infer_vector(doc.split())
    similar_docs = model.docvecs.most_similar([new_doc_vec])
    return jsonify(results = [item[0] for item in similar_docs])


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

def loadDocsBinary(filename):
    model = gensim.models.doc2vec.Doc2Vec.load(filename)
    return model

def loadDocuments(filename):
    f = open(filename, 'r')
    logging.info("processing the document file")
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    lines = []
    d = {}
    for line in f.readlines():
        if re.match(url_regex,line):
            d['url'] = line.strip()
        elif not line.isspace():
            d['doc'] = line
            lines.append(d)
            d = {}      
    f.close()  
    logging.info("finished processing document file")
    createModel(lines, filename)

def createSentences(lines):
    logging.info("processing the docs")
    for l in lines:
        url = l.get('url', None)
        doc = l.get('doc', None)

        if url and doc:
            yield gensim.models.doc2vec.LabeledSentence(words=doc.split(), tags=[url])
    
def createModel(lines, filename):
    logging.info('performing training')        
    model = gensim.models.Doc2Vec(size=100, window=8, min_count=5, workers=20)  

    model.build_vocab(createSentences(lines))
    new_doc_vec = model.infer_vector('testing')
    similar_docs = model.docvecs.most_similar([new_doc_vec])
    output = '%s.bin' %filename
    model.save(output)
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
    args = vars(parser.parse_args())
    app.config['MODEL'] = loadModel(args['word2vec'])

    if args['doc2vec']:
        logging.info('document set')
        app.config['DOCS'] = loadDocsBinary(args['doc2vec'])

    if args['doctrain']:
        logging.info('training set')

        lines = loadDocuments(args['doctrain'])
        
        


    app.run(host='0.0.0.0', port=9000, threaded=True)
