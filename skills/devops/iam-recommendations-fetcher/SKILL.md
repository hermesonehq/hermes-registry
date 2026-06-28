---
name: iam-recommendations-fetcher
description: Fetches raw IAM recommendations and associated security insights from Google Cloud for a specified target scope (Organization, Folder, or Project). Use when you need to retrieve security recommendations before analyzing or applying them. Don't use for applying/acting on recommendations (use the recommendation applier skill) or for general allow policy querying (use the allow policy viewer skill).
version: 1.0.0
author: google
license: Apache-2.0
platforms:
- linux
- macos
- windows
source: https://github.com/google/skills/tree/main/skills/cloud/iam-recommendations-fetcher
metadata:
  category: Identity
  hermes:
    icon: lucide:cloud
    tags:
    - Google Cloud
    - Iam
    - Recommendations
    - Fetcher
---

# IAM Recommendations Retrieval

This skill provides instructions for fetching IAM recommendations and insights
from Google Cloud. It covers validating the input target scope, retrieving
recommendations using MCP tools, gcloud commands, or direct API calls, and
handling common API errors.

## Procedures

### 1. Validate Input Target

Verify the input target scope.

1.  **Check Format**: Check if the target matches one of these formats:

    *   `organizations/{org_id}`
    *   `folders/{folder_id}`
    *   `projects/{project_id}`

