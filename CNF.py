# By Kaih White and Linnea Walsh
# Project 3

import re
import os

# reads in file
def read(name):
    file = open(name)
    obj = file.readline()

    return obj, findVars(obj)

# finds variables in formula
def findVars(formula):
    noSpace = formula.replace(")","").split(" ")

    variableSet = set()

    for item in noSpace:
        if len(item) == 1:
            variableSet.add(item)

    variables = list(variableSet)
    variables.sort()
    return variables
    
# Converts implies operator
def removeImplies(formula, vars):
    startingIndex = formula.find("implies")
    endingIndex = -1

    while startingIndex != -1:

        params = []

        i = startingIndex + 7
        while i < len(formula):

            if(formula[i] == "("):
                parenthesisCount = 0

                for j in range(i+1, len(formula)):

                    if formula[j] == ")":
                        if parenthesisCount == 0:
                            params.append(formula[i:j+1])
                            i = j + 1
                            endingIndex = j
                            break

                        parenthesisCount -= 1

            elif formula[i] in vars:
                if formula[i-1] == " ":
                    if formula[i+1] == " " or formula[i+1] == ")":
                        params.append(formula[i])
                        endingIndex = i

            if len(params) > 1:
                break

            i += 1

        replacer = "or (not {}) {}".format(params[0], params[1])
        formula = formula[0:startingIndex] + replacer + formula[endingIndex + 1:]

        startingIndex = formula.find("implies")

    return formula

# Converts iff operator
def removeBiconditional(formula, vars):
    startingIndex = formula.find("iff")
    endingIndex = -1

    while startingIndex != -1:

        params = []

        i = startingIndex + 3
        while i < len(formula):

            if (formula[i] == "("):
                parenthesisCount = 0

                for j in range(i + 1, len(formula)):

                    if formula[j] == ")":
                        if parenthesisCount == 0:
                            params.append(formula[i:j + 1])
                            i = j + 1
                            endingIndex = j
                            break

                        parenthesisCount -= 1

            elif formula[i] in vars:
                if formula[i - 1] == " ":
                    if formula[i + 1] == " " or formula[i + 1] == ")":
                        params.append(formula[i])
                        endingIndex = i

            if len(params) > 1:
                break

            i += 1

        replacer = "and (implies {0} {1}) (implies {1} {0})".format(params[0], params[1])
        formula = formula[0:startingIndex] + replacer + formula[endingIndex + 1:]

        startingIndex = formula.find("iff")

    return formula

# Splits a string formula into its separate clauses
def clauseSplit(formula, vars):
    cList = set()

    i = 0

    while i < len(formula):

        if (formula[i] == "("):
            parenthesisCount = 0

            for j in range(i + 1, len(formula)):
                if formula[j] == "(":
                    parenthesisCount += 1
                elif formula[j] == ")":
                    if parenthesisCount == 0:
                        cList.add(formula[i:j + 1])
                        i = j + 1
                        break

                    parenthesisCount -= 1

        elif formula[i] in vars:
            if formula[i - 1] == " ":
                if i == len(formula) - 1 or formula[i + 1] == " " or formula[i + 1] == ")":
                    cList.add(formula[i])

        i += 1

    return cList

# "not" operator
def knot(clause, vars):
    if len(clause) < 2:
        return "(not " + clause + ")"

    if clause[0] == "(":
        clause = clause[1:-1]


    if clause[0] == "a":
        clauses = clauseSplit(clause, vars)
        output = "(or"
        for c in clauses:
            output += " " + knot(c, vars)
        output += ")"
        return output
    elif clause[0] == "o":
        clauses = clauseSplit(clause, vars)
        output = "(and"
        for c in clauses:
            output += " " + knot(c, vars)
        output += ")"
        return output
    elif clause[0] == "n":
        return clause[4:]
    else:
        return "Oops, something went wrong"

# Pushes a not inside parentheses
def notPusher(formula, vars):
    startingIndex = formula.find("not")

    finalFormula = ""

    while startingIndex != -1:

        finalFormula += formula[0:startingIndex - 1]

        currentPos = startingIndex
        parenthesisCount = 0

        while currentPos < len(formula):

            if formula[currentPos] == "(":

                parenthesisCount += 1

            if formula[currentPos] == ")":
                if parenthesisCount < 1:

                    finalFormula += knot(formula[startingIndex + 4 : currentPos], vars)
                    formula = formula[currentPos + 1 :]
                    break

                parenthesisCount -= 1

            currentPos += 1

        startingIndex = formula.find("not")

    return finalFormula + formula

