# The math, one small step at a time

**Rule for this page:** words first, then a tiny example you can check on a phone calculator.
The symbol comes last, and only once you already know what it means.

---

## Step 1: The average

**Words:** Add everything up, then divide by how many there are.

**Try it:** Three coffee sales of $5, $6, and $7.
5 + 6 + 7 = 18, and 18 ÷ 3 = **$6**.

**Symbol:** x̄ = (x₁ + x₂ + … + xₙ) ÷ n
*Read "x̄" as "x-bar." It just means "the average."*

---

## Step 2: A "miss"

**Words:** A miss is how far off a guess was: **real amount − guess**.

**Try it:** You guessed a sale would be $6, and it was $7. The miss is 7 − 6 = **$1**.

---

## Step 3: Why one big miss takes over

> 🤔 **Guess first:** One miss of 100, or a hundred misses of 1. Which hurts the usual method more?

**Words:** The usual method squares every miss (multiplies it by itself) and tries to make the total as small as possible.
Squaring makes big misses **huge**.

| Miss | Squared |
|---|---|
| 1 | 1 |
| 2 | 4 |
| 10 | 100 |
| 100 | **10,000** |

A single miss of 100 counts as much as **ten thousand** misses of 1.
That is why one typo can drag the whole answer toward it.

**Symbol:** total = Σ (miss)²
*Read "Σ" as "add them all up."*

---

## Step 4: The line

**Words:** pay = **starting amount** + **rate** × hours

**Try it:** Five workers, paid $20 an hour:

| Hours | Real pay | Typed into the system |
|---|---|---|
| 10 | $200 | $200 |
| 20 | $400 | $400 |
| 30 | $600 | **$6,000** ← extra zero |
| 40 | $800 | $800 |
| 50 | $1,000 | $1,000 |

> 🤔 **Guess first:** One typo out of five. How much will it throw off the prediction for a 10-hour shift? A few dollars? A hundred?

The usual method, fitted to the typed numbers, gives:
**pay = $1,080 + $20 × hours**

Now predict pay for 10 hours: 1,080 + 200 = **$1,280**. The real pay is $200.
One typo made **every** prediction $1,080 too high.

---

## Step 5: The fix is a fairer penalty

**Words:** Square small misses as before, but once a miss gets big, let the penalty grow **slowly** instead of exploding.

| Miss | Usual penalty | Fair penalty |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 4 | 4 |
| 10 | 100 | 36 |
| 100 | 10,000 | **396** |

The typo still counts, but it can no longer shout over everyone else.
This fairer penalty is called the **Huber loss**, after Peter Huber, who proposed it in 1964.

**Symbol (small misses):** penalty = miss × miss
**Symbol (big misses):** penalty = 4 × miss − 4
*The switch happens at a miss of 2. In the paper, this cutoff is the Greek letter δ, "delta."*

---

## Step 6: Each paycheck gets a "say"

**Words:** Give every data point a say from 0 (ignored) to 1 (full say).
Normal paychecks get a full say. A paycheck that is wildly off gets almost none.

**Try it:** In the table above, the four normal paychecks each get a say of **1**. The $6,000 typo gets a say close to **0**.

**Symbol:** say = smaller of (1, cutoff ÷ size of miss)
*In the paper "say" is written w, for "weight."*

---

## Step 7: The recipe the computer follows

1. Draw the usual line.
2. Measure each point's miss.
3. Give far-off points less say.
4. Redraw the line, listening to each point by its say.
5. Repeat steps 2–4 until the line stops moving. This usually takes about 10 rounds.

For the paycheck table, the fixed line ends up at **pay = $20 × hours**, which is exactly right.

*In the paper this recipe is called "IRLS," short for "iteratively reweighted least squares." That name only means "redraw the line with new says, again and again."*

---

## Step 8: The fraud alarm is only division

10,000 purchases. 10 are fraud. The alarm catches 9 of them and also wrongly flags 100 honest purchases.

> 🤔 **Guess first:** Your card gets flagged. What's the chance it's really fraud? Write down a number before you read on.

Flags in total: 9 + 100 = 109
Real fraud among the flags: 9 ÷ 109 ≈ **8%**

That's the whole calculation. In textbooks it's called **Bayes' rule**.

---

## 💡 The aha, in one sentence
**Squaring lets one big mistake shout over everyone else, so the fix is to stop letting it shout.**

## Say it back (try these tomorrow, without looking)
1. Why can one typo ruin an average or a line?
2. What does the "fair penalty" do differently with a big miss?
3. If an alarm is "90% accurate" but the thing it looks for is rare, are most alarms real or false?

*Trying to recall an answer, rather than rereading it, is what makes learning stick (Roediger & Karpicke, 2006).*

## Symbol cheat sheet

| You'll see | Say it as | It means |
|---|---|---|
| x̄ | "x-bar" | the average |
| ŷ | "y-hat" | the guess |
| y − ŷ | "y minus y-hat" | the miss |
| Σ | "sum" | add them all up |
| β | "beta" | the dial settings of the line (starting amount and rate) |
| δ | "delta" | the cutoff for a "big" miss |
| w | "w" | how much say a point gets |

## What you never have to do by hand
Matrix algebra, inverses, and derivatives are how the computer finds the line.
For this course you need to understand the **idea** in Steps 1–7. NumPy does the heavy lifting.
