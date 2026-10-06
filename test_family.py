"""Use temporary knowledge bases only; never edit the bundled or original facts."""
import importlib
from pathlib import Path
import pytest
import family_agent as family

@pytest.fixture
def kb(tmp_path,monkeypatch):
    path=tmp_path/'family_kb.pl'
    path.write_text('% DYNAMIC FACTS SECTION\n',encoding='utf-8')
    monkeypatch.setattr(family,'KB_FILE',path)
    return path

def seed(*facts):
    for fact in facts: family.write_fact_to_kb(fact)

def test_parent_grandparent_and_unknown(kb):
    seed('male(alex).','male(bob).','female(cara).','parent(alex, bob).','parent(bob, cara).')
    query=family.QueryAgent()
    assert family._names(query.query('father(X,cara)'))==['Bob']
    assert family._names(query.query('grandparent(X,cara)'))==['Alex']
    assert query.query('father(unknown,cara)')==[]

def test_siblings_do_not_include_self(kb):
    seed('male(bob).','male(dan).','parent(alex, bob).','parent(alex, dan).')
    query=family.QueryAgent()
    assert family._names(query.query('brother(X,bob)'))==['Dan']
    assert not query.query('sibling(bob,bob)')

def test_cousin_and_uncle_exclude_parent(kb):
    seed('male(bob).','male(dan).','parent(alex,bob).','parent(alex,dan).','parent(bob,cara).','parent(dan,erin).')
    query=family.QueryAgent()
    assert family._names(query.query('uncle(X,cara)'))==['Dan']
    assert family._names(query.query('cousin(X,cara)'))==['Erin']

def test_duplicate_and_invalid_facts(kb):
    assert family.write_fact_to_kb('male(bob).')
    assert not family.write_fact_to_kb('male(bob).')
    for bad in ['parent(bob,bob).','married(bob,bob).','dob(bob,9999).','system(remove_all).']:
        with pytest.raises(ValueError):family.write_fact_to_kb(bad)

def test_parent_cycles_rejected(kb):
    seed('parent(alex,bob).','parent(bob,cara).')
    with pytest.raises(ValueError):family.write_fact_to_kb('parent(cara,alex).')

def test_input_save_reload_and_clear(kb):
    agent=family.FamilyKnowledgeAgent()
    assert 'Fact ready' in agent.ask_input('Bob is male')
    assert 'Fact ready' in agent.ask_input('Bob is parent of Cara')
    assert 'Saved 2' in agent.ask_input('Save facts')
    assert 'Bob' in agent.ask('Who is father of Cara')
    assert 'cleared' in agent.ask_input('Clear facts')
    assert 'Bob' not in agent.ask('Who is father of Cara')

def test_failed_save_retains_pending(kb,monkeypatch):
    agent=family.InputAgent();agent._pending=['male(bob).']
    def fail(_):raise OSError('test storage failure')
    monkeypatch.setattr(family,'write_fact_to_kb',fail)
    assert agent._save_all().startswith('Save failed')
    assert agent._pending==['male(bob).']

def test_local_web_routes(kb):
    web=importlib.import_module('app')
    with web.app.test_client() as client:
        assert client.get('/').status_code==200
        assert client.post('/add',json=[]).status_code==400
        assert client.post('/ask',json={'message':['bad']}).status_code==200
        assert client.post('/add',json={'message':'Bob is male'}).status_code==200
        assert client.post('/add',json={'message':'Save facts'}).status_code==200
        assert client.post('/reload').status_code==200
