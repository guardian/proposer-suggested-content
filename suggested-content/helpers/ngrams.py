def bigrams(string):
    grams = list_to_ngrams(string.split(" "), 2)
    return map(lambda x: x[0] + '_' + x[1], grams)

def list_to_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])
