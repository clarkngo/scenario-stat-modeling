| Shock (contamination) | OLS test RMSE | Huber test RMSE | OLS ‖β̂−β‖ | Huber ‖β̂−β‖ | Huber IRLS iters |
|---|---|---|---|---|---|
| 0% | 40.3 | 40.3 | 4.6 | 4.7 | 8.6 |
| 5% | 157.2 | 40.5 | 152.0 | 5.9 | 10.6 |
| 10% | 297.3 | 41.3 | 294.3 | 9.6 | 10.9 |
| 20% | 573.9 | 45.5 | 572.5 | 21.2 | 12.4 |
| 30% | 852.6 | 62.0 | 851.5 | 47.1 | 16.6 |

Mean over 200 replications; n_train=200, n_test=1000 (clean); noise σ=40, so σ is the irreducible RMSE floor.
