import os
import sys

# TODO - optimize least squares
# TODO - store solutions list at each step of solver for debugging
# TODO - count moves -- len(solutions_path()) basically
# TODO - more specific -- drill down worldle solutions by removing the
#        ones that have already passed
# TODO - see if best first guess will change over time
# TODO - more general -- see which strategy efficiently finds ANY word in
#        legal guesses, ignore solutions dictionary
# TODO - document, tests, refactor

FN_SOLVE = "wordle_solutions_alphabetized.txt"
FN_GUESS = "wordle_complete_dictionary.txt"
abspath = os.path.abspath(sys.argv[0])
DIRNAME = os.path.dirname(abspath)
os.chdir(DIRNAME)

RESULT_OPTIONS = ["□▣■",
                  "□▤▦",
                  "□▧▩",
                  " ☆★",
                  " YG"]

# RESULT_OPTIONS[0] means I'm biased for presentation, with the cost
# that test cases are harder to type. " YG" maybe best here.


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


def guess_to_hint(sol, guess):
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


def test_guess_to_hint():
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
            if guess_to_hint(t[0], t[1]) == t[2]:
                print("PASS")
            else:
                print(t[0])
                print(t[1])
                print(guess_to_hint(t[0], t[1]))
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
        p = guess_to_hint(sol, guess)
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
        if guess_to_hint(a, guess) == hint:
            new_answers.append(a)
    if new_answers == []:
        print('WARNING: NO MATCHING SOLUTIONS!')
        input()
    return new_answers


def best_guess(answers, guesses):
    least_sum_squares = 9999999
    tmp_best_guess = "XXXXX"
    for guess in guesses:
        print(guess + '   CURRENT BEST GUESS: ', tmp_best_guess, ' SCORE: ',
              least_sum_squares, end='          \r')
        sum_squares = guess_to_sum_squares(guess, answers)
        if sum_squares < least_sum_squares:
            tmp_best_guess = guess
            least_sum_squares = sum_squares
    print()
    return tmp_best_guess


def best_second_guess(guess, answers=SOLUTIONS):
    hint_counts = guess_to_hint_counts(guess, answers)
    second_guesses = []
    for hc in hint_counts:
        hint = hc[0]
        new_ans = answers_guess_hint_to_answers(answers, guess, hint)
        second_guesses.append((hint, best_guess(new_ans, GUESSES)))
    return second_guesses


def results_to_answers(guess_hints, answers):
    gh_stack = guess_hints.copy()
    new_ans = answers.copy()
    while len(gh_stack) > 0:
        gh = gh_stack.pop()
        guess = gh[0]
        hint = gh[1]
        new_ans = answers_guess_hint_to_answers(new_ans, guess, hint)
    return new_ans


def results_to_best_guess(guess_hints, answers):
    new_ans = results_to_answers(guess_hints, answers)
    return best_guess(new_ans, GUESSES)


def solution_path(answer, first_guess=None):
    new_ans = SOLUTIONS.copy()
    gh = []
    if first_guess:
        # first guess is massively slower
        hint = guess_to_hint(answer, first_guess)
        gh.append([first_guess, hint])
        new_ans = answers_guess_hint_to_answers(new_ans, first_guess, hint)

    while len(new_ans) > 1:
        guess = best_guess(new_ans, GUESSES)
        hint = guess_to_hint(answer, guess)
        gh.append([guess, hint])
        new_ans = answers_guess_hint_to_answers(new_ans, guess, hint)
    final = [new_ans[0], GREEN * 5]
    gh.append(final)
    return gh


if __name__ == "__main__":
    path = solution_path('DIGIT', 'LIGHT')
    print()
    # print(results_to_answers(path[:-3], SOLUTIONS))
    
