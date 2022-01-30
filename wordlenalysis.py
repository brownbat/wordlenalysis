import os, sys

FN_SOLVE = "wordle_solutions_alphabetized.txt"
FN_GUESS = "wordle_complete_dictionary.txt"
abspath = os.path.abspath(sys.argv[0])
DIRNAME = os.path.dirname(abspath)
os.chdir(DIRNAME)

" ☆★"
"□▤▦"
"□▧▩"
RESULTS = "□▣■"
GRAY, YELLOW, GREEN = list(RESULTS)


def gen_solutions():
    with open(FN_SOLVE, 'r') as SOLUTIONS:
        for solution in SOLUTIONS.readlines():
            yield solution.strip()

def gen_guesses():
    with open(FN_GUESS, 'r') as GUESSES:
        for guess in GUESSES.readlines():
            yield guess.strip()


def compare(sol, guess):
    assert type(guess) == type(sol) == str
    assert len(guess) == len(sol) == 5
    guess = guess.upper()
    sol = sol.upper()
    out_str = list("     ")
    unclaimed = list(sol)
    for i in range(len(guess)):
        if guess[i] == sol[i]:
            out_str[i] = GREEN
            try:
                unclaimed.pop(unclaimed.index(guess[i]))
            except:
                # ugly error handling here
                print('ERROR')
                print('sol:',sol)
                print('guess:',guess)
                print('unclaimed:',unclaimed)
                print('i:',i)
                print('ERROR')
                exit()
    for i in range(len(guess)):
        if guess[i] != sol[i]:
            if guess[i] in unclaimed:
                out_str[i] = YELLOW
                unclaimed.pop(unclaimed.index(guess[i]))
            else:
                assert guess[i] not in unclaimed
                out_str[i] = GRAY
    out_str = ''.join(out_str)
    assert len(out_str) == 5
    return out_str

def test_compare():
    # need more tests.
    # i think abbba,bacon is testing lookahead, but could use more
    tests = [
                ["HELIX", "hello", GREEN * 3 + GRAY * 2],
                ["AAAAA", "BBBBB", GRAY * 5],
                ["AaAAA", "aAaAa", GREEN * 5],
                ["hello", "helix", GREEN * 3 + GRAY * 2],
                ["hello", "locus", YELLOW * 2 + GRAY * 3],
                ["aaaaa", "bacon", GRAY + GREEN + GRAY * 3],
                ["bacon", "aaaaa", GRAY + GREEN + GRAY * 3],
                ["abbba", "bacon", YELLOW * 2 + GRAY * 3],
                ["bacon", "abbba", YELLOW * 2 + GRAY * 3],
                ["a", "a", None]
            ]

    for t in tests:
        try:
            if compare(t[0],t[1]) == t[2]:
                print("PASS")
            else:
                print(t[0])
                print(t[1])
                print(compare(t[0], t[1]))
                print(t[2])
                print("FAIL")
        except AssertionError:
            if t[2] == None:
                print("PASS")
            else:
                print("FAIL")


def all_patterns(guess):
    patterns = {}
    for sol in gen_solutions():
        p = compare(sol, guess)
        patterns[p] = patterns.get(p, 0) + 1
    return patterns
        

def guess_to_hint_counts(guess):
    hints = all_patterns(guess)
    return sorted(hints.items(), key=lambda x:x[1], reverse=True)

def guess_to_largest_bucket_size(guess):
    return guess_to_hint_counts(guess)[0][1]

def guess_to_num_buckets(guess):
    return len(guess_to_hint_counts(guess))
    
records = {}
MOST_BUCKETS = 0
LEAST_BUCKETS = 1
LARGEST_LARGEST_BUCKET = 2
SMALLEST_LARGEST_BUCKET = 3
records[MOST_BUCKETS] = ("XXXXX", 0)
records[LEAST_BUCKETS] = ("XXXXX", 999999)
records[LARGEST_LARGEST_BUCKET] = ("XXXXX", 0)
records[SMALLEST_LARGEST_BUCKET] = ("XXXXX", 999999)

for guess in gen_guesses():
    hints = guess_to_hint_counts(guess)
    num_buckets = guess_to_num_buckets(guess)
    largest_bucket_size = guess_to_largest_bucket_size(guess)
    if num_buckets > records[MOST_BUCKETS][1]:
        records[MOST_BUCKETS] = (guess, num_buckets)
        print(records)
    if num_buckets < records[LEAST_BUCKETS][1]:
        records[LEAST_BUCKETS] = (guess, num_buckets)
        print(records)
    if largest_bucket_size > records[LARGEST_LARGEST_BUCKET][1]:
        records[LARGEST_LARGEST_BUCKET] = (guess, largest_bucket_size)
        print(records)
    if largest_bucket_size < records[SMALLEST_LARGEST_BUCKET][1]:
        records[SMALLEST_LARGEST_BUCKET] = (guess, largest_bucket_size)
        print(records)
    
print(records)




