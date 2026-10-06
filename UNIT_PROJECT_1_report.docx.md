# Text-only document extract

Source document: UNIT_PROJECT_1_report.docx

Images and layout omitted. Claims below are source text, not independently verified results.



UNIT PROJECT 1

Family Knowledge Base and AIML Chatbot Integration

Course:

Knowledge Representation & Reasoning (KRR)

Student:

Syed Muhammad Imad

Semester:

Spring 2026

Tools Used:

Python, Prolog (pytholog), AIML (python-aiml)



1.  Introduction & Objective

This project builds a conversational agent that answers natural-language questions about family relationships. Three pieces work together: a Prolog knowledge base holding facts and inference rules, an AIML layer that recognises how a question was phrased, and a Python middleware that turns a recognised pattern into a Prolog query and turns the result back into a plain English sentence.

The brief asked for a knowledge base with more than 30 relationship rules built from at least 5 fact types, reasoning through the pytholog library, and a chatbot interface that could handle relationship questions, fact lookups, list queries, and yes/no questions.



2.  System Architecture

The system follows a three-layer architecture, separating natural language understanding from logical reasoning:



Conversational Interface (AIML):  The file family_chat.aiml contains over 80 categories of pattern-template pairs that recognise different phrasings of the same underlying question (e.g. "Who is father of X", "Who is the father of X", "Find father of X" all map to the same query type).

Middleware Logic (Python):  The FamilyKnowledgeAgent class in family_agent.py loads both the AIML kernel and the Prolog knowledge base. It parses the AIML kernel's tagged response (e.g. QUERY:father:omar), builds the corresponding Prolog query string, executes it, and formats the result into a natural language sentence.

Knowledge Base & Inference Engine (Prolog):  Implemented using the pytholog library, which provides a lightweight Prolog interpreter inside Python. Facts and rules are loaded into a pytholog.KnowledgeBase object, which performs backward-chaining resolution to answer queries.



Data Flow

Request Pipeline

User Input (natural language)

      ↓

AIML Kernel — pattern matching → tagged response string

      ↓

Python Agent — parses tag, builds Prolog query

      ↓

pytholog KnowledgeBase — backward-chaining resolution

      ↓

Python Agent — formats result into natural language

      ↓

Response shown to User





3.  Knowledge Base Design

The knowledge base lives in family_kb.pl and is loaded into pytholog at runtime. It clears the assignment's minimum of 5 fact types and 30 relationship rules by a healthy margin.



3.1  Fact Types (6 implemented — exceeds 5 minimum)

Fact Type

Example

Instances

male/1

male(tariq).

7

female/1

female(sara).

5

parent/2

parent(tariq, ali).

13

married/2

married(ali, fatima).

4

dob/2

dob(omar, 2003).

12

city/2

city(omar, lahore).

12

profession/2

profession(ali, doctor).

12



The family tree spans three generations rooted at Tariq and Sara: their three sons (Kamran, Ali, Usman), the sons' spouses, and a third generation of grandchildren (Omar, Alia, Hassan, Adam). That's enough spread to exercise direct, sibling, in-law, and multi-generational rules properly rather than just on paper.



3.2  Relationship Rules (36 implemented — exceeds 30 minimum)

Every rule is derived from the base facts using Prolog's logical conjunction (comma operator for AND) and, where needed, the inequality operator (\=) to prevent self-matching.



#

Rule

Prolog Definition

1

father/2

father(F,C) :- male(F), parent(F,C).

2

mother/2

mother(M,C) :- female(M), parent(M,C).

3

child/2

child(C,P) :- parent(P,C).

4

son/2

son(S,P) :- male(S), parent(P,S).

5

daughter/2

daughter(D,P) :- female(D), parent(P,D).

6

sibling/2

sibling(A,B) :- parent(P,A), parent(P,B), A \= B.

7

brother/2

brother(B,P) :- male(B), sibling(B,P).

8

sister/2

sister(S,P) :- female(S), sibling(S,P).

9

grandparent/2

grandparent(G,C) :- parent(G,P), parent(P,C).

10

grandfather/2

grandfather(G,C) :- male(G), grandparent(G,C).

11

grandmother/2

grandmother(G,C) :- female(G), grandparent(G,C).

12

grandchild/2

grandchild(C,G) :- grandparent(G,C).

13

grandson/2

grandson(C,G) :- male(C), grandparent(G,C).

14

granddaughter/2

granddaughter(C,G) :- female(C), grandparent(G,C).

15

great_grandparent/2

great_grandparent(G,C) :- parent(G,P), grandparent(P,C).

16

uncle/2

uncle(U,P) :- brother(U,Par), parent(Par,P).

17

aunt/2

aunt(A,P) :- sister(A,Par), parent(Par,P).

18

cousin/2

cousin(C1,C2) :- parent(P1,C1), parent(P2,C2), sibling(P1,P2), C1 \= C2.

19

ancestor/2

ancestor(A,C) :- parent(A,C).  (+ recursive clause)

20

descendant/2

descendant(D,A) :- ancestor(A,D).

21

spouse/2

spouse(X,Y) :- married(X,Y).  (+ reverse clause)

22

father_in_law/2

father_in_law(F,P) :- spouse(P,S), father(F,S).

23

mother_in_law/2

mother_in_law(M,P) :- spouse(P,S), mother(M,S).

24

parent_in_law/2

parent_in_law(P,X) :- father_in_law(P,X). (+ mother clause)

25

brother_in_law/2

brother_in_law(B,P) :- spouse(P,S), brother(B,S).

26

sister_in_law/2

sister_in_law(Si,P) :- spouse(P,S), sister(Si,S).

27

age/2

