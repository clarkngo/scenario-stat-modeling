# Research notes: making the math easier, and finance scenarios

Collected 2026-10-14 to plan the full draft. These notes are not paper text yet.
**Verified** means I saw the bibliographic record (journal, volume, DOI) in a primary or indexed listing.
**Check** means the claim came from secondary coverage, so read the paper before citing it.

---

## Part A. What the learning research says, and what it means for this project

| Finding | Evidence | What to do in the portal or paper |
|---|---|---|
| **Problem first, then instruction ("productive failure")** beats instruction first for conceptual understanding, provided the problem is hard but solvable and students have enough background. | Sinha & Kapur (2021), *Review of Educational Research*: meta-analysis of 53 studies and 166 comparisons. **Check** effect sizes; the "2–3×" figure comes from press coverage. | This is the **Shock** stage. Let learners fit OLS and *predict* what the shock will do **before** showing the Huber derivation. Add a "make your prediction" box above the lab. |
| **Worked examples** help novices more than solving problems unaided. The benefit reverses for students who already know the material (the "expertise reversal" effect). | Paas (1992), statistics training: worked and completion problems gave better transfer. A Springer *Higher Education* study, done in statistics, found low-prior-knowledge students gained most from worked examples. **Check** both. | Give the OLS derivation **fully worked**. Present the Huber derivation as a **completion problem**: show the steps, then leave the IRLS weight step for the learner to fill in. |
| **Concreteness fading**: concrete story → picture → symbols works better than starting with the symbols. | Fyfe, McNeil, Son & Goldstone (2014), *Educational Psychology Review*, systematic review. A 2020 critique warns it does not transfer equally well to every domain. | Order every section **story → chart → equation → code**. The finance scenarios below supply the story. |
| **Natural frequencies** ("9 out of 10,000") make Bayes problems much easier than probabilities ("0.09%"). | Gigerenzer & Hoffrage (1995), *Psychological Review* (**Verified** citation). McDowell & Jacobs (2017) meta-analysis: 24% correct vs. 4% (**Check**). | Use counts out of 10,000 in the fraud-alert scenario (B2) and in any probability explanation. |
| **Real data with a context and purpose.** | GAISE College Report (ASA, 2016), recommendation 3 (**Verified**). | Replace the synthetic housing data with real finance data (see Part C). |
| **AI tutors help only with guardrails.** An answer-giving chatbot raised practice scores but **lowered** later exam scores. A hint-only tutor removed that harm. | Bastani et al. (2025), *PNAS*, about 1,000 students (**Verified** citation). Kestin et al. (2025), *Scientific Reports*, n = 194: a pedagogy-designed AI tutor beat in-class active learning (**Verified** citation). | This is direct evidence for the paper's "AI-guided, Socratic" design. The tutor should give **hints and questions, never the final formula**. Cite both papers in the Introduction. |

---

## Part B. Finance scenarios, from easiest to hardest

Each scenario follows the paper's loop (**Derive → Implement → Shock → Diagnose → Revise**) and needs only NumPy.

### B1. "The catering order that broke the average": mean vs. median *(warm-up)*
- **Story:** A coffee shop's typical sale is about $6. One day a $5,000 catering order arrives. The owner asks, "What's our average sale?"
- **Baseline:** The sample mean, which minimizes Σ(xᵢ − μ)².
- **Shock:** One extreme transaction. The mean jumps; the median doesn't move.
- **Diagnosis:** Squared loss lets a single point pull the estimate as far as it likes. This is the one-variable version of the OLS problem.
- **Revision:** The median (absolute loss), then the Huber location estimate. That estimate is exactly what Huber's (1964) original paper solved.
- **Why it helps:** It teaches the whole idea behind the paper with one number before any matrices appear.

### B2. "Your card was flagged. Is it really fraud?": Bayes' theorem
- **Story:** Out of 10,000 card transactions, 10 are fraud. The detector catches 9 of the 10. It also falsely flags 1% of honest transactions, which is about 100 of 9,990.
- **Baseline:** "The detector is 90% accurate, so a flag means a 90% chance of fraud."
- **Shock:** Count it out: 9 real frauds out of 109 flags, so **P(fraud | flag) ≈ 8%**.
- **Diagnosis:** The intuition ignored the **base rate**, how rare fraud is in the first place.
- **Revision:** Bayes' rule, P(F | flag) = P(flag | F)·P(F) / P(flag), presented in natural frequencies.
- **Second shock:** During the holidays, fraud doubles to 20 per 10,000. Learners predict, then compute, the new answer (≈ 15%).