2.  **Handle Ambiguous/Raw Target**: If the user provides only a raw ID (without
    the prefix):

    *   **Alphanumeric (starts with a letter)**: Assume it is a Project ID.
        Format it as `projects/{project_id}` and proceed.
    *   **Purely Numeric**: It is ambiguous (could be Organization, Folder, or
        Project Number).
        *   Ask the user to clarify the resource type: > "Is the target ID
            '{provided_id}' an Organization, a Folder, or a Project?"
        *   Once the user specifies, format the target scope accordingly (e.g.,
            prepend `organizations/`, `folders/`, or `projects/`) and proceed.
        *   If the user's response is invalid or they cannot clarify, treat it
            as an error and proceed to [Handle Errors](#5-handle-errors)
            (incorrect target).

3.  **Handle Project Numbers**: If the target is a project but uses a purely
    numeric ID (Project Number) instead of a Project ID (e.g.,
    `projects/123456789`):

    *   `gcloud` recommender commands require a Project ID. Attempt to resolve
        the Project Number to a Project ID using: `gcloud projects list
        --filter="projectNumber={project_number}" --format="value(projectId)"`
    *   If this resolution returns empty or fails with a permission error, do
        not attempt to describe the project, search the codebase, or search for
        mock data. Immediately return the standardized error JSON specified in
        [Handle Errors](#5-handle-errors) and stop execution (do not call any
        more tools).

4.  **Record Validation**: Explicitly state the validated and formatted target
    scope (e.g., `projects/123456789` or `organizations/123456789012`) in your
    thought/reasoning before proceeding to the fetch step.

### 2. Fetch Recommendations and Insights (Fallback Flow)

Attempt the following retrieval methods in order. Stop at the first success.

**CRITICAL: Fail Fast on Errors** (To avoid redundant API calls that will fail
for the same authorization/permission reasons): If any attempted method (Option
A or Option B) fails with an API-level error (such as `PERMISSION_DENIED`,
`UNAUTHENTICATED`, or resource `NOT_FOUND` / does not exist) or a CLI validation
error (such as project number not allowed), **do NOT attempt any further
options** (including Option C or direct API/curl calls). Stop immediately, do
not call any more tools, and return the standardized error JSON as specified in
the "Handle Errors" section.

#### Option A: MCP Tool (Preferred)

Use the MCP tool if available. MCP tools are designed for efficient, secure
execution within Google's internal environments, often providing streamlined
authentication and better integration compared to general-purpose CLI commands.

If an IAM Recommender MCP tool is available in your context:

*   Call the tool with the `target` parameter.

#### Option B: gcloud CLI (First Fallback)

If MCP is unavailable, use `run_command` to execute the following (replace
variables accordingly):

Target                            | Flag
:-------------------------------- | :---------------------------------
`projects/{project_id}`           | `--project={project_id}`
`folders/{folder_id}`             | `--folder={folder_id}`
`organizations/{organization_id}` | `--organization={organization_id}`

**Commands to run**:

```bash
GCLOUD_COMMON_FLAGS="--format=json --location=global \
--filter=stateInfo.state=ACTIVE"

# 1. Fetch Recommendations
gcloud recommender recommendations list \
--recommender=google.iam.policy.Recommender $GCLOUD_COMMON_FLAGS {mapped_flag}

# 2. Fetch Insights
gcloud recommender insights list --insight-type=google.iam.policy.Insight
$GCLOUD_COMMON_FLAGS {mapped_flag}
```

#### Option C: Google Cloud API (Final Fallback)

Only attempt this option if `gcloud` is physically unavailable in the
environment (e.g., `gcloud: command not found`). API client libraries require
more setup and execution overhead, so they are only used as a last resort if CLI
tools are missing. Do NOT use this option if `gcloud` is available but failed
with an API error.

Use Google Cloud Recommender API client libraries via a helper script (or direct
API calls if libraries are unavailable) to:

1.  Call `list_recommendations` (or `recommendations.list`) for
    `google.iam.policy.Recommender` (filter: `stateInfo.state=ACTIVE`).
2.  Call `list_insights` (or `insights.list`) for `google.iam.policy.Insight`
    (filter: `stateInfo.state=ACTIVE`).

### 3. Determine Output Format and Deliver

**CRITICAL**: Only proceed to this step if the retrieval in Step 2 was
successful. If the retrieval failed, skip this step and go directly to
[Handle Errors](#5-handle-errors).

Before presenting the results, determine the desired output format.

**CRITICAL**: If the user's initial prompt already specifies the output format
(e.g., "return the raw results in JSON" or "show it in a table"), bypass asking
and proceed directly to that format.

Otherwise, ask the user in a dropdown menu, with the options being:

1.  JSON file
2.  Markdown table in chat

Based on the choice (either pre-specified or chosen by the user), deliver the
output:

#### Option A: JSON File

1.  Write the raw results to a file named
    `iam_recommendations_<target_id>_<timestamp>.json` (where `<target_id>` is
    the sanitized resource identifier and `<timestamp>` is formatted as
    `YYYYMMDD_HHMMSS`) in the current working directory.
2.  The file content must match the structure shown in
    [Example Execution](#4-example-execution).
3.  Respond to the user with the file path.

#### Option B: Chat Table

1.  **Sort Recommendations**: Sort the retrieved recommendations, placing
    service agent recommendations last in the list.
2.  **Format Table**: Format the sorted recommendations into a markdown table.
    The table should contain key fields:
    -   **Subtype**: The recommender subtype or insight subtype (e.g.,
        indicating if it's for resource-level roles).
    -   **Recommended Action**: Summary of the recommendation.
    -   **Rationale**: Rationale/justification.
    -   **Associated Insights**: The IDs of any linked insights (from
        `associatedInsights`).
3.  **Limit Chat Display**: Display only the top 10 recommendations in the chat
    table.
4.  **Provide Full List**: Save the complete list of recommendations and
    insights to a markdown file (e.g.,
    `iam_recommendations_<target_id>_<timestamp>.md`, where `<target_id>` is the
    sanitized resource identifier and `<timestamp>` is formatted as
    `YYYYMMDD_HHMMSS`) and provide a link for the user to download it.
5.  **Format Insights Table**: If insights are present, format them in a
    separate table in the markdown file (and optionally show a summary in chat
    if appropriate, but keep the chat clean). The table should contain key
    fields:
    -   **Insight ID**: The insight identifier (`INSIGHT_ID`).
    -   **State**: The insight state (`INSIGHT_STATE`).
    -   **Subtype**: The insight subtype (`INSIGHT_SUBTYPE`).
    -   **Description**: Description of the insight (`DESCRIPTION`).
6.  **DO NOT** provide a JSON file with the raw results if this option is
    chosen.

### 4. Example Execution

*   **Input Target**: projects/my-test-project
*   **Mapped Flag**: --project=my-test-project
*   **Action (Option B)**: Run `gcloud recommender recommendations list
    --recommender=google.iam.policy.Recommender --format=json --location=global
    --filter=stateInfo.state=ACTIVE --project=my-test-project`
*   **Expected Output Structure**:

    ```json
    {
      "raw_results": {
        "recommendations": [
          {
            "name": "projects/my-test-project/locations/global/recommenders/ \
            google.iam.policy.Recommender/recommendations/123",
            "content": { ... }
          }
        ],
        "insights": []
      },
      "error": null
    }
    ```

### 5. Handle Errors

**CRITICAL**: If you encounter any of the error conditions below (during
validation or fetch), **stop immediately**. Do not attempt to debug, switch
accounts, search the codebase, or verify resource existence. Immediately output
the specified JSON structure as your final response and call no further tools.

If all methods fail, return:

*   For incorrect target: `{"raw_results": null, "error": "The specified target
    resource is incorrect or does not exist."}`
*   For authentication issues: `{"raw_results": null, "error": "User is
    unauthenticated. Please authenticate (e.g., run 'gcloud auth login')."}`
*   For permissions: `{"raw_results": null, "error": "Insufficient permissions.
    Please ensure you have 'roles/recommender.iamViewer' on the target scope."}`
*   Other: `{"raw_results": null, "error": "Failed to fetch: {error_details}"}`
    (Do not mention MCP tool failures to the user).

## Gotchas

*   **State Filter**: Always ensure you are filtering for `ACTIVE`
    recommendations.
*   **Location**: The location for IAM Recommender is always global.