# Distributes and over or
def distributeAnOr(formula):
    #takes in the whole '(or (and a b) (and c d))'
    split = clauseSplit(formula[4: -1], findVars(formula))
    clauses = []

    for clause in split:
        if len(clause) == 1 or clause[1] == "n":
            clauses.append([clause])
        else:
            clauses.append(clauseSplit(clause[1:-1], findVars(clause)))
    return buildAnd(clauses)

# Helper for distributeAnOr, permutes the terms in the ands
def permuteTerms(clauses, count, vars):
    curr = clauses[count]
    continuedVars = []
    for variation in curr:
        newList = vars.copy()
        newList.append(variation)
        if count is len(clauses) - 1:
            continuedVars.append(newList)
        else:
            permutes = permuteTerms(clauses, count+1, newList)
            for thing in permutes:  
                continuedVars.append(thing)
    return continuedVars

# Helper for distributeAnOr, builds the resulting and statement
def buildAnd(clauses):
    orStatements = permuteTerms(clauses, 0, [])
    output = "(and"
    for statement in orStatements:
        orOutput = " (or"
        for term in statement:
            orOutput += " " + term
        orOutput += ")"
        output += orOutput
    output += ")"
    return output

# Finds all cases or Or And nests and modifies them
def OrAnd(formula):
    x = re.search("\(or(.*?)(\s\(and(\s([a-z]|\(.*?\)))+\))+(.*?)\)", formula)

    while x is not None:

        toReplace = distributeAnOr(x.group())

        formula = re.sub("\(or(.*?)(\s\(and(\s([a-z]|\(.*?\)))+\))+(.*?)\)", toReplace, formula, 1)

        x = re.search("\(or(.*?)(\s\(and(\s([a-z]|\(.*?\)))+\))+(.*?)\)", formula)

    return formula

# Finds nested Ors and removes them
def OrOr(formula):
    x = re.search("\(or ((([a-z]|\(and .*?\)|\(not [a-z]\))\s)*?)((\(or(\s([a-z]|\(not [a-z]\)))+\))\s?)+((\s?([a-z]|\(and .*?\)|\(not [a-z]\)))*?)\)", formula)

    while x is not None:

        outerOr = x.group(0)

        innerOr = re.search("\(or(\s([a-z]|\(not [a-z]\)))+\)", outerOr)

        vars = ""

        while innerOr is not None:

            endpoint = innerOr.span()[1]

            innerOrStr = innerOr.group()[4:-1]

            lpar = 1
            count = 0
            for c in innerOrStr:
                if lpar == 0:
                    vars += c
                if c == "(":
                    lpar = 0
                    vars += "("
                elif c == ")":
                    lpar = 1
                    if count < len(innerOrStr) - 1:
                        vars += " "
                elif c != " " and lpar == 1:
                    vars += c
                    if count < len(innerOrStr) - 1:
                        vars += " "
                count += 1


            outerOr = outerOr[endpoint:]
            innerOr = re.search("\(or(\s([a-z]|\(not [a-z]\)))+\)", outerOr)

            if innerOr is not None:
                vars += " "

        vars2 = x.group(1)

        if len(vars2) != 0:
            if vars2[len(vars2) - 1] == " ":
                vars2 = vars2[0:-1]
            if vars2[0] == " ":
                vars2 = vars2[1:]

        vars3 = x.group(8)

        if len(vars3) != 0:
            if vars3[len(vars3) - 1] == " ":
                vars3 = vars3[0:-1]
            if vars3[0] == " ":
                vars3 = vars[1:]

        toReplace = ""

        if vars is None:
            vars = ""
        if vars2 is None:
            vars2 = ""
        if vars3 is None:
            vars3 = ""

        addSpace = 0

        if len(vars) != 0:
            toReplace += vars
            addSpace = 1

        if len(vars2) != 0:
            if addSpace == 1:
                toReplace += " "
            toReplace += vars2

        if len(vars3) != 0:
            if addSpace == 1:
                toReplace += " "
            toReplace += vars3

        toReplace = "(or " + toReplace + ")"


        formula = re.sub("\(or (([a-z]|\(and .*?\)|\(not [a-z]\))\s)*?((\(or(\s([a-z]|\(not [a-z]\)))+\))\s?)+(\s?([a-z]|\(and .*?\)|\(not [a-z]\)))*?\)", toReplace, formula, 1)

        x = re.search("\(or (([a-z]|\(and .*?\)|\(not [a-z]\))\s)*?((\(or(\s([a-z]|\(not [a-z]\)))+\))\s?)+(\s?([a-z]|\(and .*?\)|\(not [a-z]\)))*?\)", formula)

    return formula

