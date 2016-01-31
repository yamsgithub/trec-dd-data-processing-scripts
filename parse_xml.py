import xml.etree.ElementTree as ET
from sets import Set
from pprint import pprint
import json
from sys import argv

from elastic.get_documents import get_documents_by_id
from elastic.add_documents import update_document

from elasticsearch import Elasticsearch
from elasticsearch.helpers import BulkIndexError

exclude = []
es = Elasticsearch("http://localhost:9200")

index = argv[1]
print "INDEX ", index

tree = ET.parse('dynamic-domain-2015-truth-data-v5.xml')
root = tree.getroot()

doc_ids = {}

for domain in root:
    domain_name = domain.attrib['name']
    if domain_name in 'Ebola':
        for topic in domain:
            for subtopic in topic:
                if 'subtopic' in subtopic.tag:
                    for passage in subtopic:
                        doc_id = ""
                        rating = ""
                        for doc in passage:
                            if 'docno' in doc.tag:
                                doc_id = doc.text
                            if 'rating' in doc.tag:
                                rating = doc.text
                        doc_val = doc_ids.get(doc_id)
                        if doc_val is None:
                            doc_ids[doc_id] = {"topic_name": [topic.attrib['id']], "subtopic_name": [subtopic.attrib['id']+":"+rating]}
                        else:
                            topics = doc_val.get("topic_name")
                            if topics is not None:
                                if topic.attrib['id'] not in doc_ids[doc_id]["topic_name"] :
                                    doc_ids[doc_id]["topic_name"].append(topic.attrib['id'])
                                    
                            subtopics = doc_val.get("subtopic_name")
                            if subtopics is not None:
                                if subtopic.attrib['id']+":"+rating not in doc_ids[doc_id]["subtopic_name"] :
                                    doc_ids[doc_id]["subtopic_name"].append(subtopic.attrib['id']+":"+rating)
        
                if len(doc_ids) >= 10:
                    try:
                        update_document(doc_ids,  es_index=index, es_doc_type='page', es=es)
                        doc_ids = {}
                    except BulkIndexError as e:
                        print e

#unique_doc_ids = Set(doc_ids)

# json_data=open('/media/data/yamuna/Memex/data/trec-dd/ebola-web-01-2015-dump.json').read()

# json_docs = json.loads(json_data)

# ebola_data_ids = json_docs.keys()

# json_data=open('/media/data/yamuna/Memex/data/trec-dd/ebola-web-03-2015-dump.json').read()

# json_docs = json.loads(json_data)

# ebola_data_ids.extend(json_docs.keys())
# print len(ebola_data_ids)

# ebola_data_ids_set = Set(ebola_data_ids)

# print len(ebola_data_ids_set.intersection(unique_doc_ids))

