% ==========================================
% FAMILY KNOWLEDGE BASE - RULES ONLY
% KRR project 2 - Muhammad Imad
% Facts are added dynamically via chatbot
% ==========================================

% ==========================================
% RULES (30+)
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

% Rule 6: Sibling
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

% Rule 16: Uncle
uncle(U, P) :-
    brother(U, Par),
    parent(Par, P).

% Rule 17: Aunt
aunt(A, P) :-
    sister(A, Par),
    parent(Par, P).

% Rule 18: Cousin
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

% Rule 21: Spouse
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

% Rule 27: Same city
same_city(P1, P2) :-
    city(P1, C),
    city(P2, C),
    P1 \= P2.

% Rule 28: Same profession
same_profession(P1, P2) :-
    profession(P1, Job),
    profession(P2, Job),
    P1 \= P2.

% Rule 29: Father of son
father_of_son(F, S) :-
    father(F, S),
    male(S).

% Rule 30: Father of daughter
father_of_daughter(F, D) :-
    father(F, D),
    female(D).

% Rule 31: Mother of son
mother_of_son(M, S) :-
    mother(M, S),
    male(S).

% Rule 32: Mother of daughter
mother_of_daughter(M, D) :-
    mother(M, D),
    female(D).

% Rule 33: Is married check
is_married(X) :-
    spouse(X, _).

% ==========================================
% DYNAMIC FACTS SECTION
% Synthetic demo facts; no personal runtime data.
