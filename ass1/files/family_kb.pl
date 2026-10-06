% ==========================================
% FAMILY KNOWLEDGE BASE
% KRR Assignment - Muhammad Imad
% ==========================================

% ==========================================
% 1. FACTS: Gender
% ==========================================
male(tariq).
male(kamran).
male(ali).
male(usman).
male(omar).
male(hassan).
male(adam).
female(sara).
female(fatima).
female(alia).
female(noor).
female(zara).

% ==========================================
% 2. FACTS: Parentage (parent(Parent, Child))
% ==========================================
parent(tariq, kamran).
parent(tariq, ali).
parent(tariq, usman).
parent(sara, kamran).
parent(sara, ali).
parent(sara, usman).
parent(ali, omar).
parent(ali, alia).
parent(fatima, omar).
parent(fatima, alia).
parent(kamran, hassan).
parent(kamran, adam).
parent(noor, adam).

% ==========================================
% 3. FACTS: Marriage (married(Person1, Person2))
% ==========================================
married(tariq, sara).
married(ali, fatima).
married(kamran, noor).
married(omar, zara).

% ==========================================
% 4. FACTS: Date of Birth (dob(Person, Year))
% ==========================================
dob(tariq, 1950).
dob(sara, 1953).
dob(kamran, 1975).
dob(ali, 1978).
dob(usman, 1983).
dob(fatima, 1980).
dob(noor, 1977).
dob(omar, 2003).
dob(alia, 2006).
dob(hassan, 2000).
dob(adam, 2005).
dob(zara, 2002).

% ==========================================
% 5. FACTS: City (city(Person, City))
% ==========================================
city(tariq, lahore).
city(sara, lahore).
city(kamran, karachi).
city(ali, lahore).
city(usman, islamabad).
city(fatima, lahore).
city(noor, karachi).
city(omar, lahore).
city(alia, lahore).
city(hassan, karachi).
city(adam, karachi).
city(zara, lahore).

% ==========================================
% 6. FACTS: Profession (profession(Person, Job))
% ==========================================
profession(tariq, retired).
profession(sara, teacher).
profession(kamran, engineer).
profession(ali, doctor).
profession(usman, banker).
profession(fatima, lawyer).
profession(noor, architect).
profession(omar, student).
profession(alia, student).
profession(hassan, student).
profession(adam, student).
profession(zara, designer).

% ==========================================
% 7. RULES: Core Relationship Rules (30+)
% ==========================================

% Rule 1: Father
father(F, C) :-
    male(F),
    parent(F, C).

% Rule 2: Mother
mother(M, C) :-
    female(M),
    parent(M, C).

% Rule 3: Child
child(C, P) :-
    parent(P, C).

% Rule 4: Son
son(S, P) :-
    male(S),
    parent(P, S).

% Rule 5: Daughter
daughter(D, P) :-
    female(D),
    parent(P, D).

% Rule 6: Sibling (share at least one parent)
sibling(A, B) :-
    parent(P, A),
    parent(P, B),
    A \= B.

% Rule 7: Brother
brother(B, P) :-
    male(B),
    sibling(B, P).

% Rule 8: Sister
sister(S, P) :-
    female(S),
    sibling(S, P).

% Rule 9: Grandparent
grandparent(G, C) :-
    parent(G, P),
    parent(P, C).

% Rule 10: Grandfather
grandfather(G, C) :-
    male(G),
    grandparent(G, C).

% Rule 11: Grandmother
grandmother(G, C) :-
    female(G),
    grandparent(G, C).

% Rule 12: Grandchild
grandchild(C, G) :-
    grandparent(G, C).

% Rule 13: Grandson
grandson(C, G) :-
    male(C),
    grandparent(G, C).

% Rule 14: Granddaughter
granddaughter(C, G) :-
    female(C),
    grandparent(G, C).

% Rule 15: Great Grandparent
great_grandparent(G, C) :-
    parent(G, P),
    grandparent(P, C).

% Rule 16: Uncle (parent's brother)
uncle(U, P) :-
    brother(U, Par),
    parent(Par, P).

% Rule 17: Aunt (parent's sister)
aunt(A, P) :-
    sister(A, Par),
    parent(Par, P).

% Rule 18: Cousin (uncle/aunt's child)
cousin(C1, C2) :-
    parent(P1, C1),
    parent(P2, C2),
    sibling(P1, P2),
    C1 \= C2.

% Rule 19: Ancestor (recursive)
ancestor(A, C) :-
    parent(A, C).
ancestor(A, C) :-
    parent(A, P),
    ancestor(P, C).

% Rule 20: Descendant
descendant(D, A) :-
    ancestor(A, D).

% Rule 21: Spouse (married to each other)
spouse(X, Y) :- married(X, Y).
spouse(X, Y) :- married(Y, X).

% Rule 22: Father-in-law
father_in_law(F, P) :-
    spouse(P, S),
    father(F, S).

% Rule 23: Mother-in-law
mother_in_law(M, P) :-
    spouse(P, S),
    mother(M, S).

% Rule 24: Parent-in-law
parent_in_law(P, X) :-
    father_in_law(P, X).
parent_in_law(P, X) :-
    mother_in_law(P, X).

% Rule 25: Brother-in-law
brother_in_law(B, P) :-
    spouse(P, S),
    brother(B, S).

% Rule 26: Sister-in-law
sister_in_law(Si, P) :-
    spouse(P, S),
    sister(Si, S).

% Rule 27: Age calculation
age(Person, Age) :-
    dob(Person, BirthYear),
    Age is 2026 - BirthYear.

% Rule 28: Older than
older_than(P1, P2) :-
    dob(P1, Y1),
    dob(P2, Y2),
    Y1 < Y2.

% Rule 29: Same city
same_city(P1, P2) :-
    city(P1, C),
    city(P2, C),
    P1 \= P2.

% Rule 30: Same profession
same_profession(P1, P2) :-
    profession(P1, Job),
    profession(P2, Job),
    P1 \= P2.

% Rule 31: Father of son
father_of_son(F, S) :-
    father(F, S),
    male(S).

% Rule 32: Father of daughter
father_of_daughter(F, D) :-
    father(F, D),
    female(D).

% Rule 33: Mother of son
mother_of_son(M, S) :-
    mother(M, S),
    male(S).

% Rule 34: Mother of daughter
mother_of_daughter(M, D) :-
    mother(M, D),
    female(D).

% Rule 35: Nuclear family (share both parents)
nuclear_family(X, Y) :-
    parent(P1, X),
    parent(P2, X),
    parent(P1, Y),
    parent(P2, Y),
    X \= Y,
    P1 \= P2.

% Rule 36: Is married (check if person is married)
is_married(X) :-
    spouse(X, _).
