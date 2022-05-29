from CNF import findSolution
from CNF import findVars
from CNF import clauseSplit

# Runs clause split only when the operation is present
# Operation would typically be "and" or "or"
def situationalClauseSplit(formula, operation):
   if len(formula) > 1 and formula[1] == operation[0]:
      return clauseSplit(formula[1:-1], findVars(formula))
   else:
      return {formula}

# Replaces an "or" clause with a set of each of the sub-clauses
def replaceOr(clauses):
   for i in range(len(clauses)):
      clause = clauses[i]
      clauses[i] = situationalClauseSplit(clause, "or")
   return clauses

# Makes sure that both groups of clauses are equivalent
# I'd rather just use a set and do set1 == set2, but a set of sets isn't allowed
# So instead we make do
# The two sets are my answer and the correct answer
def testSameClauses(setA, setB):
   listA = replaceOr(list(setA))
   listB = replaceOr(list(setB))

   if len(listA) != len(listB):
      return False

   for item in listA:
      if item not in listB:
         return False
   
   for item in listB:
      if item not in listA:
         return False
   
   return True

# Runs a single test
# Test is a tuple in the form (input formula, correct result formula)
def test(test, testNumber):
   answerClauses, answerFormula = findSolution(test[0])
   correctFormula = test[1]
   correctClauses = situationalClauseSplit(correctFormula, "and")
   if testSameClauses(answerClauses, correctClauses):
      print("Test", testNumber, test[0], "passed")
   else:
      print("Test", testNumber, test[0], "failed:")
      print("    Student formula was:", answerFormula)
      print("    Correct formula was:", test[1])
      # print("    Student clauses were:", answerClauses)
      # print("    Correct clauses were:", correctClauses)

def runTests():
   # Each element in the list is in the form (input formula, correct result formula)
   tests = [("(implies p q)", "(or (not p) q)"), 
            ("(not (and p q (not r)))", "(or (not p) (not q) r)"), 
            ("(not (implies p (and q r)))", "(and p (or (not q) (not r)))"), 
            ("(or (and p (not q)) (and r s))", "(and (or p r) (or p s) (or (not q) r) (or (not q) s))"), 
            ("(or p (or r (not s)))", "(or p r (not s))"), 
            ("(and (not p) (and q r) s)", "(and (not p) q r s)")]

   for i in range(len(tests)):
      test(tests[i], i+1)


def main():
   runTests()

main()