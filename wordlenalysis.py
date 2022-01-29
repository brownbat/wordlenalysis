import os, sys

FN_SOLVE = "wordle_solutions_alphabetized.txt"
FN_GUESS = "wordle_complete_dictionary.txt"
abspath = os.path.abspath(sys.argv[0])
DIRNAME = os.path.dirname(abspath)
os.chdir(DIRNAME)

YELLOW = "/"
GREEN = "*"
GRAY = "_"

def gen_solutions():
    with open(FN_SOLVE, 'r') as SOLUTIONS:
        for solution in SOLUTIONS.readlines():
            yield solution.strip()

def gen_guesses():
    with open(FN_GUESS, 'r') as GUESSES:
        for guess in GUESSES.readlines():
            yield guess.strip()


def compare(guess, sol):
    assert type(guess) == type(sol) == str
    assert len(guess) == len(sol) == 5
    guess = guess.upper()
    sol = sol.upper()
    out_str = ""
    unclaimed = list(sol)
    for i in range(len(guess)):
        if guess[i] == sol[i]:
            out_str += GREEN
            unclaimed.pop(unclaimed.index(guess[i]))
        elif guess[i] in unclaimed:
            out_str += YELLOW
            unclaimed.pop(unclaimed.index(guess[i]))
        else:
            assert guess[i] not in unclaimed
            out_str += GRAY
    assert len(out_str) == 5
    return out_str

def test_compare():
    tests = [
                ["hello", "HELIX", GREEN * 3 + GRAY * 2],
                ["AAAAA", "BBBBB", GRAY * 5],
                ["aAaAa", "AaAAA", GREEN * 5],
                ["helix", "hello", GREEN * 3 + GRAY * 2],
                ["locus", "hello", YELLOW * 2 + GRAY * 3],
                ["a", "a", None]
            ]

    for t in tests:
        try:
            if compare(t[0],t[1]) == t[2]:
                print("PASS")
            else:
                print("FAIL")
        except AssertionError:
            if t[2] == None:
                print("PASS")
            else:
                print("FAIL")


def gen_all_patterns(guess):
    for sol in gen_solutions():
        print(sol)
        yield compare(guess, sol)

for guess in gen_guesses():
    for p in gen_all_patterns(guess):
        print(guess)
        print(p)
        input()
