"""AIML family chatbot with parameterized Neo4j traversals; local credentials via environment."""
import os, re, time
from datetime import date
from pathlib import Path
import aiml
from neo4j import GraphDatabase
if not hasattr(time, 'clock'): time.clock=time.perf_counter
DATA_DIR=Path(__file__).parent/'sample data'
if not DATA_DIR.exists(): DATA_DIR=Path(__file__).parent/'sample_data'
class Neo4jConnection:
    def __init__(self, uri, auth): self.driver=GraphDatabase.driver(uri, auth=auth)
    def close(self): self.driver.close()
    def query(self, query, parameters=None):
        with self.driver.session(database=os.environ.get('NEO4J_DATABASE','neo4j')) as session:
            return [dict(r) for r in session.run(query,parameters or {})]
db=None
def get_db():
    global db
    if db is None:
        password=os.environ.get('NEO4J_PASSWORD','')
        if not password: raise RuntimeError('Set NEO4J_PASSWORD before using the graph stage')
        db=Neo4jConnection(os.environ.get('NEO4J_URI','bolt://127.0.0.1:7687'),(os.environ.get('NEO4J_USER','neo4j'),password))
    return db
def atom(value):
    result=re.sub(r'[^a-z0-9_]+','_',str(value).lower()).strip('_')
    if not re.fullmatch(r'[a-z][a-z0-9_]*',result): raise ValueError('Use a non-empty person or property name')
    return result
def clean(value):
    if not isinstance(value,str) or not value.strip() or len(value)>2000: raise ValueError('Enter a message of 1–2000 characters')
    return re.sub(r'[?!.,]','',value).upper().strip()
def add_fact(kind,first,second=''):
    if kind not in {'male','female','parent','married','dob','city','profession'}: raise ValueError('Unknown fact type')
    a=atom(first)
    b=str(second).strip() if kind=='dob' else atom(second) if second else ''
    if kind not in {'male','female'} and not b: raise ValueError('Missing fact value')
    if kind in {'parent','married'} and a==b: raise ValueError('Self relationships are invalid')
    if kind=='dob' and (not b.isdigit() or not 1900<=int(b)<=date.today().year): raise ValueError('Invalid birth year')
    if kind=='parent':
        if get_db().query('MATCH (c:FamilyPerson {name:$b})-[:PARENT_OF*1..]->(p:FamilyPerson {name:$a}) RETURN p.name AS res',{'a':a,'b':b}): raise ValueError('Parent cycles are invalid')
        q='MERGE (a:FamilyPerson {name:$a}) MERGE (b:FamilyPerson {name:$b}) MERGE (a)-[:PARENT_OF]->(b)'
    elif kind=='married': q='MERGE (a:FamilyPerson {name:$a}) MERGE (b:FamilyPerson {name:$b}) MERGE (a)-[:MARRIED_TO]->(b) MERGE (b)-[:MARRIED_TO]->(a)'
    elif kind in {'male','female'}: q='MERGE (a:FamilyPerson {name:$a}) SET a.gender=$b';b=kind
    else: q='MERGE (a:FamilyPerson {name:$a}) SET a.'+kind+'=$b'
    get_db().query(q,{'a':a,'b':b})
    return 'Fact saved in Neo4j.'
