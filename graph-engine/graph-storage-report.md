# Text-only document extract

Source document: UNIT PROJECT 3.docx

Images and layout omitted. Claims below are source text, not independently verified results.

UNIT PROJECT 3: GRAPH-BASED KNOWLEDGE REPRESENTATION AND REASONING USING NEO4J 

reference: Knowledge Representation & Reasoning (KRR)

Student Name: Syed Muhammad Imad


1. INTRODUCTION & SYSTEM ARCHITECTURE

This project modernizes a conversational rule-based system by migrating its underlying data storage from a Prolog flat-file architecture into a high-performance Neo4j Graph Database. The hybrid intelligent system utilizes a three-tier decoupled architecture designed for fluid knowledge acquisition, graph traversal, and logical inference. 

Architecture Stack 

Conversational Interface (AIML): Manages natural language pattern matching. family_input.aiml handles the parsing rules for knowledge acquisition , while family_chat.aiml processes conversational entity resolution for retrieval. 

Middleware Processing (Python): Serves as the logic integration framework. It instantiates the GraphDatabase native driver connections, performs string normalization, sanitizes data inputs, and dynamically translates text templates into operational Cypher transactions. 

Knowledge Base & Inference Engine (Neo4j): Acts as the unified storage and graph-reasoning cluster. Relationships are maintained natively as structural pointer pathways, bypassing expensive relational table joins. 

2. GRAPH MODEL DESIGN

The knowledge base represents familial and social structures using an intentional graph schema composed of labeled nodes, directional relationships, and key-value atomic properties. 

Node Labels: Entities are universally labeled as :Person.

Node Properties: * name (Unique string identifier used for lookups)

gender (male or female flags used for line-of-descent checks)

city (Residential property used for geospatial hub analytics)

profession (Vocational property tracking employment data)

dob (Date of birth tracker)

Relationship Types: * [:PARENT_OF]: A directed relationship going from parent to child.

[:MARRIED_TO]: A symmetric, bidirectional relationship establishing marital linkage.

Visually Mapping the Graph Layout

Below is the live structural layout of the family network database showing active nodes, property keys, and edge labels.



3. LOGIC & REASONING MECHANISM: PROLOG VS. NEO4J

Transitioning from a first-order logic engine (Prolog) to a graph-based reasoning network (Neo4j) alters the computational model for inference: 

Rule Execution vs. Path Traversals: Prolog uses backward-chaining resolution over horn clauses, stack-evaluating predicates like grandfather(G, C) :- parent(G, P), parent(P, C). Neo4j evaluates this relationship via pattern-matching memory hops (MATCH (g)-[:PARENT_OF]->()-[:PARENT_OF]->(c)), optimizing execution times for deeply nested trees.

Identity Constraints: In Prolog, preventing self-matching loops requires manual declaration tags such as A \= B. In Neo4j Cypher queries, graph traversals can filter identity loopbacks instantly using inline constraints like WHERE s <> c. 

4. SAMPLE CHAT LOGS & DEMONSTRATION

Phase 1: Natural Language Knowledge Acquisition 

The interactive console takes raw user inputs, extracts parameters through conversational slots, and dynamically populates node attributes or edge connections within the database:

============================================================

  KRR project 3 — Neo4j Family Knowledge Base Chatbot

============================================================



📥  MODE 1: ADD FACTS TO GRAPH

    Type 'done' to switch over to query engine evaluation mode.



You (add): add male faraz 

Bot: Got it! Fact added to Neo4j: Faraz is marked as male.



You (add): add male mansoor 

Bot: Got it! Fact added to Neo4j: Mansoor is marked as male.



You (add): faraz is parent of mansoor 

Bot: Got it! Fact added to Neo4j: Faraz is the parent of Mansoor.



You (add): add male azfar  

Bot: Got it! Fact added to Neo4j: Azfar is marked as male.



You (add): azfar is parent of faraz 

Bot: Got it! Fact added to Neo4j: Azfar is the parent of Faraz.



You (add): faraz lives in seikhupura 

Bot: Got it! Fact added to Neo4j: Faraz's city is set to seikhupura.



You (add): done



Phase 2: Complex Graph Traversal, Analytics, & Inference 

Once switched to query evaluation mode, the system successfully processes single-hop lookups, multi-hop structural traversals , graph metric aggregations , and contextual property inference engine recommendations: 

🔍  MODE 2: QUERY GRAPH PATTERNS

    Type 'exit' to terminate engine orchestration run.



You (query): who is the grandfather of mansoor

Bot: The grandfather of Mansoor is Azfar.



You (query): identify the main family hub city

Bot: Graph-based metrics show that 'Seikhupura' is the primary family hub node with residents.



You (query): recommend meetup for faraz

Bot: Inference engine discovery: We recommend Faraz meet up with Azfar because they reside in the same city but aren't directly linked in the immediate tree branches!

5. CONCLUSION

The architecture satisfies all baseline functional goals. By moving from Prolog rules to native graph paths, the system demonstrates robust relational tracking, fast structural traversals, and dynamic data indexing. This implementation validates the efficiency of using conversational graph database integrations for managing highly relational data.