age(Person,Age) :- dob(Person,Y), Age is 2026 - Y.

28

older_than/2

older_than(P1,P2) :- dob(P1,Y1), dob(P2,Y2), Y1 < Y2.

29

same_city/2

same_city(P1,P2) :- city(P1,C), city(P2,C), P1 \= P2.

30

same_profession/2

same_profession(P1,P2) :- profession(P1,J), profession(P2,J), P1 \= P2.

31

father_of_son/2

father_of_son(F,S) :- father(F,S), male(S).

32

father_of_daughter/2

father_of_daughter(F,D) :- father(F,D), female(D).

33

mother_of_son/2

mother_of_son(M,S) :- mother(M,S), male(S).

34

mother_of_daughter/2

mother_of_daughter(M,D) :- mother(M,D), female(D).

35

nuclear_family/2

nuclear_family(X,Y) :- shared P1,P2, X \= Y, P1 \= P2.

36

is_married/1

is_married(X) :- spouse(X,_).



4.  AIML Conversational Layer

The file family_chat.aiml defines 80+ <category> pattern-template pairs grouped by relationship type, each using the wildcard symbol * to capture the subject's name. The kernel returns a tagged string (rather than a final sentence) which the Python layer interprets — this separation keeps natural-language pattern recognition independent from the logic that executes Prolog queries.



4.1  Pattern Categories Implemented

Greetings — HI, HELLO, HEY, BYE, EXIT

Direct relationship queries — father, mother, siblings, brothers, sisters, children

Extended relationship queries — grandparents, uncles, aunts, cousins, ancestors, in-laws

Fact queries — date of birth, age, city, profession

Aggregate queries — same city as X, list all males/females, list all married couples

Yes/No queries — "Is X father of Y?", "Are X and Y siblings?", "Is X married?", "Is X older than Y?"



4.2  Example Pattern-Template Mapping

AIML Category Example

<category>

  <pattern>WHO IS THE FATHER OF *</pattern>

  <template>QUERY:father:<star/></template>

</category>





The same query is also reachable through several alternate phrasings — "Who is father of *", "Find father of *", "Tell me the father of *" — so the chatbot doesn't break just because a question was worded slightly differently than expected.



5.  Python Integration Layer

The FamilyKnowledgeAgent class in family_agent.py is the bridge between the AIML kernel and the Prolog knowledge base. Its responsibilities include:



Loading the Prolog KB:  Facts and rules are passed as a Python list of strings directly into pytholog.KnowledgeBase to avoid file-parsing inconsistencies.

Loading the AIML kernel:  via aiml.Kernel().learn(family_chat.aiml).

Query routing:  The _relationship_answer() and _yesno_answer() methods map each relationship keyword to the correct Prolog query string and execute it through pytholog.

Result formatting:  Helper functions _unique(), _names(), and _fmt() remove duplicate Prolog bindings and join multiple results into grammatically correct English (e.g. "Omar and Alia" instead of a raw list).



6.  Sample Chat Logs & Demonstration

The following console session demonstrates the chatbot successfully resolving direct facts, multi-generation relationships, in-law relationships, recursive ancestry queries, and yes/no confirmations — covering every required query category from the assignment brief.



Family Knowledge Base Chatbot — Console Session

You:  Hi

Bot:  Hello! I am the Family Knowledge Base assistant. Ask me about any family member!

You:  Who is father of Omar?

Bot:  Ali is the father of Omar.

You:  Who are the siblings of Omar?

Bot:  Alia is the sibling of Omar.

You:  Who is the grandfather of Adam?

Bot:  Tariq is the grandfather of Adam.

You:  Who are the uncles of Adam?

Bot:  Ali and Usman are the uncles of Adam.

You:  Is Ali father of Omar?

Bot:  Yes, Ali is father of Omar.

You:  Are Omar and Alia siblings?

Bot:  Yes, Omar and Alia are siblings.

You:  Is Tariq older than Ali?

Bot:  Yes, Tariq is older than Ali.

You:  Who is the spouse of Ali?

Bot:  Fatima is the spouse of Ali.

You:  What is the profession of Kamran?

Bot:  Kamran is a engineer.

You:  List all males

Bot:  All males in the family: Tariq, Kamran, Ali, Usman, Omar, Hassan and Adam.

You:  Show all married

Bot:  Married couples: Tariq & Sara; Ali & Fatima; Kamran & Noor; Omar & Zara.

You:  Bye

Bot:  Goodbye! Come back anytime.



7.  Requirements Mapping

The table below maps each assignment requirement to where it is satisfied in the implementation, for quick verification.



Requirement

Implementation

30+ relationship rules

36 rules implemented in family_kb.pl

5+ fact types

7 fact types: male, female, parent, married, dob, city, profession

Prolog integration via pytholog

pytholog.KnowledgeBase loaded in FamilyKnowledgeAgent.__init__

AIML chatbot interface

family_chat.aiml with 80+ categories

Natural language variants accepted

Multiple phrasing patterns per query type (e.g. "who is", "find", "tell me")

Relationship, fact, list, yes/no queries

All 4 categories implemented and demonstrated in Section 6

Pure Python project (PyCharm)

requirements.txt: python-aiml, pytholog



8.  Conclusion

The final implementation covers every requirement of Unit Project 1: a Prolog knowledge base with 7 fact types and 36 inference rules, reasoning handled by pytholog, and an AIML chatbot that recognises over 80 distinct phrasings across relationship, fact, list, and yes/no queries. Keeping AIML, Python, and Prolog as separate layers made each one easy to test on its own, and it means new relationship types or a larger family tree can be added later without touching the other two layers.



UNIT PROJECT 1  |  Knowledge Representation & Reasoning

Page PAGE of NUMPAGES