def lookup(relation,person):
    name=atom(person)
    base='MATCH (p:FamilyPerson {name:$name})'
    parent=base+'<-[:PARENT_OF]-(r:FamilyPerson)'
    grand=base+'<-[:PARENT_OF]-(:FamilyPerson)<-[:PARENT_OF]-(r:FamilyPerson)'
    sibling=base+'<-[:PARENT_OF]-(:FamilyPerson)-[:PARENT_OF]->(r:FamilyPerson)'
    queries={
      'father':parent+" WHERE r.gender='male'",'mother':parent+" WHERE r.gender='female'",
      'grandparent':grand,'grandfather':grand+" WHERE r.gender='male'",'grandmother':grand+" WHERE r.gender='female'",
      'sibling':sibling+' WHERE r<>p','brother':sibling+" WHERE r<>p AND r.gender='male'",'sister':sibling+" WHERE r<>p AND r.gender='female'",
      'child':base+'-[:PARENT_OF]->(r:FamilyPerson)','son':base+"-[:PARENT_OF]->(r:FamilyPerson) WHERE r.gender='male'",'daughter':base+"-[:PARENT_OF]->(r:FamilyPerson) WHERE r.gender='female'",
      'spouse':base+'-[:MARRIED_TO]->(r:FamilyPerson)',
      'ancestor':base+'<-[:PARENT_OF*1..]-(r:FamilyPerson)',
      'cousin':base+'<-[:PARENT_OF]-(a:FamilyPerson)<-[:PARENT_OF]-(:FamilyPerson)-[:PARENT_OF]->(b:FamilyPerson)-[:PARENT_OF]->(r:FamilyPerson) WHERE a<>b AND r<>p',
      'same_city':base+', (r:FamilyPerson) WHERE r<>p AND r.city=p.city',
      'recommend_meetup':base+', (r:FamilyPerson) WHERE r<>p AND r.city=p.city AND NOT (p)-[:PARENT_OF]-(r) AND NOT (p)-[:MARRIED_TO]-(r)',
    }
    for label,gender in [('uncle','male'),('aunt','female')]:
        queries[label]=base+"<-[:PARENT_OF]-(a:FamilyPerson)<-[:PARENT_OF]-(:FamilyPerson)-[:PARENT_OF]->(r:FamilyPerson) WHERE r<>a AND r<>p AND r.gender='"+gender+"'"
    for label,gender in [('father_in_law','male'),('mother_in_law','female')]:
        queries[label]=base+"-[:MARRIED_TO]->(:FamilyPerson)<-[:PARENT_OF]-(r:FamilyPerson) WHERE r.gender='"+gender+"'"
    for label,gender in [('brother_in_law','male'),('sister_in_law','female')]:
        queries[label]=base+"-[:MARRIED_TO]->(s:FamilyPerson)<-[:PARENT_OF]-(:FamilyPerson)-[:PARENT_OF]->(r:FamilyPerson) WHERE r<>s AND r<>p AND r.gender='"+gender+"'"
    if relation in queries:
        return [r['res'] for r in get_db().query(queries[relation]+' RETURN DISTINCT r.name AS res ORDER BY res',{'name':name})]
    if relation in {'city','profession','dob','age'}:
        prop='dob' if relation=='age' else relation
        rows=get_db().query(base+' RETURN p.'+prop+' AS res',{'name':name})
        values=[r['res'] for r in rows if r['res'] is not None]
        return [date.today().year-int(x) for x in values] if relation=='age' else values
    if relation in {'male','female'}: return [r['res'] for r in get_db().query("MATCH (r:FamilyPerson) WHERE r.gender=$gender RETURN r.name AS res ORDER BY res",{'gender':relation})]
    if relation=='married': return [r['res'] for r in get_db().query('MATCH (a:FamilyPerson)-[:MARRIED_TO]->(b:FamilyPerson) WHERE a.name<b.name RETURN a.name+" and "+b.name AS res ORDER BY res')]
    if relation=='family_hub': return [r['res'] for r in get_db().query('MATCH (p:FamilyPerson) WHERE p.city IS NOT NULL RETURN p.city AS res,count(p) AS residents ORDER BY residents DESC,res LIMIT 1')]
    raise ValueError('Unsupported relationship')
class InputAgent:
    def __init__(self):
        self.kernel=aiml.Kernel();self.kernel.learn(str(DATA_DIR/'family_input.aiml'))
    def ask(self,text):
        response=self.kernel.respond(clean(text)).strip();parts=response.split(':')
        if parts[0]=='ADDFACT': return add_fact(parts[1].lower(),parts[2],parts[3] if len(parts)>3 else '')
        if parts[0]=='CONTROL':
            if parts[1].lower()=='clear': get_db().query('MATCH (p:FamilyPerson) DETACH DELETE p');return 'Family graph cleared; other nodes preserved.'
            return 'Facts are saved immediately in Neo4j.'
        return response
class QueryAgent:
    def __init__(self):
        self.kernel=aiml.Kernel();self.kernel.learn(str(DATA_DIR/'family_chat.aiml'))
    def ask(self,text):
        response=self.kernel.respond(clean(text)).strip();parts=response.split(':')
        if parts[0]=='QUERY':
            values=lookup(parts[1].lower(),parts[2]);return ', '.join(str(x).replace('_',' ').capitalize() for x in values) if values else 'No matching facts found.'
        if parts[0]=='YESNO':
            rel=parts[1].lower();first=atom(parts[2]);second=atom(parts[3]) if len(parts)>3 else None
            if rel=='is_married': result=bool(lookup('spouse',first))
            elif rel=='older_than':
                a,b=lookup('dob',first),lookup('dob',second);result=bool(a and b and int(a[0])<int(b[0]))
            else: result=first in lookup('spouse' if rel=='married' else rel,second)
            return 'Yes, according to the stored facts.' if result else 'No matching fact is recorded.'
        return response
class FamilyKnowledgeAgent:
    def __init__(self): self.input_agent=InputAgent();self.query_agent=QueryAgent()
    def ask_input(self,text):return self.input_agent.ask(text)
    def ask(self,text):return self.query_agent.ask(text)
    def reload(self):return 'Graph facts are queried directly.'
def run_console_chat():
    agent=FamilyKnowledgeAgent()
    for prompt,handler in [('Add facts',agent.ask_input),('Ask questions',agent.ask)]:
        print(prompt+'; type done to leave this mode')
        while True:
            try: value=input('You: ')
            except (EOFError,KeyboardInterrupt):return
            if value.lower() in {'done','exit','quit'}:break
            try:print(handler(value))
            except ValueError as error:print(error)
if __name__=='__main__':run_console_chat()
