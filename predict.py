from sklearn.externals import joblib
from sklearn.preprocessing import binarize
import scipy
import numpy as np

import codecs

from ranking import word2vec
from elastic.config import es
from sklearn import svm
from elastic.get_mtermvectors import getTermStatistics

from text_process import term_tfidf

from pprint import pprint

index = "ebola"
doctype = "page"

mapping = {"timestamp":"retrieved", "text":"text", "html":"html", "tag":"tag", "query":"query"}

ebola_topics = [ "DD15-"+str(i) for i in range(49, 89)]

query = {
    "query" : {
        "match_all":{}
    },
    "fields": ["url"],
    "size": 100
    #"size": 100000000
}

res = es.search(body=query, 
                index=index,
                doc_type=doctype, request_timeout=600)

records = []

if res['hits']['hits']:
    hits = res['hits']['hits']
    
    for hit in hits:
        record = {}
        if not hit.get('fields') is None:
            record = hit['fields']
        record['id'] =hit['_id']
        records.append(record)

del res
del hits

ids = [rec["id"] for rec in records]

del records

print "Before term tfidf"

[data,_,_,corpus,urls] = term_tfidf(ids, mapping, index, doctype, es)

print "original data ", data.shape

features = []
f = codecs.open("linearSVC_features.txt", encoding='utf-8')
for line in f:
    features.extend(line.split("::"))

print "Number of features ", len(features)    
d = None
for f in features:
    try:
        if d is not None:
            d = np.hstack((d, data[:,corpus.index(f)].reshape(data.shape[0],1)))
        else:
            d = data[:,corpus.index(f)].reshape(data.shape[0],1)
    except ValueError:
        if d is not None:
            d = np.hstack((d, np.zeros((data.shape[0],1))))
        else:
            d = np.zeros((data.shape[0],1)) 

print "extended features data ",d.shape        

clf_from_file = joblib.load('trecdd_model_linearSVC.pkl')

topics = [ebola_topics[label] for label in clf_from_file.predict(d[0:20])]

for i in range(0,20):
    pprint(topics[i] + " " +urls[i])
