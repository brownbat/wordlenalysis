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


def compare(sol, guess):
    # breaks on BACON,AAAAA
    assert type(guess) == type(sol) == str
    assert len(guess) == len(sol) == 5
    guess = guess.upper()
    sol = sol.upper()
    out_str = ""
    unclaimed = list(sol)
    for i in range(len(guess)):
        if guess[i] == sol[i]:
            out_str += GREEN
            try:
                unclaimed.pop(unclaimed.index(guess[i]))
            except:
                print('ERROR')
                print('sol:',sol)
                print('guess:',guess)
                print('unclaimed:',unclaimed)
                print('i:',i)
                print('ERROR')
                exit()
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
                ["HELIX", "hello", GREEN * 3 + GRAY * 2],
                ["AAAAA", "BBBBB", GRAY * 5],
                ["AaAAA", "aAaAa", GREEN * 5],
                ["hello", "helix", GREEN * 3 + GRAY * 2],
                ["hello", "locus", YELLOW * 2 + GRAY * 3],
                ["aaaaa", "bacon", GRAY + GREEN + GRAY * 3],
                ["bacon", "aaaaa", GREEN + GRAY * 4],
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


test_compare()
exit()

def all_patterns(guess):
    patterns = {}
    for sol in gen_solutions():
        p = compare(sol, guess)
        patterns[p] = patterns.get(p, 0) + 1
    return patterns
        

for guess in gen_guesses():
    print(all_patterns(guess))
    input()
    
