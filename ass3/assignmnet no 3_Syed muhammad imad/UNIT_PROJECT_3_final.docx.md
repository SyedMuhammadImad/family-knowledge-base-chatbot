# Text-only document extract

Source document: UNIT_PROJECT_3_final.docx

Images and layout omitted. Claims below are source text, not independently verified results.



UNIT PROJECT 3

Graph-Based Knowledge Representation and Reasoning Using Neo4j

Course:

Knowledge Representation & Reasoning (KRR)

Student:

Syed Muhammad Imad

Semester:

Spring 2026



1.  Introduction & System Architecture

This project modernizes a conversational rule-based system by migrating its underlying data storage from a Prolog flat-file architecture into a high-performance Neo4j Graph Database. The hybrid intelligent system utilizes a three-tier decoupled architecture designed for fluid knowledge acquisition, graph traversal, and logical inference.



Architecture Stack

Conversational Interface (AIML):  Manages natural language pattern matching. family_input.aiml handles parsing rules for knowledge acquisition, while family_chat.aiml processes conversational entity resolution for retrieval.

Middleware Processing (Python):  Serves as the logic integration framework. It instantiates the neo4j.GraphDatabase native driver connections, performs string normalization, sanitizes data inputs, and dynamically translates AIML text templates into operational Cypher transactions.

Knowledge Base & Inference Engine (Neo4j):  Acts as the unified storage and graph-reasoning cluster. Relationships are maintained natively as structural pointer pathways, bypassing expensive relational table joins. Connection is established via the Bolt protocol at bolt://127.0.0.1:7687.



2.  Graph Model Design

The knowledge base represents familial and social structures using an intentional graph schema composed of labeled nodes, directional relationships, and key-value atomic properties.



Node Labels

Entities are universally labeled as :Person.



Node Properties

name  Unique string identifier used for lookups.

gender  male or female flags used for line-of-descent checks.

city  Residential property used for geospatial hub analytics.

profession  Vocational property tracking employment data.

dob  Date of birth tracker.



Relationship Types

[:PARENT_OF]  A directed relationship going from parent to child.

[:MARRIED_TO]  A symmetric, bidirectional relationship establishing marital linkage. Both directions are merged simultaneously.



Visually Mapping the Graph Layout

Below is the live structural layout of the family network database showing active nodes, property keys, and edge labels.





3.  Logic & Reasoning Mechanism: Prolog vs. Neo4j

Transitioning from a first-order logic engine (Prolog) to a graph-based reasoning network (Neo4j) alters the computational model for inference:



Rule Execution vs. Path Traversals:  Prolog uses backward-chaining resolution over Horn clauses, stack-evaluating predicates like grandfather(G,C) :- parent(G,P), parent(P,C). Neo4j evaluates this via pattern-matching memory hops using the actual Cypher query below, optimizing execution times for deeply nested trees.



Grandfather Traversal — Cypher (actual implementation)

MATCH (g:Person)-[:PARENT_OF]->(:Person)-[:PARENT_OF]->(c:Person {name: $name})

WHERE g.gender = 'male'

RETURN DISTINCT g.name AS res





Identity Constraints:  In Prolog, preventing self-matching loops requires manual declaration tags such as A \= B. In Neo4j Cypher queries, graph traversals can filter identity loopbacks instantly using inline constraints such as WHERE s <> c, as seen in the sibling query:



Sibling Query — Cypher (actual implementation)

MATCH (c:Person {name: $name})<-[:PARENT_OF]-(p)-[:PARENT_OF]->(s:Person)

WHERE s <> c

RETURN DISTINCT s.name AS res





Advanced Graph Operations

The system implements three advanced graph operations that go beyond simple fact retrieval, demonstrating the power of native graph traversals:



1. Graph-Based Hub Detection — Identifies the city with most family members

MATCH (p:Person)

WHERE p.city IS NOT NULL

RETURN p.city AS city, count(p) AS count

ORDER BY count DESC LIMIT 1





2. Inference & Discovery — Recommends meetups between same-city non-relatives

MATCH (p1:Person {name: $name}), (p2:Person)

WHERE p1.city = p2.city AND p1 <> p2

AND NOT (p1)-[:PARENT_OF]->(p2)

AND NOT (p2)-[:PARENT_OF]->(p1)

AND NOT (p1)-[:MARRIED_TO]-(p2)

RETURN DISTINCT p2.name AS res





3. Multi-Hop Traversal — Finds brother-in-law via marriage and sibling paths

MATCH (p:Person {name: $name})-[:MARRIED_TO]->(spouse)

      -[:PARENT_OF]<-[:PARENT_OF]-(parent)-[:PARENT_OF]->(bil:Person)

WHERE bil.gender = 'male' AND bil <> spouse

RETURN DISTINCT bil.name AS res





4.  Sample Chat Logs & Demonstration

Phase 1: Natural Language Knowledge Acquisition

The interactive console takes raw user inputs, extracts parameters through conversational slots in the AIML layer, and dynamically populates node attributes or edge connections directly within the Neo4j database in real-time:



KRR Assignment 3 — Neo4j Family Knowledge Base Chatbot

========================================================

📥  MODE 1: ADD FACTS TO GRAPH

    Type 'done' to switch over to query engine evaluation mode.

You (add):  add male faraz

Bot:  Got it! Fact added to Neo4j: Faraz is marked as male.

You (add):  add male mansoor

Bot:  Got it! Fact added to Neo4j: Mansoor is marked as male.

You (add):  faraz is parent of mansoor

Bot:  Got it! Fact added to Neo4j: Faraz is the parent of Mansoor.

You (add):  add male azfar

Bot:  Got it! Fact added to Neo4j: Azfar is marked as male.

You (add):  azfar is parent of faraz

Bot:  Got it! Fact added to Neo4j: Azfar is the parent of Faraz.

You (add):  faraz lives in seikhupura

Bot:  Got it! Fact added to Neo4j: Faraz city is set to seikhupura.

You (add):  done



Phase 2: Complex Graph Traversal, Analytics & Inference

Once switched to query evaluation mode, the system successfully processes single-hop lookups, multi-hop structural traversals, graph metric aggregations, and contextual property inference engine recommendations:



🔍  MODE 2: QUERY GRAPH PATTERNS

    Type 'exit' to terminate engine orchestration run.

You (query):  who is the grandfather of mansoor

Bot:  The grandfather of Mansoor is Azfar.

You (query):  identify the main family hub city

Bot:  Graph-based metrics show that 'Seikhupura' is the primary family hub node with residents.

You (query):  recommend meetup for faraz

Bot:  Inference engine discovery: We recommend Faraz meet up with Azfar because they reside in the same city but aren't directly linked in the immediate tree branches!



5.  Conclusion

The architecture satisfies all baseline functional goals. By moving from Prolog rules to native graph paths, the system demonstrates robust relational tracking, fast structural traversals, and dynamic data indexing. This implementation validates the efficiency of using conversational graph database integrations for managing highly relational data.











UNIT PROJECT 3  |  Knowledge Representation & Reasoning

Page PAGE1 of NUMPAGES2