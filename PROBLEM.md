# Problem card

| **Question** | At pickup, predict whether each trip will crawl through traffic, so that the dispatcher can warn the passenger. |

| **Target** | is_crawl is 1 when the trip’s average speed is below 6 mph, and 0 otherwise. Average speed = trip_distance (miles) divided by the duration in hours, where duration = tpep_dropoff_datetime − tpep_pickup_datetime. |

| **One row is** | One single taxi trip. |

| **Predict at** | Pickup, the moment the passenger gets in the vehicle. |

| **Allowed information** | tpep_pickup_datetime, PULocationID, DOLocationID, passenger_count, VendorID, and trip_distance. The distance is measured during the trip, but we treat it as the length of the planned route, which a routing app can calculate at pickup. We must keep in mind that it reflects the route actually driven, so a detour caused by traffic leaks a little information. Everything recorded at drop-off or payment is excluded: drop-off time, fare, fees, tip, total, RatecodeID and payment_type.|

| **Left out** | Trips whose speed cannot be trusted, so they cannot be labelled: duration under 1 minute or over 120 minutes (above two hours, durations are dominated by meter errors, which would be labelled as crawls), distance of 0 miles or over 40 miles, and average speed of 70 mph or more (each value is plausible alone, but the combination is not). Together these remove 29,673 of 600,000 trips (5%). Flex fare trips (`payment_type` 0, 25% of valid trips) are kept: the dispatcher would face them in practice, so dropping them would make the model look better than it would be in use. They crawl less often (11.5% against 20.8%), mostly because they are longer trips (median 3.0 miles against 1.7), and they have no `passenger_count`, which the pipeline must handle. |

| **Positive rate** | 18.5% of valid trips crawl (about one in five). |

| **Decision it supports** | The dispatcher, when receiving the prediction, sends a warning to the customer if their trip is going to crawl so that they can plan ahead. |

| **Costly mistake** | Both missing a crawl and a needless warning would be costly mistakes to consider. If the user is sent a warning for crawl every time they go on a trip but ends up being a false alarm, they would lose trust in the system, in the long run it would cause more dissatisfaction. On the other side, not being warned of a crawl is the most "impactful" of the mistakes, since an unexpected delay may cause anger from the customer. |

| **Metric** | The model can be measured trough various different metrics. Recall: % of warned users out of all of the crawl trips that took place. Precision: % of correct warnings out of all users that have crawled trough traffic. |

| **Baseline to beat** | [The best baseline score, filled in at the end] |

## Changes

- *YYYY-MM-DD: what changed, and why.*