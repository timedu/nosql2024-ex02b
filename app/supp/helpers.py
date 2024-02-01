
import yaml # pyright: ignore
from neo4j.exceptions import CypherSyntaxError, ClientError # pyright: ignore
from prettytable import PrettyTable # pyright: ignore
from os import path
from supp.config import todo

_QRY_TITLES = {
    'qa_1': '(QA.1) How long is the shortest paths from "Kevin Bacon" to "Meg Ryan"?',
    'qa_2': '(QA.2) How many shortest paths are there from "Kevin Bacon" to "Meg Ryan"?',
    'qa_3': '(QA.3) What is one of the shortest paths from "Kevin Bacon" to "Meg Ryan"?',
    'qa_4': '(QA.4) What are the distinct shortest paths from "Kevin Bacon" to "Meg Ryan"?',

    'qb_1': '(QB.1) Create a native projection of Person and Movie nodes and ACTED_IN and DIRECTED relationships.',
    'qb_2': '(QB.2) How long is the shortest paths from "Kevin Bacon" to "Meg Ryan" (use "dijkstra")?',
    'qb_3': '(QB.3) What is one of the shortest paths from "Kevin Bacon" to "Meg Ryan" (use "dijkstra")?',
    'qb_4': '(QB.4) What is one of the shortest paths from "Kevin Bacon" to "Meg Ryan" (use "yens")?',
    'qb_5': '(QB.5) What are the seven shortest paths from "Kevin Bacon" to "Meg Ryan" (use "yens")?',
    'qb_6': '(QB.6) Remove the "person-movie" projection.',

    'qc_1': '(QC.1) Create a cypher projection ... ',
    'qc_2': '(QC.2) Determine the actors\' unweighted degree of centrality.',
    'qc_3': '(QC.3) Determine the actors\' weighted degree of centrality.',
    'qc_4': '(QC.4) Mutate the weighted degree of centrality to the nodes of the projection.',
    'qc_5': '(QC.5) Remove the mutated property.',
    'qc_6': '(QC.6) Detemine the Lovain communities of actors.',
    'qc_7': '(QC.7) Write the community IDs into the graph (not into projection).',
    'qc_8': '(QC.8) Remove the "person-acted-with" projection.'
}

_FB_QRY = {
    'qb_1': '''
        CALL gds.graph.list("person-movie") 
        YIELD graphName, schema 
        RETURN graphName, schema.nodes, schema.relationships
    ''',
    'qc_1': '''
        CALL gds.graph.list("person-acted-with") 
        YIELD graphName, schema 
        RETURN graphName, schema.nodes, schema.relationships
    ''',
    'qc_4': '''
        CALL gds.graph.list("person-acted-with") 
        YIELD graphName, schema 
        RETURN graphName, schema.nodes
    ''',
    'qc_7': '''
        MATCH (p:Person)-[:ACTED_IN]->(:Movie) 
        RETURN  
          p.communityId AS community, 
          count(DISTINCT p) AS memberCount,
          apoc.coll.remove(collect(DISTINCT p.name), 3, 100) AS exampleMembers
        ORDER BY community
    ''',
}


_TODOS_PATH = path.join(
    path.dirname(path.abspath(__file__)), '..', 'todos'
)


def load_queries():
    '''
    Load queries from file to dict
    '''    
    qry_path = path.join(_TODOS_PATH, todo['folder'], 'queries.yml')
    with open(qry_path, 'r') as file:
        queries_dict = yaml.safe_load(file)
    return queries_dict


def execute_query(driver, command):
    '''
    Load queries and executes one
    '''
    query = load_queries()[command]
    return driver.execute_query(query)


def print_qry_result(result, command=None, driver=None):
    '''
    Print feedback for query that returns data
    '''
    table = PrettyTable()
    table.align = 'l'
    table.field_names = result.keys
    table.add_rows ([record.values() for record in result.records ])
    
    if command: 
        qry_title = _QRY_TITLES[command]
        print(qry_title)
        print()
        print(result.summary.query)
        feedback_qry = _FB_QRY.get(command)

    print(table)
    print(f'{len(result.records)} record(s)')

    if command and feedback_qry:
        print(f'\nAfter executing {qry_title[0:6]}:')
        fb_qry_result = driver.execute_query(feedback_qry)
        print_qry_result(fb_qry_result)


def execute_all_qry(driver, command):
    '''
    Load queries and executes all that return data
    '''
    queries = load_queries()
    print()
    for qry_key, query in queries.items():
        if command[4:7] != qry_key[0:2]: continue
        try:
            result = driver.execute_query(query)
            print_qry_result(result, qry_key, driver)
        except (CypherSyntaxError, ClientError) as err:
            print(_QRY_TITLES[qry_key])
            print()
            print(err)
        except KeyError:
            print('Unkwown query:', qry_key)
        finally:
            print()
            continue


def print_crud_result(result):
    '''
    Print feedback for query not returning data
    '''
    ctr_obj = result.summary.counters
    ctr_list = [
        attr for attr in dir(ctr_obj)\
        if not callable(getattr(ctr_obj, attr))\
        and not attr.startswith("_")\
        and not attr.startswith("contains_")\
        and getattr(ctr_obj, attr) > 0
    ]
    for ctr in ctr_list: 
        print(f'- {ctr}: {getattr(ctr_obj, ctr)}')


def merge_movie_data(driver):    
    '''
    Stores movie data if not already exist; 
    expected feedback
    - labels_added: 171
    - nodes_created: 171
    - properties_set: 564
    - relationships_created: 253
    '''    
    qry_path = path.join(
        path.dirname(path.abspath(__file__)), 
        'merge_movie_data.cypher'
    )
    with open(qry_path, 'r') as file:
         query = file.read()
    result = driver.execute_query(query)
    print_crud_result(result)
