"""
family_agent.py
KRR project 2 - Muhammad Imad

Two modes:
  INPUT MODE  — collects facts from natural language → writes to family_kb.pl
  QUERY MODE  — queries the KB using the facts that were saved

Flow:
  1. User chats with INPUT bot to add facts
  2. Facts are written to family_kb.pl using file handling
  3. User switches to QUERY bot to ask questions about the family
"""
import time

if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
import re
from datetime import date
from pathlib import Path

import aiml
import pytholog as pl

# ─────────────────────────────────────────
# File paths
# ─────────────────────────────────────────
BASE_DIR       = Path(__file__).parent
DATA_DIR       = BASE_DIR / "sample data"
if not DATA_DIR.exists():
    DATA_DIR   = BASE_DIR / "sample_data"

KB_FILE        = DATA_DIR / "family_kb.pl"
INPUT_AIML     = DATA_DIR / "family_input.aiml"
QUERY_AIML     = DATA_DIR / "family_chat.aiml"

# Marker line in KB — facts are written after this line
FACTS_MARKER   = "% DYNAMIC FACTS SECTION"


# ═══════════════════════════════════════════════════════════════
# HELPER UTILITIES
# ═══════════════════════════════════════════════════════════════

def _unique(results):
    seen, out = set(), []
    for item in (results or []):
        if not isinstance(item, dict):
            continue
        key = tuple(sorted(item.items()))
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _names(results, var="X"):
    return [r[var].capitalize() for r in _unique(results) if var in r]


def _fmt(names):
    if not names:
        return None
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _prolog_atom(value: str) -> str:
    """Convert natural-language text into a safe lowercase Prolog atom."""
    atom = str(value).lower().strip()
    atom = re.sub(r"[^a-z0-9_]+", "_", atom)
    return atom.strip("_")


def _canonical_fact(fact_str: str) -> str:
    """Normalise a fact for exact duplicate comparisons."""
    return re.sub(r"\s+", "", fact_str.strip().rstrip("."))


# ═══════════════════════════════════════════════════════════════
# FACT BUILDER  — string handling to create Prolog fact strings
# ═══════════════════════════════════════════════════════════════

def build_fact(fact_type: str, *args) -> str:
    """
    Build a valid Prolog fact string from type and arguments.
    Uses string handling as required by project.

    Examples:
      build_fact("male", "ali")        → "male(ali)."
      build_fact("parent", "ali","omar") → "parent(ali, omar)."
    """
    fact_type = _prolog_atom(fact_type)
    clean_args = [_prolog_atom(a) for a in args]

    if not fact_type or not clean_args or any(not arg for arg in clean_args):
        return ""

    if len(clean_args) == 1:
        return f"{fact_type}({clean_args[0]})."
    elif len(clean_args) == 2:
        return f"{fact_type}({clean_args[0]}, {clean_args[1]})."
    return ""


def fact_already_exists(fact_str: str) -> bool:
    """Check if a fact already exists in the KB file."""
    try:
        target = _canonical_fact(fact_str)
        for line in KB_FILE.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("%") or ":-" in stripped:
                continue
            if _canonical_fact(stripped) == target:
                return True
        return False
    except Exception:
        return False


