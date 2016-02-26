from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Search, Q


class ES:
    def __init__(self, index, es_type, host, port):
        if not index or not es_type:
            print 'Init error - you need to provide index and type'
            exit(1)
        if not host:
            self.host = 'localhost'
        else:
            self.host = host
        if not port:
            self.port = '9200'
        else:
            self.port = port
        self.index = index
        self.type = es_type
        self.client = self.connect()

    def connect(self):
        if not self.index or not self.type:
            print 'Connection error - You need to provide index and type'
            exit(1)
        try:
            client = Elasticsearch(host=self.host, port=self.port)
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

    def index_replay(self, document, replay_id):
        # TODO: replays should have their own type, index per replay?
        # TODO: does the python API differentiate betwen transport and node client?
        # TODO: do we want to do bulk indexing of a queue of indexing actions?
        self.client.create(index=self.index, doc_type=self.type, id=replay_id, body={
            document
        })

    # Bulk indexing of replays received from a message queue
    # Actions look like:
    #  action = {
    #     "_index": "index",
    #     "_type": "type",
    #     "_id": id,
    #     "_source": {
    #         "field":"value",
    #         }
    #  }
    def bulk_index_replays(self, actions):
        helpers.bulk(self.client, actions)


def check_replay(self, replay_id):
    # TODO: matches should have their own type, index per replay?
    if self.client.indices.exists(index=self.index, type=self.type, id=replay_id):
        return self.client.get(index=self.index, type=self.type, id=replay_id)
    else:
        return None


def check_player(self, player_id):
    # TODO: players should have their own index, (not each), what about types and cluster?
    if self.client.indices.exists(index=self.index, type=self.type, id=player_id):
        return self.client.get(index=self.index, type=self.type, id=player_id)
    else:
        return None
