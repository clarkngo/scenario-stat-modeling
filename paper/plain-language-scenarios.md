# Everyday money stories (plain-language version)

Each story works the same way:

1. **Use the usual rule.**
2. **Something odd happens.**
3. **The rule gives a silly answer.**
4. **Fix the rule.**

No math knowledge is needed to follow along. The math for DS 623 sits underneath each story; see `research-notes.md`.

---

### 1. The coffee shop and the giant order
- **Usual rule:** "Our average sale is about $6."
- **Something odd:** In a day of 100 sales, one customer places a $5,000 catering order.
- **Silly answer:** The "average sale" jumps to about $56, although nobody spends that much.
- **Fix:** Look at the **typical** sale: line up all the sales and take the one in the middle. It stays at about $6.
- **Lesson:** One big number can fool an average.

### 2. "Your card was flagged for fraud"
- **Usual rule:** "The fraud alarm is right 9 times out of 10, so a flag means it's probably fraud."
- **Count it out:** Picture 10,000 card purchases. Only 10 are fraud, and the alarm catches 9 of them. It also wrongly flags about 100 honest purchases.
- **Surprise:** Of the 109 flags, only 9 are real fraud, **fewer than 1 in 10**.
- **Fix:** Always ask "how rare is this to begin with?"
- **Lesson:** When something is rare, most alarms are false alarms.

### 3. The paycheck typo *(main example in the paper)*
- **Usual rule:** Draw the straight line that best fits "hours worked" against "pay." Then use it to predict anyone's pay.
- **Something odd:** A few paychecks were typed with an extra zero, so $500 became $5,000.
- **Silly answer:** Those typos drag the whole line upward, and every prediction comes out too high.
- **Fix:** Use a line that **listens less to points that are wildly off**. It follows the normal paychecks and mostly ignores the typos.
- **Lesson:** A good rule shouldn't let a few mistakes boss it around.

### 4. The rainy-day fund
- **Usual rule:** "Last year my worst month cost an extra $300, so a $300 cushion is enough."
- **Something odd:** This year brings a car repair and a medical bill in the same month.
- **Silly answer:** The cushion based on one calm year is far too small.
- **Fix:** Pay more attention to **recent** months, and plan for a worse month than you have seen so far.
- **Lesson:** A calm past can hide a bumpy future.

### 5. Lending money during a recession
- **Usual rule:** "Normally 2 out of 100 borrowers miss payments, so we expect 2."
- **Something odd:** A recession hits, and now 6 out of 100 miss payments.
- **Silly answer:** The old rule still puts the right people at the top of the risk list, but every risk number it gives is now too low.
- **Fix:** Update the starting assumption, "how many miss payments these days," and keep the rest.
- **Lesson:** When the world changes, update your starting guess.