### B3. "How jumpy is this stock?": CAPM beta, the **recommended main case**
- **Story:** "If the whole market rises 1%, how much does this stock or industry typically move?" That number is **beta**, and analysts use it every day.
- **Baseline:** Regress the stock's excess return on the market's excess return. Beta is the OLS slope. **The current code is already this model.**
- **Shock:** One extreme month, such as a crash month (October 1987, October 2008, March 2020) or a takeover announcement.
- **Diagnosis:** A single outlier month can change the OLS beta dramatically. The data have **heavy tails**, so the Gaussian assumption fails (Cont, 2001).
- **Revision:** Robust beta via Huber IRLS. This is exactly what **Martin & Simin (2003)** propose in the *Financial Analysts Journal*. In 8,314 stocks, they found deleting one outlier could change the OLS beta dramatically, and that small companies were most affected.
- **Data:** Kenneth French Data Library: the monthly market factor (Mkt-RF) plus industry portfolios. It's free and goes back to 1926. Returns are in percent, and missing values are coded −99.
- **Why it's the best fit:** It is the same math as the current prototype, with real data and a published finance paper that matches. Learners can also read the result in plain words: "Beta = 1.4 means the stock tends to move 1.4% when the market moves 1%."

### B4. "How much could we lose on a bad day?": Value-at-Risk and volatility
- **Story:** A fund manager wants to know the loss they should expect to beat only one day in 100.
- **Baseline:** Assume returns are normal. Estimate σ̂ from history and set VaR₉₉ = 2.33·σ̂ (the 99% normal quantile).
- **Shock:** A calm year followed by March 2020. Losses exceed the VaR far more than 1% of the time.
- **Diagnosis:** Two assumptions fail. Volatility **clusters**, so σ isn't constant, and the tails are heavier than normal (Cont, 2001).
- **Revision:** An exponentially weighted variance, σ²ₜ = λσ²ₜ₋₁ + (1 − λ)r²ₜ₋₁, with λ = 0.94 for daily data, following the RiskMetrics Technical Document (J.P. Morgan, 1996). Learners count VaR breaches before and after the change.
- **Data:** The daily market factor from the French library.

### B5. "Will this customer miss a payment?": logistic regression and a recession shock *(advanced)*
- **Story:** A bank estimates each cardholder's probability of default.
- **Baseline:** Logistic regression derived by maximum likelihood (cross-entropy loss, gradient Xᵀ(σ(Xβ) − y)) and trained with gradient descent in NumPy.
- **Shock:** The share of customers who default changes, for example because of a recession, or because the bank trained on a rebalanced sample. The **ranking** of risky customers stays fine, but the **probabilities** are now wrong.
- **Diagnosis:** The intercept encodes the base rate. This links back to B2.
- **Revision:** Prior correction of the intercept or the probabilities. Dal Pozzolo et al. (2015) derive p = βpₛ / (βpₛ − pₛ + 1) for undersampling.
- **Data:** UCI "Default of Credit Card Clients" (ID 350): 30,000 Taiwanese cardholders, 23 features, CC BY 4.0, from Yeh & Lien (2009).

---

## Part C. Recommendation

1. **Make CAPM beta (B3) the paper's main worked case.** It reuses the current OLS → Huber code, uses real public data, and has a matching peer-reviewed finance paper (Martin & Simin, 2003).
2. **Open with B1 (coffee-shop mean) as a warm-up** before any matrices, and use **B2 (fraud alert)** as the Bayes/base-rate sidebar.
3. **Mention B4 and B5 under Future Work** as further scenarios, each one shock targeting a different assumption.
4. **Build the portal around the evidence:** learners make a prediction before each shock (productive failure); OLS is fully worked and Huber is a completion problem (worked examples); each section runs story → chart → equation → code (concreteness fading); and the AI tutor gives hints only (Bastani et al., 2025).

---

## References found (APA 7, for the paper)

- Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., & Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. *Proceedings of the National Academy of Sciences, 122*(26), e2422633122. https://doi.org/10.1073/pnas.2422633122 *(check the author list)*
- Cont, R. (2001). Empirical properties of asset returns: Stylized facts and statistical issues. *Quantitative Finance, 1*(2), 223–236. https://doi.org/10.1080/713665670
- Dal Pozzolo, A., Caelen, O., Johnson, R. A., & Bontempi, G. (2015). Calibrating probability with undersampling for unbalanced classification. *2015 IEEE Symposium Series on Computational Intelligence*, 159–166. https://ieeexplore.ieee.org/document/7376606 *(check the pages and venue)*
- Fyfe, E. R., McNeil, N. M., Son, J. Y., & Goldstone, R. L. (2014). Concreteness fading in mathematics and science instruction: A systematic review. *Educational Psychology Review, 26*(1), 9–25. https://doi.org/10.1007/s10648-014-9249-3 *(check the DOI)*
- GAISE College Report ASA Revision Committee. (2016). *Guidelines for assessment and instruction in statistics education college report 2016*. American Statistical Association. https://www.amstat.org/asa/files/pdfs/GAISE/GAISECollege_Full.pdf
- Gigerenzer, G., & Hoffrage, U. (1995). How to improve Bayesian reasoning without instruction: Frequency formats. *Psychological Review, 102*(4), 684–704. https://doi.org/10.1037/0033-295X.102.4.684
- J.P. Morgan/Reuters. (1996). *RiskMetrics technical document* (4th ed.). https://www.msci.com/research-and-insights/paper/1996-riskmetrics-technical-document
- Kestin, G., Miller, K., Klales, A., Milbourne, T., & Ponti, G. (2025). AI tutoring outperforms in-class active learning: An RCT introducing a novel research-based design in an authentic educational setting. *Scientific Reports, 15*, 17458. https://doi.org/10.1038/s41598-025-97652-6
- Martin, R. D., & Simin, T. T. (2003). Outlier-resistant estimates of beta. *Financial Analysts Journal, 59*(5), 56–69. https://doi.org/10.2469/faj.v59.n5.2564 *(check the DOI; the CFA Institute page is linked below)*
- Roediger, H. L., III, & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science, 17*(3), 249–255. https://doi.org/10.1111/j.1467-9280.2006.01693.x *(check the DOI)*
- Sinha, T., & Kapur, M. (2021). When problem solving followed by instruction works: Evidence for productive failure. *Review of Educational Research, 91*(5), 761–798. https://doi.org/10.3102/00346543211019105 *(check the DOI)*
- Yeh, I.-C., & Lien, C.-H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. *Expert Systems with Applications, 36*(2), 2473–2480. https://doi.org/10.1016/j.eswa.2007.12.020 *(check the DOI)*

### Source pages consulted
- Martin & Simin abstract (CFA Institute): https://rpc.cfainstitute.org/research/financial-analysts-journal/2003/outlier-resistant-estimates-of-beta
- Kestin et al. full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/
- Bastani et al. summary (Wharton): https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education
- GAISE 2016 summary (ASA): https://magazine.amstat.org/?p=47967
- UCI dataset 350: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- Fyfe et al. review summary: https://pc.cogs.indiana.edu/?p=885
- Concreteness-fading critique (2020): https://link.springer.com/article/10.1007/s10648-020-09581-7
- Worked examples in a statistics classroom: https://ubmr.hds.hebis.de/EdsRecord/eric%252CEJ1238088
- Expertise reversal in statistics: https://link.springer.com/article/10.1007/s10734-011-9476-1
- Paas (1992) record: https://www.causeweb.org/cause/node/5623
- Natural frequencies review: https://www.frontiersin.org/articles/10.3389/fpsyg.2018.01833/pdf
- Productive failure coverage: https://www.weforum.org/stories/2021/09/students-who-productively-fail-learn-more/
- RiskMetrics document (MSCI): https://www.msci.com/research-and-insights/paper/1996-riskmetrics-technical-document
- Cont (2001) record: https://ideas.repec.org/a/taf/quantf/v1y2001i2p223-236.html
- Dal Pozzolo et al. (IEEE): https://ieeexplore.ieee.org/document/7376606