def write_fact_to_kb(fact_str: str) -> bool:
    """
    File handling: append a new Prolog fact to family_kb.pl
    after the DYNAMIC FACTS SECTION marker.
    Returns True if written, False if duplicate.
    """
    allowed = {"male": 1, "female": 1, "parent": 2, "married": 2,
               "dob": 2, "city": 2, "profession": 2}
    match = re.fullmatch(r"([a-z_]+)\(([^()]*)\)\.", fact_str)
    if not match: raise ValueError("Invalid fact syntax")
    kind, values = match[1], [v.strip() for v in match[2].split(",")]
    if kind not in allowed or len(values) != allowed[kind]: raise ValueError("Unsupported fact")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", values[0]): raise ValueError("Invalid person name")
    if kind in {"parent", "married"} and values[0] == values[1]: raise ValueError("Self relationships are invalid")
    if kind == "dob" and (not values[1].isdigit() or not 1900 <= int(values[1]) <= date.today().year):
        raise ValueError("Birth year must be between 1900 and the current year")
    if kind == "parent":
        edges = {}
        for line in KB_FILE.read_text(encoding="utf-8").splitlines():
            relation = re.fullmatch(r"parent\(\s*([a-z0-9_]+)\s*,\s*([a-z0-9_]+)\s*\)\.", line.strip())
            if relation: edges.setdefault(relation[1], set()).add(relation[2])
        pending = [values[1]]; visited = set()
        while pending:
            person = pending.pop()
            if person == values[0]: raise ValueError("Parent relationship would create a cycle")
            if person in visited: continue
            visited.add(person); pending.extend(edges.get(person, ()))

    if fact_already_exists(fact_str):
        return False  # Duplicate — skip

    try:
        content = KB_FILE.read_text(encoding="utf-8")

        if FACTS_MARKER in content:
            # Insert after the marker line
            parts   = content.split(FACTS_MARKER, 1)
            updated = parts[0] + FACTS_MARKER + parts[1].rstrip() + "\n" + fact_str + "\n"
        else:
            # Append at end of file
            updated = content.rstrip() + "\n" + fact_str + "\n"

        KB_FILE.write_text(updated, encoding="utf-8")
        return True
    except Exception as e:
        raise OSError("Could not persist family facts") from e


def read_all_dynamic_facts() -> list:
    """Read and return all dynamically added facts from KB file."""
    try:
        content  = KB_FILE.read_text(encoding="utf-8")
        if FACTS_MARKER not in content:
            return []
        facts_section = content.split(FACTS_MARKER)[-1]
        lines = [
            line.strip()
            for line in facts_section.splitlines()
            if line.strip() and not line.strip().startswith("%")
        ]
        return lines
    except Exception:
        return []


def clear_dynamic_facts():
    """Remove all dynamically added facts from KB file."""
    try:
        content = KB_FILE.read_text(encoding="utf-8")
        if FACTS_MARKER in content:
            parts   = content.split(FACTS_MARKER, 1)
            updated = parts[0] + FACTS_MARKER + "\n"
            KB_FILE.write_text(updated, encoding="utf-8")
    except Exception as e:
        raise OSError("Could not clear family facts") from e


# ═══════════════════════════════════════════════════════════════
# INPUT AGENT  — collects facts via natural language
# ═══════════════════════════════════════════════════════════════

class InputAgent:
    """
    Mode 1: Collects family facts from the user via natural language.
    Uses family_input.aiml to parse patterns.
    Writes facts to family_kb.pl using file handling.
    """

    def __init__(self):
        self.kernel   = aiml.Kernel()
        self.kernel.learn(str(INPUT_AIML))
        self._session = "input_session"
        self._pending = []          # facts collected but not yet saved

    def ask(self, user_input: str) -> str:
        clean    = re.sub(r"[?!.,]", "", user_input).upper().strip()
        response = self.kernel.respond(clean, self._session).strip()

        # ── ADDFACT responses ────────────────────────────────────────────────
        if response.startswith("ADDFACT:"):
            return self._handle_add(response)

        # ── CONTROL responses ────────────────────────────────────────────────
        if response.startswith("CONTROL:"):
            return self._handle_control(response)

        return response

    def _handle_add(self, response: str) -> str:
        """
        Parse ADDFACT:type:arg1[:arg2] and build+store a Prolog fact.
        String handling: split on ':', normalise, call build_fact().
        """
        parts     = response.split(":")
        fact_type = parts[1].lower()  if len(parts) > 1 else ""
        arg1      = parts[2].lower()  if len(parts) > 2 else ""
        arg2      = parts[3].lower()  if len(parts) > 3 else ""

        # ── String handling: normalise names ────────────────────────────────
        arg1 = arg1.strip().replace(" ", "_")
        arg2 = arg2.strip().replace(" ", "_")

        # ── Build fact string ────────────────────────────────────────────────
        if arg2:
            fact_str = build_fact(fact_type, arg1, arg2)
        else:
            fact_str = build_fact(fact_type, arg1)

        if not fact_str:
            return "I could not create a fact from that. Please try again."

        self._pending.append(fact_str)
        return (
            f"Got it! Fact ready: {fact_str}\n"
            f"Say 'Save facts' to write to knowledge base, or keep adding more."
        )

    def _handle_control(self, response: str) -> str:
        command = response.split(":")[1].lower() if ":" in response else ""

        if command == "save":
            return self._save_all()

        if command == "show":
            saved   = read_all_dynamic_facts()
            pending = self._pending
            msg     = ""
            if pending:
                msg += f"Pending (not saved yet):\n" + "\n".join(f"  {f}" for f in pending) + "\n"
            if saved:
                msg += f"Saved in KB:\n" + "\n".join(f"  {f}" for f in saved)
            return msg if msg else "No facts yet. Start adding facts!"

        if command == "clear":
            self._pending.clear()
            clear_dynamic_facts()
            return "All dynamic facts cleared from knowledge base."

        return "Unknown command."

    def _save_all(self) -> str:
        """File handling: write all pending facts to KB file."""
        if not self._pending:
            return "No pending facts to save."

        saved_count   = 0
        skipped_count = 0
        saved_facts   = []

        for fact_str in self._pending:
            try:
                written = write_fact_to_kb(fact_str)
            except (ValueError, OSError) as exc:
                return f"Save failed: {exc}. Pending facts were retained; already saved facts are deduplicated on retry."
            if written:
                saved_count += 1
                saved_facts.append(fact_str)
            else:
                skipped_count += 1

        self._pending.clear()

        msg = f"Saved {saved_count} fact(s) to family_kb.pl."
        if skipped_count:
            msg += f" ({skipped_count} duplicate(s) skipped.)"
        if saved_facts:
            msg += "\nSaved:\n" + "\n".join(f"  {f}" for f in saved_facts)
        return msg


