from sklearn.feature_extraction.text import TfidfVectorizer

def frequencies(corpus):
    vectorizer = TfidfVectorizer(min_df=1)
    X = vectorizer.fit_transform(corpus)
    idf = vectorizer.idf_
    return dict(zip(vectorizer.get_feature_names(), idf))

def filter_low_frequency_bigrams(corpus, bigrams):
    freqs = frequencies(corpus)
    return filter(lambda x: freqs[x[0]] > 1.4, bigrams)
