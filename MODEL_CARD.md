# Model card: will this trip crawl?

## What it does
At pickup, it estimates the probability that a New York yellow taxi trip will crawl, meaning an average speed under 6 mph. A dispatcher would warn the passenger when the probability is 0.30 or higher.

## Intended use and what it is not for
- **Intended:** a warning shown at pickup, to help a passenger plan ahead.
- **Not intended:** estimating arrival times or fares, judging a driver, or any decision about a person. It has no information about why a trip is slow.

## Data
- New York yellow taxi trips, 200,000 per month for May, June and July 2026 (600,000 in total), raw on purpose.
- Target: `is_crawl` = 1 when `trip_distance` divided by the duration in hours is below 6 mph.
- Trips removed (29,673, 5%): duration under 1 or over 120 minutes, distance of 0 or over 40 miles, speed of 70 mph or more. Two trips picked up in April are also removed. Each rule is fixed and learns nothing from the data. The full list of data problems and decisions is in `reports/data_issues.md`.
- Flex fare trips (`payment_type` 0, about 25% of valid trips) are kept, because a dispatcher would see them in practice. They crawl less often (11.5% against 20.8%).
- Split by pickup month: May for training (190,878 trips), June for every decision (190,003), July for one final test (189,444).
- Crawl rate by month: 19.7% in May, 19.0% in June, 16.8% in July.

## Model
Logistic regression inside a scikit-learn pipeline (`src/pipeline.py`).
- **Inputs, all known at pickup:** trip distance and its logarithm (treated as the planned route length), pickup hour, day of week, pickup zone, drop-off zone, a same-zone flag and an airport flag.
- **Never used:** drop-off time, duration, speed, fare, fees, tip, total, rate code, payment type.
- **Pipeline:** missing values are filled with the May median, numbers are scaled, categories are one-hot encoded (zones with fewer than 50 May trips are grouped). Everything that learns from data is fitted on May only.
- **Features tested on June, one group at a time:** distance 0.445 PR AUC, plus time 0.495, plus zones 0.632 (the biggest gain), plus passenger count and vendor 0.634. The last group was dropped because it added only 0.002.

## Baselines (scored on June)
| Baseline | PR AUC | Lift |
|---|---|---|
| Always predict no crawl | 0.190 | 1.00 |
| Rule: pickup 10:00 to 18:59 in the 10 zones with the most crawls in May | 0.279 | 1.47 |
| Decision tree, depth 2 (hour, day, distance): the baseline to beat | 0.339 | 1.78 |

A decision tree with the final features reaches 0.574 PR AUC at depth 20 and is still below the logistic regression (0.632).

## Threshold and costs
We assumed a missed crawl costs 3 times a needless warning. This is a stated assumption, not a measurement. On June, the threshold with the lowest cost is **0.30**: it warns 27% of trips, with precision 0.509 and recall 0.723. The cost per trip is 0.291, against 0.571 for never warning and 0.81 for always warning. The choice depends on the assumption: the best threshold is 0.37 if a missed crawl costs 2 times a warning, and 0.19 if it costs 5 times.

## Reliability
On June the probabilities are well calibrated (`reports/figures/reliability_june.png`). The model overestimates slightly in the middle range: trips given 0.33 crawled 29% of the time, and trips given 0.22 crawled 19%.

## Results
| | June | July (95% bootstrap interval) |
|---|---|---|
| PR AUC | 0.632 | 0.627 (0.621 to 0.632) |
| Lift | 3.32 | 3.73 (3.69 to 3.77) |
| Precision at 0.30 | 0.509 | 0.465 (0.460 to 0.469) |
| Recall at 0.30 | 0.723 | 0.779 (0.775 to 0.784) |
| Cost per trip (missed crawl = 3, false alarm = 1) | 0.291 | 0.262 (0.259 to 0.265) |
| Baseline PR AUC (depth-2 tree) | 0.339 | 0.327 (0.324 to 0.331) |

July was scored once, at the end, with the model and the threshold chosen on June. Nothing was changed after seeing it. The model beats the baseline by 0.299 PR AUC (interval 0.295 to 0.304). Lift is higher in July only because the crawl rate is lower, so PR AUC is the figure to compare across months. In July, never warning costs about 0.50 per trip and warning everyone about 0.83.

## Where it fails
Results on June at threshold 0.30, with the number of trips in each group. One threshold is used for all trips, so the warning misses most crawls in the groups where crawls are rare.

| Group | Trips | Crawl rate | Precision | Recall |
|---|---|---|---|---|
| All trips | 190,003 | 19.0% | 0.509 | 0.723 |
| Pickup 0-6h | 22,622 | 3.4% | 0.254 | 0.131 |
| Pickup 7-9h | 20,978 | 14.5% | 0.487 | 0.590 |
| Pickup 10-18h | 92,987 | 28.1% | 0.521 | 0.816 |
| Pickup 19-23h | 53,416 | 11.8% | 0.465 | 0.474 |
| Weekday | 138,584 | 21.5% | 0.523 | 0.775 |
| Weekend | 51,419 | 12.4% | 0.424 | 0.482 |
| Distance under 0.5 miles | 9,546 | 57.4% | 0.661 | 0.868 |
| Distance 2-4 miles | 45,728 | 11.0% | 0.421 | 0.338 |
| Distance over 4 miles | 44,839 | 0.7% | 0.263 | 0.032 |
| Flex fare | 48,170 | 12.1% | 0.558 | 0.602 |
| Not flex | 141,833 | 21.4% | 0.502 | 0.746 |
| Pickup in Manhattan | 168,126 | 21.3% | 0.512 | 0.725 |
| Pickup in Brooklyn | 5,213 | 4.6% | 0.318 | 0.550 |
| Pickup in Queens | 15,727 | 0.8% | 0.420 | 0.468 |

- It misses about 87% of the crawls that start between midnight and 7 am, and almost all crawls on trips over 4 miles.
- It does worse at weekends than on weekdays.
- It is a Manhattan model: 88% of the trips start there. The Bronx (679 trips), Staten Island (11), EWR (4) and unknown zones (243) have too few trips to judge, and so do airport trips (15,666 trips but only about 60 crawls).
- Flex fare trips have lower recall (0.60 against 0.75). We have not checked why.

## What went wrong or did not work
- Passenger count and vendor added only 0.002 PR AUC on June and were dropped.
- The decision tree improved with depth but never reached the logistic regression.
- The hand-written rule (busy hours in the busiest zones) was only 1.47 times better than chance.
- In July, precision fell from 0.509 to 0.465 while recall rose from 0.723 to 0.779. With fewer crawls, the same threshold warns more trips that do not crawl.
- A single threshold is a poor fit for night and long trips, where crawls are rare.

## Limits
- `trip_distance` is measured during the trip. We treat it as the planned route length, but the real distance includes detours caused by traffic, so it leaks a little information.
- The threshold rests on our cost assumption, which no data supports.
- Only three months of data. The crawl rate fell from 19.7% to 16.8% over them, and the July interval only measures sampling noise, not how the rate moves from month to month.
- Crawl rates by zone were stable from May to June (correlation 0.98, the same 10 worst zones). Crawl rates by day of week moved by 2 to 3 points.
- The model uses no personal information, but it warns far less often outside Manhattan, so it serves some neighbourhoods much worse than others.

## Reproduce
See `README.md`, which also declares how AI was used in this project.