# Text-only document extract

Source document: UNIT_PROJECT_2_report.docx

Images and layout omitted. Claims below are source text, not independently verified results.



UNIT PROJECT 2

Dynamic Knowledge Acquisition via Natural Language and File Handling

reference:

Knowledge Representation & Reasoning (KRR)

Contributor:

Syed Muhammad Imad


Spring 2026

Tools Used:

Python, Prolog (pytholog), AIML (python-aiml), Flask



1.  Introduction & Objective

Unit Project 2 takes the static family knowledge base from Unit Project 1 and makes it learn on the fly. Instead of pre-loading a fixed list of facts into the Prolog file, the system now picks up new facts straight from conversation: an AIML interface parses statements like "Add male Ali" or "Ali is parent of Omar", Python converts what it parsed into valid Prolog syntax, and those facts get written into family_kb.pl for real — the knowledge base grows on disk, not just in memory for the length of one session.

The brief broke this down into six steps: copy the Unit Project 1 codebase, strip the hard-coded facts out of the Prolog file but keep the rules, build a new AIML file just for capturing facts through natural language, pull the AIML-recognised values into Python, use string handling to turn that input into valid Prolog fact syntax, use file handling to append the new facts to the knowledge base, and finally reuse the original project 1 AIML file to query and check that the new facts actually stuck.



2.  System Architecture — Dual-Mode Agent

The system is restructured around two cooperating agents inside family_agent.py, both wrapped by a single FamilyKnowledgeAgent facade so the rest of the application (console runner or Flask app) does not need to know which mode is active:



InputAgent — Knowledge Acquisition Mode:  Loads family_input.aiml and listens for fact-style sentences. Recognised input is converted into a tagged string of the form ADDFACT:type:arg1:arg2, which Python then parses, normalises, and queues as a pending Prolog fact.

QueryAgent — Reasoning Mode:  Re-uses family_chat.aiml unchanged from Unit Project 1. On each reload, it re-reads every fact that has been saved to disk and re-builds a fresh pytholog.KnowledgeBase by combining the dynamic facts with the fixed rule set, so newly learned facts are immediately reasoned over.

Flask Web Layer (app.py):  Exposes three endpoints — /add (routes to InputAgent), /ask (routes to QueryAgent), and /reload (forces the QueryAgent to re-read the KB file) — allowing a browser-based UI to switch between teaching the bot and querying it.



Knowledge Acquisition Pipeline

End-to-End Flow

User: "Ali is parent of Omar"

      ↓

family_input.aiml — pattern match → "ADDFACT:parent:ali:omar"

      ↓

InputAgent._handle_add() — splits tag, normalises text

      ↓

build_fact() — string handling → "parent(ali, omar)."

      ↓

write_fact_to_kb() — file handling → appended to family_kb.pl

      ↓

QueryAgent.reload() — re-reads file, rebuilds pytholog KB

      ↓

family_chat.aiml — "Who is father of Omar?" now resolves correctly





3.  Prolog Knowledge Base — Rules Retained, Facts Removed

Per Step 2 of the project, family_kb.pl was edited to strip out every hard-coded fact from Unit Project 1 while leaving the full 33-rule inference engine alone. A DYNAMIC FACTS SECTION comment block was added at the bottom of the file — that’s the insertion point the file-handling logic targets when it appends new facts.



family_kb.pl — Structure After Editing

% RULES (33 total — unchanged from project 1)

father(F, C) :- male(F), parent(F, C).

mother(M, C) :- female(M), parent(M, C).

  ...  (31 more rules)  ...

is_married(X) :- spouse(X, _).



% ==========================================

% DYNAMIC FACTS SECTION

% Facts below are added by the chatbot

% ==========================================

  ← new facts are appended here at runtime





All 33 relational rules from Unit Project 1 carried over without modification: father, mother, sibling, brother, sister, grandparent (and its gendered variants), great-grandparent, uncle, aunt, cousin, the recursive ancestor/descendant pair, spouse, all four in-law relations, same_city, same_profession, and the gendered parent-of-son/daughter helpers. None of the rule logic needed to change, since a rule reasons over whatever facts happen to exist in the KB at query time — it doesn’t care how those facts got there.



