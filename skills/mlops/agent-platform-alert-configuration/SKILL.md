---
name: agent-platform-alert-configuration
description: 'Configures best-practice alerting policies for Google Cloud Vertex AI / Agent Platform agents on Agent Runtime. Use when analyzing, writing, or deploying alerting policies to monitor agent latency, error rates, and quality metrics (response quality, tool use, hallucination). Also use when provisioning online monitors for quality evaluation, or analyzing live metrics traffic footprints. NOTE: This skill currently only works for the Agent Runtime. Don''t use for configuring general GCP alert policies or non-agent GCP alerting policies.'
allowed-tools:
- terraform
- gcloud
- python
version: 1.0.0
author: google
license: Apache-2.0
platforms:
- linux
- macos
- windows
source: https://github.com/google/skills/tree/main/skills/cloud/agent-platform-alert-configuration
metadata:
  category: AiAndMachineLearning
  hermes:
    icon: lucide:bot
    tags:
    - Google Cloud
    - Agent
    - Platform
    - Alert
---

# Agent Platform Alert Configuration

This skill provides dynamic threshold alerting configurations for Google Cloud /
Vertex AI Reasoning Engines (Agent Platform container deployments) using
extended 1-week lookback retention baselines. Standard static thresholds (e.g.,
"latency > 2s") cause excessive alert noise for AI agents. Dynamic PromQL
baselines solve this.

## Safety & Confirmation Tiers (CRITICAL)

Before executing any commands or writing configurations on behalf of the user,
you MUST adhere to the following safety tiers based on the action requested:

1.  **Tier R: Read-only (`check_telemetry.py`)**
    *   **Rule**: No confirmation needed. You may execute these scripts
        immediately to inspect the telemetry status of the Reasoning Engine.
2.  **Tier B: Billing & Resource Creation (`create_online_monitor.py` /
    provisioning)**
    *   **Rule**: **Explicit User Confirmation Required**. These actions incur
        additional billing charges and create cloud resources. The agent MUST
        ask the user directly for approval before proceeding.

--------------------------------------------------------------------------------

## CRITICAL RULES

*   **Always configure both Reliability and Quality alerting policies** for the
    target agent (6 policies in total):
    *   **For Reliability Monitoring**: You MUST configure exactly three
        alerting policies:
        1.  **Latency** (anomaly monitoring)
        2.  **Error Rate - Fast Burn SLO** (1-Hour Window)
        3.  **Error Rate - Slow Burn SLO** (3-Day Window)
    *   **For Quality Monitoring**: You MUST configure exactly three alerting
        policies:
        1.  **Final Response Quality**
        2.  **Tool Use Quality**
        3.  **Hallucination**