# ═══════════════════════════════════════════════════════════════
# QUERY AGENT  — queries the KB using saved facts
# ═══════════════════════════════════════════════════════════════

class QueryAgent:
    """
    Mode 2: Queries the family KB using pytholog.
    Loads the KB file (now containing dynamic facts) at runtime.
    Uses family_chat.aiml to parse natural language queries.
    """

    _CURRENT_YEAR = date.today().year

    def __init__(self):
        self.kernel = aiml.Kernel()
        self.kernel.learn(str(QUERY_AIML))
        self._load_kb()

    def _load_kb(self):
        """Load the KB inline — reads dynamic facts from file and adds to pytholog."""
        self.kb = pl.KnowledgeBase("family")

        # Read dynamic facts from file using file handling
        dynamic_facts = read_all_dynamic_facts()

        # ── Fixed rules (pytholog-compatible syntax) ─────────────────────────
        rules = [
            "child(C, P) :- parent(P, C)",
            "father(F, C) :- male(F), parent(F, C)",
            "mother(M, C) :- female(M), parent(M, C)",
            "son(S, P) :- male(S), parent(P, S)",
            "daughter(D, P) :- female(D), parent(P, D)",
            "sibling(A, B) :- parent(P, A), parent(P, B), neq(A,B)",
            "brother(B, P) :- male(B), sibling(B,P)",
            "sister(S, P) :- female(S), sibling(S,P)",
            "grandparent(G, C) :- parent(G, P), parent(P, C)",
            "grandfather(G, C) :- male(G), parent(G, P), parent(P, C)",
            "grandmother(G, C) :- female(G), parent(G, P), parent(P, C)",
            "grandchild(C, G) :- parent(G, P), parent(P, C)",
            "grandson(C, G) :- male(C), parent(G, P), parent(P, C)",
            "granddaughter(C, G) :- female(C), parent(G, P), parent(P, C)",
            "great_grandparent(G, C) :- parent(G, P), parent(P, Q), parent(Q, C)",
            "ancestor(A, C) :- parent(A, C)",
            "ancestor(A, C) :- parent(A, P), ancestor(P, C)",
            "descendant(D, A) :- ancestor(A, D)",
            "uncle(U, P) :- brother(U,Par), parent(Par,P)",
            "aunt(A, P) :- sister(A,Par), parent(Par,P)",
            "cousin(C1, C2) :- parent(P1,C1), parent(P2,C2), sibling(P1,P2), neq(C1,C2)",
            "spouse(X, Y) :- married(X, Y)",
            "spouse(X, Y) :- married(Y, X)",
            "father_in_law(F, P) :- married(P, S), male(F), parent(F, S)",
            "father_in_law(F, P) :- married(S, P), male(F), parent(F, S)",
            "mother_in_law(M, P) :- married(P, S), female(M), parent(M, S)",
            "mother_in_law(M, P) :- married(S, P), female(M), parent(M, S)",
            "parent_in_law(P, X) :- father_in_law(P, X)",
            "parent_in_law(P, X) :- mother_in_law(P, X)",
            "brother_in_law(B, P) :- spouse(P, S), male(B), sibling(B,S)",
            "sister_in_law(Si, P) :- spouse(P, S), female(Si), sibling(Si,S)",
            "same_city(P1, P2) :- city(P1, C), city(P2, C)",
            "same_profession(P1, P2) :- profession(P1, Job), profession(P2, Job)",
            "father_of_son(F, S) :- father(F, S), male(S)",
            "father_of_daughter(F, D) :- father(F, D), female(D)",
            "mother_of_son(M, S) :- mother(M, S), male(S)",
            "mother_of_daughter(M, D) :- mother(M, D), female(D)",
        ]

        # ── String handling: parse fact strings from file ─────────────────────
        parsed_facts = []
        for fact_str in dynamic_facts:
            clean = fact_str.rstrip(".")          # remove trailing dot
            clean = re.sub(r"\s+", " ", clean)    # normalise whitespace
            clean = clean.replace(", ", ",")       # remove space after comma for pytholog
            parsed_facts.append(clean)

        # Pytholog 2.4.1 does not reliably eliminate equal bindings with neq.
        # Materialize the two inequality-sensitive relations from finite facts.
        parents = {}
        for fact in parsed_facts:
            match = re.fullmatch(r"parent\(([a-z0-9_]+),([a-z0-9_]+)\)", fact)
            if match:
                parents.setdefault(match[1], set()).add(match[2])
        siblings = {(a, b) for children in parents.values()
                    for a in children for b in children if a != b}
        cousins = {(a, b) for p1, p2 in siblings
                   for a in parents.get(p1, ()) for b in parents.get(p2, ()) if a != b}
        rules = [rule for rule in rules if not rule.startswith(("sibling(", "cousin("))]
        derived = [f"sibling({a},{b})" for a,b in sorted(siblings)]
        derived += [f"cousin({a},{b})" for a,b in sorted(cousins)]
        all_entries = parsed_facts + derived + rules
        if all_entries:
            self.kb(all_entries)

        # Build DOB dict for age calculations (pure Python)
        self._dob = {}
        for fact_str in dynamic_facts:
            if fact_str.startswith("dob("):
                # String handling: extract name and year
                inner = fact_str[4:].rstrip(").")
                parts = inner.split(",")
                if len(parts) == 2:
                    name = parts[0].strip()
                    year = parts[1].strip()
                    try:
                        self._dob[name] = int(year)
                    except ValueError:
                        pass

    def reload(self):
        """Reload KB after new facts have been saved."""
        self._load_kb()
        return "Knowledge base reloaded with latest facts."

    def query(self, expr: str):
        try:
            result = self.kb.query(pl.Expr(expr)) or []
            return [] if result == ["No"] else result
        except Exception:
            return []

    def _age_of(self, person):
        yr = self._dob.get(person.lower())
        return self._CURRENT_YEAR - yr if yr else None

    def _older_than(self, p1, p2):
        yr1 = self._dob.get(p1.lower())
        yr2 = self._dob.get(p2.lower())
        if yr1 and yr2:
            return yr1 < yr2
        return None

    def _same_city(self, person):
        res = self.query(f"city({person.lower()},X)")
        names = _names(res)
        if not names:
            return []
        target = names[0].lower()
        all_res = self.query("city(X,Y)")
        return [r["X"].capitalize() for r in _unique(all_res)
                if r.get("Y", "").lower() == target
                and r.get("X", "").lower() != person.lower()]

    def _relationship_answer(self, relation: str, person: str) -> str:
        p = person.lower().strip()
        r = relation.lower().strip()

        if r == "dob":
            yr = self._dob.get(p)
            if yr:
                return f"{person.capitalize()} was born in {yr}."
            return f"I don't have the date of birth for {person.capitalize()}."

        if r == "age":
            age = self._age_of(p)
            if age is not None:
                return f"{person.capitalize()} is {age} years old."
            return f"I don't have age info for {person.capitalize()}."

        if r == "city":
            res   = self.query(f"city({p},X)")
            names = _names(res)
            if names:
                return f"{person.capitalize()} lives in {names[0].capitalize()}."
            return f"I don't know where {person.capitalize()} lives."

        if r == "same_city":
            same = self._same_city(p)
            if same:
                return f"People in the same city as {person.capitalize()}: {_fmt(same)}."
            return f"No one else is in the same city as {person.capitalize()}."

        if r == "profession":
            res   = self.query(f"profession({p},X)")
            names = _names(res)
            if names:
                return f"{person.capitalize()} is a {names[0]}."
            return f"I don't know the profession of {person.capitalize()}."

        if r == "male" and person == "all":
            res   = self.query("male(X)")
            names = _names(res)
            return f"All males: {_fmt(names)}." if names else "No males found."

        if r == "female" and person == "all":
            res   = self.query("female(X)")
            names = _names(res)
            return f"All females: {_fmt(names)}." if names else "No females found."

        if r == "married" and person == "all":
            res   = _unique(self.query("married(X,Y)"))
            pairs = [(d["X"].capitalize(), d["Y"].capitalize())
                     for d in res if "X" in d and "Y" in d]
            if pairs:
                return "Married couples: " + "; ".join(f"{a} & {b}" for a, b in pairs) + "."
            return "No married couples found."

        single_map = {
            "father":         (f"father(X,{p})",          "X", f"the father of {person.capitalize()}"),
            "mother":         (f"mother(X,{p})",          "X", f"the mother of {person.capitalize()}"),
            "son":            (f"son(X,{p})",             "X", f"the sons of {person.capitalize()}"),
            "grandparent":    (f"grandparent(X,{p})",     "X", f"the grandparents of {person.capitalize()}"),
            "grandfather":    (f"grandfather(X,{p})",     "X", f"the grandfather of {person.capitalize()}"),
            "grandmother":    (f"grandmother(X,{p})",     "X", f"the grandmother of {person.capitalize()}"),
            "great_grandparent": (f"great_grandparent(X,{p})", "X", f"the great grandparents of {person.capitalize()}"),
            "uncle":          (f"uncle(X,{p})",           "X", f"the uncles of {person.capitalize()}"),
            "aunt":           (f"aunt(X,{p})",            "X", f"the aunts of {person.capitalize()}"),
            "ancestor":       (f"ancestor(X,{p})",        "X", f"the ancestors of {person.capitalize()}"),
            "spouse":         (f"spouse(X,{p})",          "X", f"the spouse of {person.capitalize()}"),
            "father_in_law":  (f"father_in_law(X,{p})",  "X", f"the father-in-law of {person.capitalize()}"),
            "mother_in_law":  (f"mother_in_law(X,{p})",  "X", f"the mother-in-law of {person.capitalize()}"),
            "brother_in_law": (f"brother_in_law(X,{p})", "X", f"the brother-in-law of {person.capitalize()}"),
            "sister_in_law":  (f"sister_in_law(X,{p})",  "X", f"the sister-in-law of {person.capitalize()}"),
            "grandchild":     (f"grandchild(X,{p})",     "X", f"the grandchildren of {person.capitalize()}"),
            "grandson":       (f"grandson(X,{p})",       "X", f"the grandsons of {person.capitalize()}"),
            "granddaughter":  (f"granddaughter(X,{p})",  "X", f"the granddaughters of {person.capitalize()}"),
        }

        if r == "child":
            sons = _names(self.query(f"son(X,{p})"))
            daus = _names(self.query(f"daughter(X,{p})"))
            all_children = list(dict.fromkeys(sons + daus))
            if all_children:
                return f"The children of {person.capitalize()}: {_fmt(all_children)}."
            return f"No children found for {person.capitalize()}."

        if r == "sibling":
            parents_of_p = _names(self.query(f"parent(X,{p})"))
            siblings = []
            for par in [x.lower() for x in parents_of_p]:
                ch = _names(self.query(f"parent({par},X)"))
                siblings.extend(ch)
            siblings = list(dict.fromkeys([s for s in siblings if s.lower() != p]))
            if siblings:
                return f"Siblings of {person.capitalize()}: {_fmt(siblings)}."
            return f"No siblings found for {person.capitalize()}."

        if r == "brother":
            parents_of_p = _names(self.query(f"parent(X,{p})"))
            brothers = []
            for par in [x.lower() for x in parents_of_p]:
                ch = _names(self.query(f"son(X,{par})"))
                brothers.extend(ch)
            brothers = list(dict.fromkeys([b for b in brothers if b.lower() != p]))
            if brothers:
                return f"Brothers of {person.capitalize()}: {_fmt(brothers)}."
            return f"No brothers found for {person.capitalize()}."

        if r == "sister":
            parents_of_p = _names(self.query(f"parent(X,{p})"))
            sisters = []
            for par in [x.lower() for x in parents_of_p]:
                ch = _names(self.query(f"daughter(X,{par})"))
                sisters.extend(ch)
            sisters = list(dict.fromkeys([s for s in sisters if s.lower() != p]))
            if sisters:
                return f"Sisters of {person.capitalize()}: {_fmt(sisters)}."
            return f"No sisters found for {person.capitalize()}."

        if r == "cousin":
            parents_of_p = _names(self.query(f"parent(X,{p})"))
            cousins = []
            for par in [x.lower() for x in parents_of_p]:
                gps = _names(self.query(f"parent(X,{par})"))
                for gp in [x.lower() for x in gps]:
                    par_siblings = _names(self.query(f"parent({gp},X)"))
                    for ps in [x.lower() for x in par_siblings]:
                        if ps != par:
                            cuz = _names(self.query(f"son(X,{ps})")) + _names(self.query(f"daughter(X,{ps})"))
                            cousins.extend(cuz)
            cousins = list(dict.fromkeys([c for c in cousins if c.lower() != p]))
            if cousins:
                return f"Cousins of {person.capitalize()}: {_fmt(cousins)}."
            return f"No cousins found for {person.capitalize()}."

        if r in single_map:
            expr, var, label = single_map[r]
            res   = self.query(expr)
            names = _names(res, var)
            if names:
                verb = "is" if len(names) == 1 else "are"
                return f"{_fmt(names)} {verb} {label}."
            return f"Could not find {label}."

        return "I'm not sure how to answer that. Please rephrase."

    def _yesno_answer(self, relation: str, p1: str, p2: str = None) -> str:
        r = relation.lower().strip()
        a = p1.lower().strip()
        b = p2.lower().strip() if p2 else None
        label = r.replace("_", " ")

        if r == "older_than":
            result = self._older_than(a, b)
            if result is True:
                return f"Yes, {p1.capitalize()} is older than {p2.capitalize()}."
            elif result is False:
                return f"No, {p1.capitalize()} is not older than {p2.capitalize()}."
            return "I don't have enough info to compare their ages."

        if r == "is_married":
            res   = self.query(f"spouse(X,{a})")
            found = bool(res)
            if found:
                return f"Yes, {p1.capitalize()} is married."
            return f"No, {p1.capitalize()} is not married."

        if r == "married" and b:
            res1  = self.query(f"spouse({a},{b})")
            res2  = self.query(f"spouse({b},{a})")
            found = bool(res1) or bool(res2)
            if found:
                return f"Yes, {p1.capitalize()} and {p2.capitalize()} are married."
            return f"No, {p1.capitalize()} and {p2.capitalize()} are not married."

        if r == "sibling" and b:
            if a == b:
                return f"No, {p1.capitalize()} and {p2.capitalize()} are not siblings."
            parents_a = set(_names(self.query(f"parent(X,{a})")))
            parents_b = set(_names(self.query(f"parent(X,{b})")))
            if parents_a & parents_b:
                return f"Yes, {p1.capitalize()} and {p2.capitalize()} are siblings."
            return f"No, {p1.capitalize()} and {p2.capitalize()} are not siblings."

        if r in {"brother", "sister"} and b:
            if a == b:
                return f"No, {p1.capitalize()} is not {label} of {p2.capitalize()}."
            found = bool(self.query(f"{r}({a},{b})"))
            if found:
                return f"Yes, {p1.capitalize()} is {label} of {p2.capitalize()}."
            return f"No, {p1.capitalize()} is not {label} of {p2.capitalize()}."

        two_arg = {
            "father":      f"father({a},{b})",
            "mother":      f"mother({a},{b})",
            "grandparent": f"grandparent({a},{b})",
            "grandfather": f"grandfather({a},{b})",
            "grandmother": f"grandmother({a},{b})",
            "ancestor":    f"ancestor({a},{b})",
            "uncle":       f"uncle({a},{b})",
            "aunt":        f"aunt({a},{b})",
        }

        if r in two_arg and b:
            res   = self.query(two_arg[r])
            found = bool(res)
            if found:
                return f"Yes, {p1.capitalize()} is {label} of {p2.capitalize()}."
            return f"No, {p1.capitalize()} is not {label} of {p2.capitalize()}."

        return "Could not verify that relationship."

    def ask(self, user_input: str) -> str:
        clean    = re.sub(r"[?!.,]", "", user_input).upper().strip()
        response = self.kernel.respond(clean).strip()

        if response.startswith("QUERY:"):
            parts    = response.split(":")
            relation = parts[1] if len(parts) > 1 else ""
            person   = parts[2].lower() if len(parts) > 2 else ""
            return self._relationship_answer(relation, person)

        if response.startswith("YESNO:"):
            parts    = response.split(":")
            relation = parts[1] if len(parts) > 1 else ""
            p1       = parts[2].lower() if len(parts) > 2 else ""
            p2       = parts[3].lower() if len(parts) > 3 else None
            return self._yesno_answer(relation, p1, p2)

        return response if response else "I did not understand. Please try again."


