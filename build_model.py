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
    "fields": ["url", "topic_name", "text"],
    #"size": 3000
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
text = []

for rec in records:
    try:
        if text.index(rec["text"]):
            print "Duplicate text found ", rec["id"]
    except KeyError:
        pprint(rec)
    except ValueError:
        labels.append(ebola_topics.index(rec["topic_name"][0]))
        ids.append(rec["id"])
        text.append(rec["text"])
        

del records
del text

print "Total documents ", len(ids)

print "Before term tfidf"

[data,_,_,features,ids_ret] = term_tfidf(ids, mapping, index, doctype, es)

print "After term tfidf"

labels_ret = [labels[ids.index(id)] for id in ids_ret]

#data_train, data_test, labels_train, labels_test = train_test_split(data, labels_ret, test_size=0.33, random_state=42)

print "Features ", len(features)

with open("linearSVC_features_no_duplicates.txt", "w") as f:
    f.write(u"::".join(features).encode('utf-8').strip())
    
clf = svm.LinearSVC()

scores = cross_validation.cross_val_score(clf, data, labels_ret, cv=3)
print "Cross Validation Scorees ", scores

clf.fit(data, labels_ret) 

joblib.dump(clf, 'trecdd_model_linearSVC_no_duplicates.pkl') 

# clf_linearsvc = joblib.load('trecdd_model_linearSVC.pkl')

# labels_pred = clf_linearsvc.predict(data_test)

# print confusion_matrix(labels_test, labels_pred)
# print "Accuracy Score ", accuracy_score(labels_test, labels_pred)
