__author__ = 'Sébastien Muller'

import elasticsearch
from elasticsearch_dsl import Search, Q


class ES:
    def __init__(self, host=None, port=None, index=None, type=None):
        if not index or type:
            print 'Error - you need to provide index and type'
            exit(1)
        if not host or port:
            # Use default values for Elasticsearch if not provided
            self.host = 'localhost'
            self.port = '9200'
        self.index = index
        self.type = type
        self.client = self.connect()


def connect(self):
    if not self.index or self.type:
        print 'Error - You need to provide index and type'
        exit(1)
    try:
        client = elasticsearch.Elasticsearch()
        # Wait until we get a non-red response from Elasticsearch
        client.cluster.health(wait_for_status='yellow')
        return client
    except Exception, e:
        print 'Error while trying to establish connection to Elasticsearch: %s' % e
        exit(1)


def create_index(self):
    # If index doesn't exist, create it
    if not self.client.indices.exists(index=self.index):
        try:
            self.client.indices.create(index=self.index)
        except Exception, e:
            print e
            exit(1)


def index_replay(self, replay):
    self.client.index(index='replay_index', doc_type='replay_type', id='replay_id', body={
        # TODO: index replay as JSON/nested dictionaries
    })


def check_match(self, replay_id):
    self.client.get(index=self.index, doc_type=self.type, id=replay_id, )