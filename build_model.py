from sklearn.externals import joblib
from sklearn import svm, cross_validation
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score

import scipy as sp
import numpy as np


from elastic.config import es

from text_process import term_tfidf

from pprint import pprint

index = "trec_dd_ebola_without_duplicate"
doctype = "page"

mapping = {"timestamp":"retrieved", "text":"text", "html":"html", "tag":"tag", "query":"query"}

query = {
    "query" : {
        "filtered" : {
            "filter" : {
                "exists" : { "field" : "topic_name" }
            }
        }
    },
    "fields": ["url", "topic_name"],
    #"size": 1000
    "size": 100000000
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

ebola_topics = [ "DD15-"+str(i) for i in range(49, 89)]

labels = []
ids = []
count= 0
for rec in records:
    try:
        labels.append(ebola_topics.index(rec["topic_name"][0]))
        print rec["topic_name"]
        ids.append(rec["id"])
        if len(rec["topic_name"]) > 1:
            print rec["topic_name"]
            count = count + 1
    except KeyError:
        pprint(rec)

print "total ", len(records), " docs with more than one topic ", count
del records

exit

print "Before term tfidf"

[data,_,_,features,ids_ret] = term_tfidf(ids, mapping, index, doctype, es)

print "After term tfidf"

labels_ret = [labels[ids.index(id)] for id in ids_ret]

#data_train, data_test, labels_train, labels_test = train_test_split(data, labels_ret, test_size=0.33, random_state=42)

print "Features ", len(features)

with open("linearSVC_features.txt", "w") as f:
    f.write(u"::".join(features).encode('utf-8').strip())
    
clf = svm.LinearSVC()

scores = cross_validation.cross_val_score(clf, data, labels_ret, cv=3)
print "Cross Validation Scorees ", scores

clf.fit(data, labels_ret) 

joblib.dump(clf, 'trecdd_model_linearSVC.pkl') 

# clf_linearsvc = joblib.load('trecdd_model_linearSVC.pkl')

# labels_pred = clf_linearsvc.predict(data_test)

# print confusion_matrix(labels_test, labels_pred)
# print "Accuracy Score ", accuracy_score(labels_test, labels_pred)
