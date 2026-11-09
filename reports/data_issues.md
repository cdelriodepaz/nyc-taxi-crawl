# Data issues and decisions

Explored on May trips only (the training month). Decisions: **fix** = repair it, **flag** = mark it and keep going, **drop** = remove it.

| Problem | How much | Decision | Why |
|---|---|---|---|
| Impossible duration, distance or speed | 29,673 of 600,000 (5%) | Drop (in `load_trips()`) | The target cannot be labelled reliably |
| Trips picked up in April | 2 | Drop (in `load_trips()`) | They belong to no split |
| Flex fare trips: `passenger_count` empty | 23.3% of May | Fix: impute in the pipeline, with a value computed on train only | The trips are kept (decision in PROBLEM.md) |
| `passenger_count` = 0 | 622 in May | Flag: treat as missing in the pipeline | A trip cannot have 0 passengers |
| `RatecodeID`, `store_and_fwd_flag`, surcharges empty on flex fare | 23.3% of May | No action | Excluded columns, not model inputs |
| `request_source` empty and undocumented | 100% | Drop the column | No information and no documentation |
| Negative amounts (`fare_amount`, `total_amount`, fees) | about 0.3% | Flag, rows kept | Excluded columns; the trip itself can still be valid |
| Duplicated rows | 0 | No action | None found |
| Pickup and dropoff in the same zone | 4.6% | No action | Legitimate short trips |
| Dropoff before pickup | 0 | No action | None found |