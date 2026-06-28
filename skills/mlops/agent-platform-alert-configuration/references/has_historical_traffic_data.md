# Has Historical Traffic Data Available

Use these instructions if the agent has historical metrics data available:

## 1. Run Traffic Analyzer Script

-   Run the `analyze_traffic.py` script to classify the metrics traffic pattern
    profile using one of the following commands:
    -   **Live Query**: `python3 scripts/analyze_traffic.py --live --project-id
        [PROJECT_ID] --reasoning-engine-id [REASONING_ENGINE_ID]`
    -   **Metrics File**: `python3 scripts/analyze_traffic.py --metrics-file
        [PATH_TO_JSON]`
-   **Handling Tool Failures**: If the `--live` command fails with
    `CredentialsMissingError` (exit code 1), report the error and instruct the
    user to run `gcloud auth application-default login` on their terminal.
-   Map the traffic pattern profile classified by the script to **Latency**:
    -   **Steady**: Maps to **Long-Window Z-Score Baseline (1-week lookback)**
        (safe since the script verified we have at least 14 days of history).
    -   **Seasonal**: Maps to **Seasonal Decomposition** (average 1w and 1d).
    -   **Bursty**: Maps to **Moving Averages** (1h baseline).

#### Decision Mapping Reference:

| Variance Ratio   | Autocorrelation | Traffic        | Assigned Latency       |
: (std_dev / mean) : (1-week lag)    : Classification : Algorithm & baseline   :
| :--------------- | :-------------- | :------------- | :--------------------- |
| `≤ 2.0`          | `≤ 0.75`        | **Steady**     | Long-Window Z-Score    |
:                  :                 :                : (1-week lookback)      :
| `≤ 2.0`          | `> 0.75`        | **Seasonal**   | Seasonal Decomposition |
:                  :                 :                : (1w & 1d avg)          :
| `> 2.0`          | Any / Not       | **Bursty**     | Moving Averages        |
:                  : Applicable      :                : (1-hour window)        :

*Example classifications:*

-   *Steady*: Low variance traffic (e.g. steady QPS) with little or no weekly
    cyclical pattern.
-   *Seasonal*: Clear daily/weekly repeating patterns with high weekly
    correlation (e.g. daily peak traffic).
-   *Bursty*: Highly volatile traffic with rapid spikes and quiet periods (e.g.
    batch job workloads).

-   **Fallback for Insufficient Data / No Traffic**:

    -   If the script fails with a `ValueError` indicating insufficient data
        points (less than 14 days of history), or if it outputs "New Agent / No
        Traffic" (inactive agent), you MUST fallback to the user inquiry
        instructions in
        [no_historical_traffic_data.md](no_historical_traffic_data.md) to ask
        the user for the expected traffic pattern.

-   Regardless of the script's output profile, the other policies MUST use their
    correct data-class defaults:

    -   **Error Rate**: ALWAYS use **Multi-Window Multi-Burn Rate SLO Alerting**
        (or ratio-based static limits).

## 2. User Notification

Clearly communicate the findings and selection at the start of your response:

1.  Explain the classified traffic profile (Seasonal, Steady, or Bursty) output
    by the metrics analysis script (citing indicators like standard deviation,
    autocorrelation, or zero-ratio from the script output). If falling back to
    user inquiry due to zero metrics or insufficient data, explain that.
2.  Propose the corresponding alerting policy mapping (Latency matching the
    traffic profile, Error Rate using SLO Burn Rate).
3.  Ask the user if this expected profile mapping is correct or if they would
    like to customize standard deviation thresholds.
4.  Provide a brief plain-English explanation of what each of the proposed
    alerts measures and how the underlying algorithms work and what they
    actually measure. Keep this explanation in the conversational response text.