4.  family_input.aiml — Capturing Facts via Natural Language

A separate AIML file was built just to recognise fact-stating sentences rather than questions. It holds 66 categories covering all seven fact types in the schema (male, female, parent, married, dob, city, profession), each one accepting a few different natural phrasings.



4.1  Pattern Categories

Gender facts:  "Add male X", "X is male", "X is a boy/man", and the female equivalents.

Parent facts:  "X is parent of Y", "X is father/mother of Y", "X has child Y".

Marriage facts:  "X is married to Y", "X and Y are married", "X is the husband/wife of Y".

Date of birth, city, and profession facts:  "X was born in YEAR", "X lives in CITY", "X works as PROFESSION", each with multiple alternate phrasings.

Control commands:  "Show facts" (list pending and saved facts), "Save facts" (commit to disk), "Clear facts" (reset the dynamic section), and a HELP category listing all supported phrasings.



4.2  Example Category

family_input.aiml — Parent Fact Pattern

<category>

  <pattern>* IS PARENT OF *</pattern>

  <template>ADDFACT:parent:<star index="1"/>:<star index="2"/></template>

</category>





Each category returns a machine-readable tag instead of a conversational sentence, the same design choice used for family_chat.aiml in project 1. The AIML layer’s only job is recognising natural language; all the data construction logic lives in Python.



5.  String Handling — Building Valid Prolog Syntax

Once the AIML kernel returns a tag such as ADDFACT:parent:ali:omar, the InputAgent splits the string on the colon delimiter and runs the pieces through a couple of string-handling functions before anything touches disk:



_prolog_atom() — Sanitising User Text Into a Valid Prolog Atom

def _prolog_atom(value: str) -> str:

    atom = str(value).lower().strip()

    atom = re.sub(r"[^a-z0-9_]+", "_", atom)

    return atom.strip("_")





This catches malformed Prolog syntax before it happens — a user typing "Add female Sara Khan" becomes the safe atom sara_khan instead of two illegal tokens.



build_fact() — Assembling the Final Fact String

def build_fact(fact_type: str, *args) -> str:

    fact_type = _prolog_atom(fact_type)

    clean_args = [_prolog_atom(a) for a in args]

    if len(clean_args) == 1:

        return f"{fact_type}({clean_args[0]})."

    elif len(clean_args) == 2:

        return f"{fact_type}({clean_args[0]}, {clean_args[1]})."





So build_fact("parent", "ali", "omar") returns the exact Prolog-legal string "parent(ali, omar)." — parenthesised, comma-separated, full stop included, ready to drop straight into the .pl file.



6.  File Handling — Persisting Facts to family_kb.pl

Three functions handle the file-handling side of the project, all working against the same KB_FILE path and the % DYNAMIC FACTS SECTION marker:



fact_already_exists():  Reads the entire KB file and compares a normalised, whitespace-stripped version of the candidate fact against every existing fact line, skipping rule lines (those containing :-) and comments. This prevents duplicate facts from being written if the same sentence is taught twice.

write_fact_to_kb():  Splits the file's text at the DYNAMIC FACTS SECTION marker and inserts the new fact line immediately after it, then writes the updated content back to disk — implementing genuine persistent file modification rather than an in-memory-only update.

read_all_dynamic_facts():  Re-opens the file and returns every fact line found after the marker, which the QueryAgent uses on every reload to rebuild its in-memory pytholog KnowledgeBase from what is actually saved on disk.



write_fact_to_kb() — Core File-Handling Logic

def write_fact_to_kb(fact_str: str) -> bool:

    if fact_already_exists(fact_str):

        return False

    content = KB_FILE.read_text(encoding="utf-8")

    parts   = content.split(FACTS_MARKER)

    updated = parts[0] + FACTS_MARKER + parts[1].rstrip() + "\n" + fact_str + "\n"

    KB_FILE.write_text(updated, encoding="utf-8")

    return True





