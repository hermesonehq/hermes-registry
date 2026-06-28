# PromQL Queries Reference

This file contains the recommended PromQL queries and template configurations
for monitoring Latency and Error Rates of Agent Platform agents.

## Table of Contents

-   [1. Latency (95th Percentile)](#1-latency-95th-percentile)
    -   [Z-Score (Steady Traffic)](#z-score-recommended-for-steady-traffic)
    -   [Moving Averages (Bursty Traffic)](#moving-averages-recommended-for-bursty-traffic)
    -   [Seasonal Decomposition (Seasonal Traffic)](#seasonal-decomposition-recommended-for-traffic-with-seasonal-or-time-of-day-component)
-   [2. Error Rate (SLO)](#2-error-rate-slo)
    -   [Fast Burn SLO](#fast-burn-slo-1-hour-and-5-minute-windows)
    -   [Slow Burn SLO](#slow-burn-slo-3-day-and-6-hour-windows)

--------------------------------------------------------------------------------

## 1. Latency (95th Percentile)

### Z-Score (Recommended for Steady Traffic)

#### Long-Window Z-Score (For Established Agents - >1 week history)

Compares the 5-minute 95th percentile latency to the 1-week baseline.

```promql
abs(
  histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[5m])) by (le, reasoning_engine_id))
  -
  histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[1w])) by (le, reasoning_engine_id))
)
/
stddev_over_time(
  (histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[5m])) by (le, reasoning_engine_id)))[1w:5m]
) > 3
```

*Note: The denominator uses a subquery `[1w:5m]` to calculate standard deviation
of the 5-minute latency over 1 week. The numerator uses `[1w]` rate directly to
avoid a second subquery for the mean.*

#### Short-Window Z-Score (For Newer Agents - >1 hour history)

Compares the 1-minute 95th percentile latency to the 1-hour baseline. Useful for
quick activation on new agents.

```promql
abs(
  histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[1m])) by (le, reasoning_engine_id))
  -
  histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[1h])) by (le, reasoning_engine_id))
)
/
stddev_over_time(
  (histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[1m])) by (le, reasoning_engine_id)))[1h:1m]
) > 3
```

### Moving Averages (Recommended for Bursty Traffic)

Compares the 5-minute latency to the 1-hour average.

```promql
histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[5m])) by (le, reasoning_engine_id))
>
1.5 * histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[1h])) by (le, reasoning_engine_id))
```

### Seasonal Decomposition (Recommended for traffic with seasonal or time-of-day component)

> [!NOTE] For the Latency alert policy, ONLY use seasonal decomposition to track
> Latency spikes. Alert policies using seasonal decomposition tracking both
> spikes and drops can falsely trigger alerts.

Compares the 5-minute latency to the average of 1-week and 1-day lookback
baselines.

```promql
histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[5m])) by (le, reasoning_engine_id))
/
(
  (
    histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[5m] offset 1d)) by (le, reasoning_engine_id))
    +
    histogram_quantile(0.95, sum(rate(aiplatform_googleapis_com:reasoning_engine_request_latencies_bucket[5m] offset 1w)) by (le, reasoning_engine_id))
  ) / 2
)
> 2
```

--------------------------------------------------------------------------------

## 2. Error Rate (SLO)

Always use Multi-Window Multi-Burn Rate SLOs. Z-score is not recommended due to
sparsity.

### Fast Burn SLO (1-Hour and 5-Minute Windows)

```promql
(
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{response_code!~"2.."}[5m])) by (reasoning_engine_id)
  /
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m])) by (reasoning_engine_id)
  > (1 - ${var.slo_target}) * 14.4
)
and
(
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{response_code!~"2.."}[1h])) by (reasoning_engine_id)
  /
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[1h])) by (reasoning_engine_id)
  > (1 - ${var.slo_target}) * 14.4
)
```

### Slow Burn SLO (3-Day and 6-Hour Windows)

```promql
(
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{response_code!~"2.."}[6h])) by (reasoning_engine_id)
  /
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[6h])) by (reasoning_engine_id)
  > (1 - ${var.slo_target}) * 1.0
)
and
(
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{response_code!~"2.."}[3d])) by (reasoning_engine_id)
  /
  sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[3d])) by (reasoning_engine_id)
  > (1 - ${var.slo_target}) * 1.0
)
```