# Finds nested Ands and removes them
def AndAnd(formula):
    x = re.search("\(and ((([a-z]|\(or .*?\)|\(not [a-z]\))\s)*?)((\(and(\s([a-z]|\(not [a-z]\)))+\))\s?)+((\s?([a-z]|\(or .*?\)|\(not [a-z]\)))*?)\)", formula)

    while x is not None:

        outerAnd = x.group(0)

        innerAnd = re.search("\(and(\s([a-z]|\(not [a-z]\)))+\)", outerAnd)

        vars = ""

        while innerAnd is not None:

            endpoint = innerAnd.span()[1]

            innerAndStr = innerAnd.group()[4:-1]

            lpar = 1
            count = 0
            for c in innerAndStr:
                if lpar == 0:
                    vars += c
                if c == "(":
                    lpar = 0
                    vars += "("
                elif c == ")":
                    lpar = 1
                    if count < len(innerAndStr) - 1:
                        vars += " "
                elif c != " " and lpar == 1:
                    vars += c
                    if count <  len(innerAndStr) - 1:
                        vars += " "

            outerAnd = outerAnd[endpoint:]
            innerAnd = re.search("\(and(\s([a-z]|\(not [a-z]\)))+\)", outerAnd)

            if innerAnd is not None:
                vars += " "

        vars2 = ""
        vars3 = ""


        if x.group(1) is not None:
            vars2 = x.group(1)

            if len(vars2) != 0:
                if vars2[len(vars2) - 1] == " ":
                    vars2 = vars2[0:-1]
                if vars2[0] == " ":
                    vars2 = vars2[1:]

        if x.group(9) is not None:
            vars3 = x.group(9)

            if len(vars3) != 0:
                if vars3[len(vars3) - 1] == " ":
                    vars3 = vars3[0:-1]
                if vars3[0] == " ":
                    vars3 = vars[1:]

        toReplace = ""

        addSpace = 0

        if len(vars) != 0:
            toReplace += vars
            addSpace = 1

        if len(vars2) != 0:
            if addSpace == 1:
                toReplace += " "
            toReplace += vars2

        if len(vars3) != 0:
            if addSpace == 1:
                toReplace += " "
            toReplace += vars3


        toReplace = "(and " + toReplace + ")"


        formula = re.sub("\(and (([a-z]|\(or .*?\)|\(not [a-z]\))\s)*?((\(and(\s([a-z]|\(not [a-z]\)))+\))\s?)+(\s?([a-z]|\(or .*?\)|\(not [a-z]\)))*?\)", toReplace, formula, 1)


        x = re.search("\(and (([a-z]|\(or .*?\)|\(not [a-z]\))\s)*?((\(and(\s([a-z]|\(not [a-z]\)))+\))\s?)+(\s?([a-z]|\(or .*?\)|\(not [a-z]\)))*?\)", formula)

    return formula

# Turns formula into CNF form
def cnf(formula, vars):

    formula = removeBiconditional(formula, vars)

    formula = removeImplies(formula, vars)

    formula = notPusher(formula, vars)

    formula = OrAnd(formula)

    formula = OrOr(formula)

    formula = AndAnd(formula)

    return formula

def findSolution(formula):
    output = set()

    vars = findVars(formula)
    formula = cnf(formula, vars)

    if len(formula) > 1 and formula[1] == "a":
        for item in clauseSplit(formula[1:-1], vars):
            output.add(item)
    else:
        output.add(formula)
    
    return output, formula


def main():

    filename = input("Please enter the file to be read: ")

    formula, vars = read(filename)

    formula = cnf(formula, vars)

    filename = input("Please enter the file you want the clauses to be written to: ")

    if os.access(filename, os.F_OK):
        os.remove(filename)

    output  = open(filename, "a")

    if len(formula) > 1 and formula[1] == "a":
        for item in clauseSplit(formula[1:-1], vars):
            output.write(item)
            output.write("\n")
    else:
        output.write(formula)


if __name__ == "__main__":
    main()