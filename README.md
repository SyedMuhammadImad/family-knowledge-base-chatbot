# Family knowledge-base chatbot

Completed KRR coursework with a local AIML/Pytholog logic stage and a Neo4j graph stage. The repairs remove self-sibling results, correct uncle/cousin inference, reject parent cycles and invalid facts, preserve unsaved facts on storage failure, and implement every graph query exposed by the AIML patterns. Repeated coursework copies use the same repaired implementations.

Install `requirements.txt`. Run `python family_agent.py` for the logic console or `python app.py` for its local Flask interface. Facts are saved in `sample_data/family_kb.pl`; the published file contains no personal facts. The notebook demonstrates temporary synthetic facts. Run `pytest -q` for the logic tests.

The graph stage is `ass3/files/family_agent.py` (or its Flask app). Set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and optionally `NEO4J_DATABASE` in your environment. The graph imports without contacting the database; credentials are never hardcoded. Use a dedicated local database. Clear removes only `FamilyPerson` nodes. Logic and graph stores are separate coursework stages.

`VERIFICATION.json` records eight logic/UI regression tests and real integration checks against an isolated Neo4j 5.26.14 instance, including all 30 relationship/property handlers, natural-language yes/no queries, duplicate relationships, cycle rejection and preservation of unrelated nodes. The temporary test server was stopped afterward.

Academic, local, single-user application. No hosted service or concurrent multi-user transaction guarantee is claimed. Credentials, personal facts, database files, pictures and videos are excluded. Historical class notes and reports retain their attribution; tested behavior is documented here.
