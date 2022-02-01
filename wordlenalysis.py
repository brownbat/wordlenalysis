import os
import sys
import multiprocessing

# TODO - optimize best guess somehow, but not sure how
# TODO - multiprocessing is kind of a mess, makes the output while
#        processing really chaotic, doesn't seem that much faster, but
#        not sure how to improve it
# TODO - more specific -- drill down worldle solutions by removing the
#        ones that have already passed; see if best first guess changes
#        over time
# TODO - more general -- see which strategy efficiently finds ANY word in
#        legal guesses, ignore solutions dictionary

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
    """Responds with a hint given a five letter solution str 'sol' and a
    five letter guess str 'guess'

    Hint strings can be built by adding combinations of GREEN, YELLOW,
    and GRAY, which are constants that can be set to individual unicode
    characters using constants RESULT_OPTIONS and RESULTS up above.
    This allows, e.g.,
      'GRAY * 5'
    to represent a hint where no letters
    in the guess are found anywhere in the answer, or
      YELLOW * 2 + GRAY * 3
    for the case where the first two letters are found somewhere in the
    answer (but not in those places) and the last three are not.
    """

    try:
        assert type(guess) == type(sol) == str
        assert len(guess) == len(sol) == 5
    except AssertionError:
        error_message = (
            f'''sol:{sol}, guess:{guess}, types:{type(sol)},
                {type(guess)}, lens:{len(sol)}, {len(guess)}'''
            )
        print(error_message)
        exit()
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
                error_message = (
                    f"""ERROR\n
                    sol: {sol}\n
                    guess:{guess}\n
                    unclaimed:{unclaimed}\n
                    i:{i}\n
                    ERROR\n
                    """
                    )
                print(error_message)
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
    """Iterates through 'tests', a list of [solution,guess,hint] tuples,
    to ensure guess_to_hint() generates the correct expected hints.
    """

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
    """return a dictionary of all possible hints and their frequency,
    {hints: count}, in response to running a guess against all possible
    answers in a list of answers"""

    patterns = {}
    for sol in answers:
        p = guess_to_hint(sol, guess)
        patterns[p] = patterns.get(p, 0) + 1
    return patterns


def guess_to_hint_counts(guess, answers):
    """return a dictionary of hints:count for a guess and list of answers

    reverse sorted, so most likely hint is first
    """
    hints = all_patterns(guess, answers)
    return sorted(hints.items(), key=lambda x: x[1], reverse=True)


def guess_to_largest_bucket_size(guess, answers):
    """Num occurrences of the most frequent hint from guess, answers
    """
    return guess_to_hint_counts(guess, answers)[0][1]


def guess_to_num_buckets(guess, answers):
    """Num distinct hints from a guess, answers list
    """
    return len(guess_to_hint_counts(guess, answers))


def guess_to_sum_squares(guess, answers):
    """Rates a guess based on how likely it is to reduce the remaining
    guesses

    Each possible hint puts you in a bucket of remaining viable answers.
    You want your answer to have the greatest likelihood of landing you
    in the smallest possible bucket.

    AESIR is minimax, the maximum possible bucket is lower than any
    other, but ROATE is better at least squares because it has a larger
    largest hint bucket, but so many smaller secondary buckets it ends up
    more likely to reduce your search space in general.
    """

    total = 0
    hint_counts = guess_to_hint_counts(guess, answers)
    for h in hint_counts:
        total += h[1] ** 2
    return total


def answers_guess_hint_to_answers(answers, guess, hint):
    """Reduces an answer set to remaining viable answers by applying a
    guess and a hint.
    """

    new_answers = []
    for a in answers:
        if guess_to_hint(a, guess) == hint:
            new_answers.append(a)
    if new_answers == []:
        print('WARNING: NO MATCHING SOLUTIONS!')
        input()
    return new_answers


def best_guess(answers, guesses):
    """Finds the best next guess given a set of answers and guesses

    uses guess_to_sum_squares() to rate guesses and returns the best one
    """

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


def best_guess_all_answers(guesses):
    """Returns the best guess (hard coding the maximum answer set)

    One-argument helper function for multiprocessing
    """
    return best_guess(SOLUTIONS, guesses)


def best_second_guess(guess, answers=SOLUTIONS):
    """After a given guess, against a set of solutions, what's your best
    second guess in response to each possible hint?
    """
    hint_counts = guess_to_hint_counts(guess, answers)
    second_guesses = []
    for hc in hint_counts:
        hint = hc[0]
        new_ans = answers_guess_hint_to_answers(answers, guess, hint)
        second_guesses.append((hint, best_guess(new_ans, GUESSES)))
    return second_guesses


def results_to_answers(guess_hints, answers):
    """Provide remaining valid answers matching a list of guesses and
    corresponding hints
    """

    gh_stack = guess_hints.copy()
    new_ans = answers.copy()
    while len(gh_stack) > 0:
        gh = gh_stack.pop()
        guess = gh[0]
        hint = gh[1]
        new_ans = answers_guess_hint_to_answers(new_ans, guess, hint)
    return new_ans


def results_to_best_guess(guess_hints, answers):
    """Solver. Returns best next guess after a series of moves and hints.
    """

    new_ans = results_to_answers(guess_hints, answers)
    return best_guess(new_ans, GUESSES)


def solution_path(answer, first_guess=None):
    """Use the solver best_guess() to find a series of guesses
    and resulting hints, a full path of guesses and hints

    A first guess can be specified to cut down the largest search time,
    or to rate initial guesses off one another.

    len(solution_path) can count the moves it takes from an initial
    guess to a solution using this method
    """

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
    multiprocessing.freeze_support()

    num_procs = 6
    guesses_sliced = []
    slice_length = len(GUESSES) // num_procs
    for i in range(num_procs):
        this_slice = GUESSES[i*slice_length:(i+1)*slice_length]
        guesses_sliced.append(this_slice)

    with multiprocessing.Pool(processes=num_procs) as pool:
        contenders = pool.map(best_guess_all_answers, guesses_sliced)
    bg = best_guess(SOLUTIONS, contenders)
    print(bg)