# ═══════════════════════════════════════════════════════════════
# COMBINED AGENT  — wraps both modes in one class
# ═══════════════════════════════════════════════════════════════

class FamilyKnowledgeAgent:
    """
    Unified agent exposing both input and query modes.
    Used by the notebook and Flask app.
    """

    def __init__(self):
        self.input_agent = InputAgent()
        self.query_agent = QueryAgent()

    def ask_input(self, user_input: str) -> str:
        """Add facts via natural language."""
        response = self.input_agent.ask(user_input)
        if response.startswith("Saved ") or response.startswith("All dynamic facts cleared"):
            self.query_agent.reload()
        return response

    def ask(self, user_input: str) -> str:
        """Query the KB via natural language."""
        return self.query_agent.ask(user_input)

    def reload(self) -> str:
        """Reload query agent after new facts are saved."""
        return self.query_agent.reload()


# ═══════════════════════════════════════════════════════════════
# CONSOLE CHAT  — interactive demo of both modes
# ═══════════════════════════════════════════════════════════════

def run_console_chat():
    print("=" * 55)
    print("  KRR project 2 — Family Knowledge Base Chatbot")
    print("=" * 55)

    agent = FamilyKnowledgeAgent()

    print("\n📥  MODE 1: ADD FACTS")
    print("    Add family members to the knowledge base.")
    print("    Type 'done' when finished adding.\n")

    while True:
        try:
            user = input("You (add): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user.lower() in {"done", "exit", "quit"}:
            break
        resp = agent.ask_input(user)
        print(f"Bot: {resp}\n")

    # Save any remaining pending facts
    if agent.input_agent._pending:
        print(f"Bot: {agent.input_agent._save_all()}\n")

    # Reload query agent with newly saved facts
    print(agent.reload())

    print("\n🔍  MODE 2: QUERY FACTS")
    print("    Ask questions about the family.")
    print("    Type 'exit' to quit.\n")

    while True:
        try:
            user = input("You (query): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit", "bye"}:
            print("Bot: Goodbye!")
            break
        print(f"Bot: {agent.ask(user)}\n")


if __name__ == "__main__":
    run_console_chat()
