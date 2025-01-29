from neo4j import GraphDatabase
import pyneoinstance
# Need a Yaml file for configs of Local neo4j DB
config_path='neo4j_config.yaml'

class Neo4jKnowledgeGraph:
    def __init__(self, config_path=config_path):
        self.configs = pyneoinstance.load_yaml_file(config_path)
        self.creds = self.configs['credentials']
        self.driver = GraphDatabase.driver(self.creds['uri'],
                                           auth=(self.creds['user'],
                                                 self.creds['password']))

    def close(self):
        self.driver.close()

    def add_node(self, node_id, node_type):
        def _add_node(tx):
            query = """
            CREATE (n:Participant {ID: $node_id, type: $node_type})
            """
            tx.run(query, node_id=node_id, node_type=node_type)

        with self.driver.session() as session:
            session.write_transaction(_add_node)
    def add_attributes_to_node(self, node_id, attributes):
        def _add_attributes(tx):
            attr_str = ", ".join([f'n.{k} = "{v}"' for k, v in attributes.items()])
            query = f'MATCH (n {{ID: $node_id}}) SET {attr_str}'
            tx.run(query, node_id=node_id)

        with self.driver.session() as session:
            session.write_transaction(_add_attributes)

    def remove_node(self, node_id):
        def _remove_node(tx):
            query = f'MATCH (n {{ID: $node_id}}) DETACH DELETE n'
            tx.run(query, node_id=node_id)

        with self.driver.session() as session:
            session.write_transaction(_remove_node)

    def create_edge(self, sr_id, tr_id, eg_id):
        def _create_edge(tx):
            query = (f'MATCH (a {{ID: $sr_id}}), (b {{ID: $tr_id}}) '
                     f'CREATE (a)-[r:RELATION {{ID: $eg_id}}]->(b)')
            tx.run(query, sr_id=sr_id, tr_id=tr_id, eg_id=eg_id)

        with self.driver.session() as session:
            session.write_transaction(_create_edge)

    def set_edge_attribute(self, eg_id, attributes):
        def _set_edge_attribute(tx):
            attr_str = ", ".join([f'r.{k} = "{v}"' for k, v in attributes.items()])
            query = f'MATCH ()-[r {{ID: $eg_id}}]->() SET {attr_str}'
            tx.run(query, eg_id=eg_id)

        with self.driver.session() as session:
            session.write_transaction(_set_edge_attribute)

    def remove_edge(self, eg_id):
        def _remove_edge(tx):
            query = f'MATCH ()-[r {{ID: $eg_id}}]->() DELETE r'
            tx.run(query, eg_id=eg_id)

        with self.driver.session() as session:
            session.write_transaction(_remove_edge)