7.  Sample Session — Acquisition Then Verification

The console runner walks through both modes in one sitting: facts get taught first, saved to disk, the KnowledgeBase reloads, and then the original family_chat.aiml interface — untouched since project 1 — is used to check the new knowledge actually got learned. That last step is what Step 7 of the project was asking for.



Phase 1 — Teaching Facts (InputAgent / family_input.aiml)

You (add):  Add male ali

Bot:  Got it! Fact ready: male(ali).\nSay 'Save facts' to write to knowledge base, or keep adding more.

You (add):  Add female fatima

Bot:  Got it! Fact ready: female(fatima).

You (add):  Add male omar

Bot:  Got it! Fact ready: male(omar).

You (add):  Ali is parent of Omar

Bot:  Got it! Fact ready: parent(ali, omar).

You (add):  Fatima is parent of Omar

Bot:  Got it! Fact ready: parent(fatima, omar).

You (add):  Ali is married to Fatima

Bot:  Got it! Fact ready: married(ali, fatima).

You (add):  Show facts

Bot:  Pending (not saved yet):\n  male(ali).\n  female(fatima).\n  male(omar).\n  parent(ali, omar).\n  parent(fatima, omar).\n  married(ali, fatima).

You (add):  Save facts

Bot:  Saved 6 fact(s) to family_kb.pl.



Phase 2 — Verifying via the Unchanged project 1 Interface (QueryAgent / family_chat.aiml)

You (query):  Who is father of Omar?

Bot:  Ali is the father of Omar.

You (query):  Who is the mother of Omar?

Bot:  Fatima is the mother of Omar.

You (query):  Is Ali married?

Bot:  Yes, Ali is married.

You (query):  Who is the spouse of Ali?

Bot:  Fatima is the spouse of Ali.



8.  Flask Web Interface

app.py puts the dual-mode agent on HTTP so the whole teach-then-query workflow can run in a browser instead of the console. The routes keep the same split that family_agent.py already set up:



app.py — Route Summary

POST /add      → agent.ask_input(message)   (InputAgent — teach facts)

POST /ask      → agent.ask(message)          (QueryAgent — answer questions)

POST /reload   → agent.reload()              (re-sync KB after saving)

GET  /         → renders templates/index.html (tabbed chat UI)





The front end (templates/index.html) has two tabs, Add Facts and Query KB, each posting to its own endpoint, plus a manual Reload KB button so the user can refresh the QueryAgent’s in-memory knowledge right after saving new facts.



9.  Requirements Mapping

Each of the seven steps from the project 2 brief maps to a specific part of the implementation:



project Step

Implementation

1. Copy Unit Project 1

Folder structure, rule set, and family_chat.aiml carried over unchanged

2. Remove facts, keep rules

family_kb.pl retains all 33 rules; facts deleted, replaced with DYNAMIC FACTS SECTION marker

3. New AIML for fact input

family_input.aiml — 66 categories covering all 7 fact types + control commands

4. Fetch AIML variables in Python

InputAgent._handle_add() parses the ADDFACT: tag returned by the AIML kernel

5. String handling to build facts

_prolog_atom() and build_fact() sanitise input and assemble valid Prolog syntax

6. File handling to update KB

write_fact_to_kb() appends new facts to family_kb.pl after the marker; read/clear functions complete the file I/O cycle

7. Reuse existing AIML to test

QueryAgent loads the unmodified family_chat.aiml from project 1 and resolves queries against the newly saved facts



10.  Conclusion

Unit Project 2 shows that the knowledge representation layer from project 1 didn’t need to change at all — only the way facts get into it did. AIML handles recognising natural language, Python’s string handling turns that into valid Prolog syntax, and Python’s file handling makes it stick on disk. Put together, someone with zero Prolog knowledge can grow the family tree just by typing normal English sentences, and the original 33-rule engine keeps reasoning correctly over whatever ends up in the file.



UNIT PROJECT 2  |  Knowledge Representation & Reasoning

Page PAGE of NUMPAGES







