# wordlenalysis
 Wordle Anaylsis Functions

What makes a good guess?

(Some spoilers below.)

Say we're playing "high/low." I'm picking a number from 1 to 100. You
guess and I tell you high or low.

You probably want your first guess to be something like 50, rather than
20. Yes, if my answer is 15, then 20 eliminates way more numbers. But
80% of the time, you're going to be worse off than the guess of 50. You
want to minimize the size of the largest remaining bucket.

What does this have to do with Wordle?

Every guess you make will return a hint. There are maybe 30-40 possible
hints you could get back after any given first guess. 30-40 buckets of
remaining viable solutions.

One first strategy might be like guessing 50 in high/low: minimize the
maximum bucket size. So you might find something like AESIR or ARISE does
that very well.

But with Wordle, we aren't just slicing the remaining solutions into two
groups, like with high/low, we're slicing the remaining solutions up into
many groups. What if instead of high low, I gave you a choice:

You can pick 50 and I'll tell you high/low.

Or you can pick 60, and if it's lower I'll say low, but if it's higher,
I'll tell you the nearest even number.

So pick 50 -> two buckets size 50 each.
So pick 60 -> 21 buckets, one is size 60, the others are size 2.

If you minimize your maximum bucket, pick 50. Most of the time it will
take fewer guesses.

Picking 60 is going to save you so many guesses for 61-100 though, it
lowers the number of guesses required on average. You'll often get to the
answer in 2-3 guesses, instead of 5 or so.

So how can we think of this? We want to average the size of remaining
viable solutions across each possible solution. Another way to find this
is to simply take the size of the buckets we get back, and sum the
squares of each bucket.

A bucket's size is the number of times you'll end up in that bucket, and
it also is a measure of how bad it is to find ourselves in that next
bucket.

Using this method, we may tolerate some words that perform a little bit
worse in the most common case, but much better in enough other cases to
be better choices all things considered.

If we are just memorizing two starting guesses, letter position can
matter a very tiny amount on the margins, but for the most part
ROATE + SULCI is pretty close to the more normalish ARISE + CLOUT.

The tools here can be used to evaluate first guesses, measure the length
of the path from guess to any given answer, etc. Others have done this
sort of thing in other repos, big shout out to Tyler Glaiel:

https://medium.com/@tglaiel/the-mathematically-optimal-first-guess-in-wordle-cbcb03c19b0a

who got further better and faster than I did.

This is a pretty terrible README because it doesn't actually tell you how
to use this. But it lays out the questions I was curious about and my
early thought process, which I'm hoping are helpful anyway. If you share
my curiousity, maybe these ramblings will inspire you to roll your own
toolkit for wordle analysis, since these are pretty short functions to
write and felt like good practice for an amateur coder like me.

Two hard problems I faced you might have fun with (or resent):
1. Ensuring yellows are assigned correctly - if there are two Rs in the
guess, and one in the answer, only your first R should be marked YELLOW.
(You can't just blindly go place by place, sometimes need information
from up ahead).

2. Optimization. Basically unsolved for me. It would take some careful
advanced planning about where you might be able to prune paths, doing
this after the fact is much harder.

One thing I'm proud of most people wouldn't have bothered with:
generalizing output strings to take any combo of unicode characters
to make them easier to copy and paste or present, depending on the
capabilities of where you're pasting them. It's a small move and just
presentational but now you can score your wordles with filled and empty
stars, enjoy.

Wordle trivia -- Wordle's creator also created a series of addictive
social experiments for reddit, like, The Button, as part of his attempt
to fight back against the way tech companies were ruining April Fools
Day. (Remember for a while how websites would randomly not work
correctly or look right one day out of the year because techbros thought
it would be funny if their products broke sometimes? I think  Josh Wardle
helped fix that.) https://www.youtube.com/watch?v=OXzfvYoFQFo
