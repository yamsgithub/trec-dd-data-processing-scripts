import numpy as np
import scipy as sp

from sklearn.preprocessing import binarize
from elastic.get_mtermvectors import getTermStatistics, getTermFrequency

def preprocess(data, corpus):
    binary_data = binarize(sp.sparse.csc_matrix(data))
    check_for_zero = binary_data.sum(axis=0)
    indices = np.where(check_for_zero <= 2)[1]
    sub_data = np.delete(data, indices, 1)
    sub_corpus = np.delete(corpus, indices).tolist()
    return [sub_data, sub_corpus]

def term_tfidf(urls, mapping, index, doctype, es):
    [data, data_tf, data_ttf , corpus, urls] = getTermStatistics(urls, mapping, [], index, doctype , es)
    [cleaned_data, cleaned_corpus] = preprocess(data, corpus)
    return [cleaned_data, data_tf, data_ttf, cleaned_corpus, urls]

def term_tf(urls, mapping, index, doctype, es):
    [data, corpus, urls] = getTermFrequency(urls, mapping, index, doctype , es)
    [cleaned_data, cleaned_corpus] = preprocess(data, corpus)
    return [cleaned_data, cleaned_corpus, urls]
