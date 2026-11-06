# Problem card

| **Question** | At pickup, predict whether each trip will crawl through traffic, so that the dispatcher can warn the passenger. |
| **Target** | is_crawl is 1 when the trip’s average speed is below 6 mph, and 0 otherwise. Average speed = trip_distance (miles) divided by the duration in hours, where duration = tpep_dropoff_datetime − tpep_pickup_datetime. |
| **One row is** | One single taxi trip. |
| **Predict at** | Pickup, the moment the passenger gets in the vehicle. |
| **Allowed information** | tpep_pickup_datetime, PULocationID, DOLocationID, passenger_count, VendorID, and trip_distance. The distance is measured during the trip, but we treat it as the length of the planned route, which a routing app can calculate at pickup. We must keep in mind that it reflects the route actually driven, so a detour caused by traffic leaks a little information. Everything recorded at drop-off or payment is excluded: drop-off time, fare, fees, tip, total, RatecodeID and payment_type.|
| **Left out** | [Trips removed and why, with how many rows each step removes] |
| **Positive rate** | [% of trips that are positive, after the filters] |
| **Decision it supports** | The dispatcher, when receiving the prediction, sends a warning to the customer if their trip is going to crawl so that they can plan ahead. |
| **Costly mistake** | Both missing a crawl and a needless warning would be costly mistakes to consider. If the user is sent a warning for crawl every time they go on a trip but ends up being a false alarm, they would lose trust in the system, in the long run it would cause more dissatisfaction. On the other side, not being warned of a crawl is the most "impactful" of the mistakes, since an unexpected delay may cause anger from the customer. |
| **Metric** | [How you measure the model] |
| **Baseline to beat** | [The best baseline score, filled in at the end] |

## Changes

- *YYYY-MM-DD: what changed, and why.*