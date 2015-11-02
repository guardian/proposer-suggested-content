import helpers

def bigrams(corpus):
    lowered = list(map(lambda x: x.lower(), corpus))
    grams = list_to_ngrams(" ".join(lowered).split(" "), 2)
    #filtered = helpers.tfidf.filter_low_frequency_bigrams(lowered, grams)
    return map(lambda x: x[0] + '_' + x[1], grams)

def list_to_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])