*   **Online Monitor Provisioning & Cost Warning**: Quality alerting policies
    rely on metrics exported by Online Monitors. You MUST ensure the Online
    Monitor is provisioned for the agent and telemetry is enabled:
    -   [ ] **Ask for Approval**: Both Online Monitors and Telemetry incur
        separate billing charges. Before provisioning them, you MUST warn the
        user about these extra costs. If not pre-approved in the prompt, you
        MUST ask a direct question in your response requesting
        confirmation/approval to proceed (e.g., "Please confirm if you approve
        the extra billing costs for the Online Monitor and Telemetry to
        proceed.").
    -   [ ] **Verify Telemetry First**: Before generating any alerting policy
        plan or provisioning Online Monitors, you MUST always verify the
        telemetry status of the Reasoning Engine first using the
        `check_telemetry.py` script as detailed in
        [Verify Telemetry Status](#verify-telemetry-status) below.
    -   [ ] **Follow the Guide**: Follow the step-by-step instructions in the
        [Online Monitor & Telemetry Provisioning](#online-monitor--telemetry-provisioning)
        section below.
*   **Brand New Agents (No Traffic History)**: When setting up alerts for a
    brand new agent, you MUST explicitly ask the user what traffic pattern they
    expect (Steady, Seasonal, or Bursty) in your response. If immediate setup is
    requested, ask the question but proceed using the default Steady/Consistent
    (Short-Window Z-Score) pattern. Follow
    [no_historical_traffic_data.md](references/no_historical_traffic_data.md).
*   **PromQL for Reliability (No MQL or Threshold Filters)**: For the 3
    reliability metrics, you MUST use `condition_prometheus_query_language` with
    PromQL. Do **NOT** use MQL or standard `condition_threshold`.
*   **Standard Threshold Filters for Agent Quality**: For the 3 agent quality
    metrics, you MUST use standard `condition_threshold` filters matching the
    monitored resource type `aiplatform.googleapis.com/OnlineEvaluator` and
    metric type `aiplatform.googleapis.com/online_evaluator/scores`. Do **NOT**
    use PromQL.
*   **Install Terraform if Necessary**: You should use terraform to deploy and
    must install terraform if you can't find a valid install.
*   **Terraform Only**: Write the generated observability configuration ONLY as
    Terraform (`.tf`) files (e.g., `alerts.tf`, `variables.tf`).
*   **Dynamic Multi-Resource Alerting (No Single-Resource Pinning)**: You MUST
    NOT hardcode specific agent IDs or resource name filters (e.g.,
    `{reasoning_engine_id="[AGENT_ID]"}` or
    `metric.labels.agent_resource_name="[AGENT_NAME]"`) in alerting conditions
    unless explicitly requested. Alerting policies must be written to cover all
    active agents in the project dynamically:
    *   **For Reliability Metrics using PromQL**: ALWAYS use grouping
        aggregations (`by (reasoning_engine_id)`) instead of filtering to a
        single ID. This allows a single alert policy to dynamically track each
        reasoning engine instance separately.
    *   **For Quality Metrics using Standard Threshold Filters**: Omit the
        `agent_resource_name` filter entirely. Configure the condition filter to
        only target the monitored resource type
        (`aiplatform.googleapis.com/OnlineEvaluator`) and metric type
        (`aiplatform.googleapis.com/online_evaluator/scores`) globally for the
        project.
*   **Check for Pre-existing Policies**: Avoid creating duplicate alert policies
    for a reasoning engine: scan the target directory or workspace to see if a
    policy already exists that targets the same metrics using aggregations
    grouped by `reasoning_engine_id`.
*   **Metric Scope Discovery & Project Inference**: Centralize alert policies in
    a Metric Scope (scoping project) to save costs. Identify if a scope is used
    and where policies should live by checking:
    1.  **GCP CLI Check**: Run `gcloud beta monitoring metrics-scopes list
        projects/[PROJECT_ID]`. If a parent scope
        `locations/global/metricsScopes/[SCOPING_PROJECT_ID]` is returned, a
        Metric Scope is active; deploy policies there.
    2.  **Infrastructure as Code Scan**: Search Terraform configurations for
        `google_monitoring_monitored_project` resources and extract the scoping
        project from the `metrics_scope` attribute.
    3.  **Ambiguity Fallback**: If unable to determine, ask the user: "Are you
        using a multi-project Cloud Monitoring Metric Scope? If so, what is the
        scoping project ID?" Deploy policies to the deduced scoping project
        (setting the `project` attribute in HCL), or default to the local
        project.
*   **Directory Inference**: Deploy configuration files to target Terraform or
    SRE folders (e.g. `monitoring/`, `ops/`, `sre/`). Use tools to locate where
    alert policies or state pointers exist in the project, rather than blindly
    writing to the current working directory.
*   **Notification Channels**: By default, never configure any notification
    channels without user input. If the user explicitly provides a notification
    channel in their prompt, configure the alerts to use it. If no notification
    channel is provided, you MUST explicitly ask the user in your final response
    if they would like to configure notification channels. **This is a mandatory
    question and you MUST NOT omit it from your response.** **IMPORTANT** Do NOT
    make assumptions about notification channels. If you search the codebase for
    a notification channel you must ALWAYS confirm with the user before using
    it.
*   **Plain English Response**: You MUST include a plain English explanation for
    what the alerts do in your response. This must explain in plain English what
    the alert measures, how the algorithm works, and what a trigger indicates.
*   **Avoid Recursive Directory Operations**: You MUST NOT run recursive listing
    or search commands (such as `ls -R`, `find .`, or raw recursive `grep`) from
    the google3 workspace root, as this will hang your session. Always target
    specific subdirectories.
*   **Background Task Cleanup**: You MUST check the status of all background
    tasks that you spawn. Before completing your execution and returning your
    final response, you MUST terminate or kill any active or hanging background
    tasks (using the `manage_task` tool with action `kill`).

--------------------------------------------------------------------------------

## Algorithm Selection & Policy Mapping Process

Alerting policies for reasoning engine agents MUST map to the correct algorithms
to ensure statistical stability and prevent alert noise or blind spots based on
data classes:

*   **Latency**: Follows workload traffic pattern (Steady -> Z-Score; Seasonal
    -> Seasonal Decomposition; Bursty -> Moving Averages).
*   **Error Rate**: ALWAYS use **Multi-Window Multi-Burn Rate SLOs** (or
    ratio-based static thresholds). Error rate is naturally sparse (normally
    `0`). When standard deviation is `0`, Z-score computation is mathematically
    unstable (division-by-zero or NaN), causing false alert storms.

To resolve the workload traffic pattern (Seasonal, Steady, or Bursty), follow
the instructions corresponding to the availability of historical metrics data:

*   **Case 1: No historical metrics data available (e.g., brand new agent)**:
    You MUST read and follow:
    [no_historical_traffic_data.md](references/no_historical_traffic_data.md)
*   **Case 2: Historical metrics data available (e.g., active agent with
    traffic)**: You MUST read and follow:
    [has_historical_traffic_data.md](references/has_historical_traffic_data.md)

--------------------------------------------------------------------------------

## Telemetry Metrics and PromQL Examples

All raw telemetry metrics for the Agent Platform are cumulative **counters**.
Because we monitor their rates or quantiles, we can optimize the PromQL queries
by using longer range windows (e.g., `[1w]`) for historical averages instead of
expensive `avg_over_time` subqueries.

Signal         | Raw Metric                                  | Type    | Description
:------------- | :------------------------------------------ | :------ | :----------
**Latency**    | `reasoning_engine_request_latencies_bucket` | Counter | Histogram bucket of request latencies
**Error Rate** | `reasoning_engine_request_count`            | Counter | Cumulative count of requests

--------------------------------------------------------------------------------

For the specific PromQL queries corresponding to each algorithm, you MUST read
and follow: [promql_queries.md](references/promql_queries.md)

--------------------------------------------------------------------------------

## Agent Quality Metrics (Online Monitor)

All agent quality evaluation metrics are exported by Online Monitors to the
monitored resource type `aiplatform.googleapis.com/OnlineEvaluator` under the
metric type `aiplatform.googleapis.com/online_evaluator/scores`.

### Metric Details & Aligners

Because the scores metric is of value type `DISTRIBUTION`, standard mean-based
PromQL or arithmetic `ALIGN_MEAN` aligners are unsupported. You MUST use a
percentile aligner (typically `ALIGN_PERCENTILE_50` to evaluate the median
score) within the `aggregations` block of your `condition_threshold`.

Signal                           | Metric Name (`evaluation_metric_name`) | Target Threshold    | Recommended Aligner
:------------------------------- | :------------------------------------- | :------------------ | :------------------
**Final Response Quality**       | `final_response_quality_v1`            | `< 0.8` (or custom) | `ALIGN_PERCENTILE_50`
**Tool Use Quality**             | `tool_use_quality_v1`                  | `< 0.8` (or custom) | `ALIGN_PERCENTILE_50`
**Hallucination (Groundedness)** | `hallucination_v1`                     | `< 0.9` (or custom) | `ALIGN_PERCENTILE_50`

### Metric Filter Example

When configuring a quality alert policy in Terraform, use the following filter
expression structure:

```filter
resource.type="aiplatform.googleapis.com/OnlineEvaluator"
AND metric.type="aiplatform.googleapis.com/online_evaluator/scores"
AND metric.labels.evaluation_metric_name="[METRIC_NAME]"
```

### Online Monitor & Telemetry Provisioning

Quality metrics are generated by the Online Monitor by evaluating trace data
exported to Cloud Trace. If telemetry is disabled on the reasoning engine, no
traces are sent, and the quality metrics will remain empty.

#### Prerequisites & Dependencies

Before executing any scripts in this skill (such as `check_telemetry.py` or
`create_online_monitor.py`), you MUST install the required dependencies in your
environment. Run this command first:

```bash
pip install -r scripts/requirements.txt
```

#### Verify Telemetry Status

Before generating any alerting policies, proposing a plan, or provisioning
Online Monitors, you MUST always check if the agent is ready to export traces by
running the telemetry checking script:

*   **Mandatory Command**: `python3 scripts/check_telemetry.py --project-id
    "[PROJECT_ID]" --agent-resource-name "[AGENT_RESOURCE_NAME]"`
    *   **Note on Parameters**: The `[AGENT_RESOURCE_NAME]` parameter MUST be
        the full resource path format
        `projects/<project_id>/locations/<location>/reasoningEngines/<agent_id>`
        (e.g. `projects/gcp-prod/locations/us-central1/reasoningEngines/556677`)
        and not just the agent ID itself.
    *   **Dependency Failures**: If package imports or dependency installation
        fails, try your best to resolve the issues (e.g., by verifying package
        installation) and run the script again with the specific project-id and
        agent-resource-name parameters. If you cannot run the script
        successfully due to missing dependencies, you MUST still attempt to run
        it first and then include the complete, pre-populated execution command
        in your final response as a verification plan (this applies even if the
        user has pre-approved provisioning).
*   **Detailed Enablement Instructions**: For details on the required
    environment variables, Terraform setups, and project dependencies, you MUST
    read and follow:
    [telemetry_enablement.md](references/telemetry_enablement.md).

#### Provision the Online Monitor

Because Online Monitors cannot be configured via Terraform, run the provisioning
script to generate the required metrics:

*   **Command**: `python3 scripts/create_online_monitor.py --project-id
    "[PROJECT_ID]" --agent-resource-name "[AGENT_RESOURCE_NAME]"
    [--sampling-percentage [PERCENTAGE]]`
*   **Sampling Rate Recommendation**: For production agents, configure a
    conservative sampling percentage (default: **10%**) to control LLM
    evaluation costs. For details, refer to
    [Continuous evaluation with online monitors](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-online).

#### Formatting the Execution Plan

If execution fails (e.g. due to sandbox restrictions or permissions), you MUST
plan it as a concrete next step. To do this, you MUST explicitly include a
section titled **"Online Monitor Provisioning Plan"** or **"Execution Plan"** in
your final response, containing the exact concrete python execution command with
all parameter values (such as project ID, region, and agent resource name) fully
populated. Do not merely state that the user should run it.

You MUST format the plan exactly as follows:

### Execution Plan: Online Monitor Provisioning

**Online Monitor Provisioning Command:**

```bash
python3 scripts/create_online_monitor.py \
  --project-id "[PROJECT_ID]" \
  --agent-resource-name "projects/[PROJECT_ID]/locations/[LOCATION]/reasoningEngines/[AGENT_ID]" \
  --sampling-percentage [PERCENTAGE]
```

**Verify Telemetry Command (Optional fallback):**

```bash
python3 scripts/check_telemetry.py \
  --project-id "[PROJECT_ID]" \
  --agent-resource-name "projects/[PROJECT_ID]/locations/[LOCATION]/reasoningEngines/[AGENT_ID]"
```

--------------------------------------------------------------------------------

## Tooling Scripts

Use the following scripts to resolve duplicates and validate configs before
presenting or applying Terraform changes:

1.  **Duplicate Check & Merge**: Checks for pre-existing alerts in the target
    folder to ensure changes are merged in-place rather than appended:
    *   Command: `python3 scripts/validate_config.py --directory [TARGET_TF_DIR]
        --engine-var "${var.reasoning_engine_id}"`
2.  **Config Linting**: Validates PromQL grammar, matching engine labels, and
    HCL structure:
    *   Command: `python3 scripts/validate_config.py --file [PATH_TO_TF_FILE]`
    *   **Self-Correction Loop**: If validation fails (exits non-zero or outputs
        errors), you MUST read the command output, locate the line/file
        containing the lint error, analyze the PromQL syntax or Terraform HCL
        issue, apply adjustments in-place, and re-run the `validate_config.py
        --file` validation. Repeat this loop until the validation script passes
        successfully.

--------------------------------------------------------------------------------

## Gotchas & Behavioral Corrections

*   **Duration Buffers (Transient Glitches)**: To avoid alerts firing on
    transient spikes, use duration/retest window buffers appropriately:
    *   **Reliability Metrics (PromQL / Cloud Monitoring)**:
        *   For short-lookback alerts querying data under 25 hours (e.g.,
            Short-Window Z-Score, Moving Averages, Fast Burn SLO), ALWAYS use a
            `duration = "300s"` (5 minutes) buffer to filter out transient cold
            start/deployment spikes.
        *   For long-lookback alerts querying data longer than 25 hours (e.g.,
            Long-Window Z-Score, Seasonal Decomposition, Slow Burn SLO),
            duration/retest windows are disabled by the platform. You must **not
            set a duration** (omit it entirely).
    *   **Quality Metrics (Standard Filters / Online Monitor)**:
        *   Always use a `duration = "300s"` (5 minutes) buffer to filter out
            transient scoring dips or evaluation outliers caused by temporary
            LLM judge congestion, or edge-case query outliers.
*   **Dynamic Baseline Adaptation Blind Spot**: Explain to users that dynamic
    statistical Z-score thresholds compare current rates to a moving statistical
    baseline. If a system degrades slowly over days, the standard baseline curve
    adapts to this slow drift, making standard Z-score alerts blind to
    persistent slow errors. Recommend a hard static threshold alert in parallel
    for strict SLA enforcement.
*   **Seasonal Decomposition Double Alerting**: The agent MUST ONLY configure
    seasonal decomposition alert policies to track spikes (e.g., latency spikes)
    OR drops AND MUST NOT use dual-direction checks (like absolute deviation).
    Explain this limitation to the user: comparing to a historical offset (e.g.,
    `offset 1w`) the alert policy triggers twice if tracking both directions
    (once for the anomaly, and once 1 week later when the anomaly becomes the
    baseline). To prevent this, the generated policy MUST only track either
    spikes (using `>`) or drops (using `<`), avoiding using `abs()`.
*   **Raw Error Boundaries**: Explain that raw error counts or absolute failed
    request count boundaries do not scale under changing traffic throughput.
    Recommend ratio-based error rate alerts instead.
*   **Safe Threshold Modulation E2E Validation**: When verifying a dynamic
    metric threshold policy end-to-end, do NOT attempt to force real platform
    errors. Instead, deploy the alert policy with standard safe bounds (Z-score
    multiplier > 15), then temporarily update standard deviation Z-score limits
    to a negative value (e.g. > -3) to trigger/verify the "Firing" state before
    reverting. Always get confirmation before taking this action proactively.
*   **Expected Script Failures**:
    *   `validate_config.py --directory` exiting with code 1: Parse the JSON
        output for duplicate resource targets. Perform in-place upgrade edits,
        then re-check until it passes with 0.
    *   **Script Execution Failures & Self-Correction**: If the execution of
        utility scripts (such as `check_telemetry.py`,
        `create_online_monitor.py`, or `analyze_traffic.py`) fails unexpectedly,
        you MUST read and inspect the stdout/stderr logs or error output.
        Analyze the error message (e.g., connection timeouts, invalid
        permissions, or missing resources) and attempt to dynamically correct
        parameters (such as verifying or correcting the region, project ID, or
        resource name format) and retry execution before escalating or falling
        back to manual plans.
*   **Distribution Metric Aligner Constraint**: Standard `ALIGN_MEAN` cannot be
    applied to `DELTA` distribution metrics like `online_evaluator/scores`. You
    MUST use percentile-based aligners (like `ALIGN_PERCENTILE_50`) to reduce
    the score distribution into a comparable numeric stream.

--------------------------------------------------------------------------------

## Supporting Links

*   [Continuous evaluation with online monitors](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-online)
*   [Agent Platform Quality Metrics](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/rubric-metric-details)
*   [Google Cloud Alerting Policies Guide](https://cloud.google.com/monitoring/alerts)
*   [Google Cloud Monitoring PromQL Documentation](https://cloud.google.com/monitoring/promql)
