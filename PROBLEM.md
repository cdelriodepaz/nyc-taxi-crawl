# Problem card

| **Question** | At pickup, predict whether each trip will crawl through traffic, so that the dispatcher can warn the passenger. |

| **Target** | is_crawl is 1 when the trip’s average speed is below 6 mph, and 0 otherwise. Average speed = trip_distance (miles) divided by the duration in hours, where duration = tpep_dropoff_datetime − tpep_pickup_datetime. |

| **One row is** | One single taxi trip. |

| **Predict at** | Pickup, the moment the passenger gets in the vehicle. |

| **Allowed information** | tpep_pickup_datetime, PULocationID, DOLocationID, passenger_count, VendorID, and trip_distance. The distance is measured during the trip, but we treat it as the length of the planned route, which a routing app can calculate at pickup. We must keep in mind that it reflects the route actually driven, so a detour caused by traffic leaks a little information. Everything recorded at drop-off or payment is excluded: drop-off time, fare, fees, tip, total, RatecodeID and payment_type.|

| **Left out** | Trips whose speed cannot be trusted, so they cannot be labelled: duration under 1 minute or over 120 minutes (above two hours, durations are dominated by meter errors, which would be labelled as crawls), distance of 0 miles or over 40 miles, and average speed of 70 mph or more (each value is plausible alone, but the combination is not). Together these remove 29,673 of 600,000 trips (5%). Two trips picked up in April are also removed, because the split is by pickup month. Flex fare trips (`payment_type` 0, 25% of valid trips) are kept: the dispatcher would face them in practice, so dropping them would make the model look better than it would be in use. They crawl less often (11.5% against 20.8%), mostly because they are longer trips (median 3.0 miles against 1.7), and they have no `passenger_count`, which the pipeline must handle. |

| **Positive rate** | 18.5% of valid trips crawl (about one in five). |

| **Decision it supports** | The dispatcher, when receiving the prediction, sends a warning to the customer if their trip is going to crawl so that they can plan ahead. |

| **Costly mistake** | Both mistakes cost something. A missed crawl is the more expensive one: the passenger gets an unexpected delay and is annoyed. A needless warning is cheaper, but if false alarms are frequent, passengers stop paying attention to the warnings and lose trust in the system. We assume a missed crawl costs 3 times a needless warning. This is a stated assumption, not a measurement, and it sets the warning threshold (0.30 on June). |

| **Metric** | Precision: of the trips we warn, the share that really crawl (it counts false alarms). Recall: of the trips that really crawl, the share we warn (it counts missed crawls). PR AUC summarises both across all thresholds, and lift is PR AUC divided by the positive rate. Accuracy is never used alone. The warning threshold is chosen from stated costs (see Costly mistake). |

| **Baseline to beat** | Depth-2 decision tree trained on May and scored on June (inputs: pickup hour, day of week and trip_distance; random_state=42). It flags a trip when its predicted probability is above May's positive rate (19.7%). Result on June: PR AUC 0.339, lift 1.78 (June positive rate is 19.0%), precision 0.315, recall 0.833. In practice the tree only used trip_distance: very short trips crawl most often. The other rungs scored lower: always predicting no crawl has lift 1.00, and a hand-written rule (pickup 10:00-18:59 in the 10 zones with the highest crawl rate in May) has lift 1.47 (precision 0.445, recall 0.349). |

## Changes

- 2026-11-09: filled in Baseline to beat with the results of the baseline ladder, scored on June.
- 2026-11-16: corrected the definition of precision in Metric, and stated the cost ratio that sets the warning threshold in Costly mistake.
- 2026-11-16: the final model uses distance, time and zones. Passenger count and VendorID were tested and dropped, because they added only 0.002 PR AUC on June.