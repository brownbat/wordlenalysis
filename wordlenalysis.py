import os
import sys

# TODO - find best second moves

FN_SOLVE = "wordle_solutions_alphabetized.txt"
FN_GUESS = "wordle_complete_dictionary.txt"
abspath = os.path.abspath(sys.argv[0])
DIRNAME = os.path.dirname(abspath)
os.chdir(DIRNAME)

RESULT_OPTIONS = ["□▣■",
                  "□▤▦",
                  "□▧▩",
                  " ☆★"]
RESULTS = list(RESULT_OPTIONS[0])
GRAY, YELLOW, GREEN = RESULTS


SOLUTIONS = []
with open(FN_SOLVE, 'r') as SOLUTIONS_FILE:
    for solution in SOLUTIONS_FILE.readlines():
        SOLUTIONS.append(solution.strip().upper())

GUESSES = []
with open(FN_GUESS, 'r') as GUESSES_FILE:
    for guess in GUESSES_FILE.readlines():
        GUESSES.append(guess.strip().upper())


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
            except IndexError:
                # ugly error handling here
                print('ERROR')
                print('sol:', sol)
                print('guess:', guess)
                print('unclaimed:', unclaimed)
                print('i:', i)
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
            if compare(t[0], t[1]) == t[2]:
                print("PASS")
            else:
                print(t[0])
                print(t[1])
                print(compare(t[0], t[1]))
                print(t[2])
                print("FAIL")
        except AssertionError:
            if t[2] is None:
                print("PASS")
            else:
                print("FAIL")


def all_patterns(guess, answers):
    patterns = {}
    for sol in answers:
        p = compare(sol, guess)
        patterns[p] = patterns.get(p, 0) + 1
    return patterns


def guess_to_hint_counts(guess, answers):
    hints = all_patterns(guess, answers)
    return sorted(hints.items(), key=lambda x: x[1], reverse=True)


def guess_to_largest_bucket_size(guess, answers):
    return guess_to_hint_counts(guess, answers)[0][1]


def guess_to_num_buckets(guess, answers):
    return len(guess_to_hint_counts(guess, answers))


def guess_to_sum_squares(guess, answers):
    total = 0
    hint_counts = guess_to_hint_counts(guess, answers)
    for h in hint_counts:
        total += h[1] ** 2
    return total


def answers_guess_hint_to_answers(answers, guess, hint):
    new_answers = []
    for a in answers:
        if compare(a, guess) == hint:
            new_answers.append(a)
    if new_answers == []:
        print('WARNING: NO MATCHING SOLUTIONS!')
        input()
    return new_answers


def least_squares(answers, guesses):
    least_sum_squares = 9999999
    best_guess = "XXXXX"
    for guess in guesses:
        print(guess + '   CURRENT BEST GUESS: ', best_guess, ' SCORE: ', least_sum_squares, end='\r')
        sum_squares = guess_to_sum_squares(guess, answers)
        if sum_squares < least_sum_squares:
            best_guess = guess
            least_sum_squares = sum_squares
    print()
    return (best_guess, least_sum_squares)

# new_ans = answers_guess_hint_to_answers(SOLUTIONS, 'RAISE', GRAY * 5)
# print(guess_to_hint_counts('RAISE', SOLUTIONS))

if __name__ == "__main__":
    print(least_squares(SOLUTIONS, GUESSES))

    
# generalize the below to find the best second guesses after ROATE or ARISE
# new_ans = answers_guess_hint_to_answers(SOLUTIONS, 'ROATE', GRAY * 5)
# new_best_guess = least_squares(new_ans, GUESSES)
# print(new_best_guess)
# input()
