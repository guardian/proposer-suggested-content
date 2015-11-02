from sklearn.feature_extraction.text import TfidfVectorizer

def frequencies(corpus):
    vectorizer = TfidfVectorizer(min_df=1)
    X = vectorizer.fit_transform(corpus)
    idf = vectorizer.idf_
    return dict(zip(vectorizer.get_feature_names(), idf))


def filter_fun(freqs, item):
    try:
        return freqs[item[0]] > 2.5
    except KeyError:
        return False

def filter_low_frequency_bigrams(corpus, bigrams):
    freqs = frequencies(corpus)
    print(freqs)
    return filter(lambda x: filter_fun(freqs, x), bigrams)
