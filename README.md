# Automatically Test CNF Converter
The goal here was to automate testing an assignment of mine

## About the assignment
The assignment was to convert a formula into the [conjunctive normal form (CNF)](https://en.wikipedia.org/wiki/Conjunctive_normal_form), "ands of ors", then split it into its separate clauses to prepare for a proof by resolution.
This presented a few challenges, as not only could the clauses be in any order, but any for any clause that is an "or" statement, *its* clauses could also be in any order and still be a valid answer.

Additionally, the format of the input is something like `(implies (and (not p) q) (not (or r s)))`, which makes the whole thing into a lovely exercise in parsing strings. Luckily, some of these functions could be reused by my testing program.

## Next steps/improvements
- [ ] Be able to run more intensive tests of a specific type (e.g. run a group of tests dealing with different variations of nested or statements) with some command line argument (maybe use optparse?)
