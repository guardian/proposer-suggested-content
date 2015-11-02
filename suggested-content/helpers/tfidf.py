from sklearn.feature_extraction.text import TfidfVectorizer

def frequencies(corpus):
    vectorizer = TfidfVectorizer(lowercase=True, min_df=1, ngram_range=(2, 2), stop_words='english')
    X = vectorizer.fit_transform(corpus)
    idf = vectorizer.idf_
    return dict(zip(vectorizer.get_feature_names(), idf))


def filter_fun(freqs, item):
    try:
        return freqs[" ".join(item)] < 2.7
    except KeyError:
        return False

def filter_low_frequency_bigrams(corpus, bigrams):
    freqs = frequencies(corpus)
    return filter(lambda x: filter_fun(freqs, x), bigrams)
