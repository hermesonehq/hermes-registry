---
name: agent-platform-inference
description: Connects to and performs inference with Google Cloud Agent Platform GenAI models, including First-Party Gemini models and Third-Party OpenMaaS models (Llama, DeepSeek, Qwen, etc.). Use when you need to generate code for calling Gemini or OpenMaaS models, authenticate with GenAI SDK, OpenAI SDK, or legacy Agent Platform SDK, configure base URLs and global/regional endpoints, or troubleshoot 429 Resource Exhausted (DSQ), 400 User Validation, or 404 Not Found errors. Don't use for deploying models to endpoints or for running model evaluations.
version: 1.0.0
author: google
license: Apache-2.0
platforms:
- linux
- macos
- windows
source: https://github.com/google/skills/tree/main/skills/cloud/agent-platform-inference
metadata:
  category: AiAndMachineLearning
  hermes:
    icon: lucide:bot
    tags:
    - Google Cloud
    - Agent
    - Platform
    - Inference
---

# Agent Platform GenAI Inference Skill

This skill provides instructions for authenticating and connecting to Google
Cloud Agent Platform to use Generative AI models. It covers both First-Party
(Gemini) and Third-Party (OpenMaaS) models.

## Safety & Confirmation Tiers (CRITICAL)

Before executing any commands or scripts on behalf of the user, you must adhere
to the following safety tiers based on the action requested. (The skill is
read-only; other safety tiers are omitted):

1.  **Tier R: Read-only / Inference (`client.models.generate_content`, `client.chat.completions.create`, `client.completions.create`, `client.embeddings.create`)**
    *   Requires **interactive confirmation** with 'Yes'/
    'No' options before executing model inference on
    behalf of the user, to prevent unexpected cost or
    quota consumption. The confirmation prompt must
    clearly explain the proposed inference execution and
    its key parameters (e.g., target model ID, SDK
    choice, input prompt). Natural-language paraphrases
    without specifying the parameters are NOT sufficient.
    *   **Same-turn restriction**: Do not execute the
    inference scripts or commands in the same turn as
    presenting the confirmation prompt. Stop and wait
    for the user's reply; only execute after explicit
    'Yes' / approval.
    *   **Gold Standard Example**:
        > I will perform model inference with the following parameters. Please
        > confirm this information before I proceed:
        > *   **Model ID**: `deepseek-ai/deepseek-v3.2-maas`
        > *   **SDK**: OpenAI SDK (via Vertex AI Endpoint)
        > *   **Input Prompt**: "Explain the concept of quantum computing..."
        > Do you confirm? [Yes/No]

## Phase 0: Environment Setup

**CRITICAL**: Before running any of the Python sample scripts in the `scripts/`
directory (e.g., `scripts/openmaas_openai_sdk.py`), you MUST ensure the
environment is correctly initialized by following these steps:

1.  **Google Cloud Authentication**: Authenticate with your Google Cloud
    credentials and configure active Application Default Credentials (ADC) for
    Agent Platform access:
    
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
2.  **Enable API** (if not already enabled):
    
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```
3.  **Virtual Environment**: Create and activate a dedicated local virtual
    environment:
    
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4.  **Install Dependencies**: Install the required SDKs:
    
    ```bash
    pip install -r scripts/requirements.txt
    ```
5.  **Verify Setup (Optional)**: Run all sample scripts at once to verify the
    environment is working end-to-end:
    
    ```bash
    ./scripts/verify_all.sh
    ```
6.  **Execution**: Advise the user that every time they execute a Python
    snippet from this skill, they must ensure this virtual environment is
    activated first.

<!-- disableFinding(LINE_OVER_80) -->

> [!IMPORTANT]
> **CRITICAL: Model IDs & Availability**
> *   **Gemini Models**: See [Gemini Models][gemini-models-docs] for valid
>     Model IDs and Regions.
> *   **OpenMaaS Models**: See [Use Open Models on Agent Platform]
>     (https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)
>     for Llama, DeepSeek, Qwen, etc.
> *   **Incomplete Lists**: The Model IDs listed in this skill are **examples
>     only** and may be incomplete or outdated.
> *   **Action**: Always verify the Model ID and Region using the links above
>     before generating code.
>
> [gemini-models-docs]: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate
<!-- enableFinding(LINE_OVER_80) -->
## Workflow Decision Tree

1.  **Model Family Identification**: Has the user specified whether they want
    to call a **Gemini** (First-Party) model or an **OpenMaaS** (Third-Party,
    e.g. Llama, DeepSeek, Qwen) model?

    *   **No** -> Ask the user which model family they want to use. If they
        provide a specific model name, infer the family from the name.
    *   **Yes** -> Proceed to Step 2.

2.  **SDK Choice**: Which SDK does the user want to use?

    *   **Gemini + GenAI SDK** (preferred for Gemini) -> Proceed to
        [1. Gemini Models].
    *   **Gemini + legacy Vertex AI SDK** -> Proceed to [1. Gemini Models].
    *   **OpenMaaS + OpenAI SDK** (preferred for OpenMaaS) -> Proceed to
        [2. OpenMaaS Models].
    *   **OpenMaaS + GenAI SDK** -> Proceed to [2. OpenMaaS Models].
    *   **Unsure** -> Default to the preferred SDK for the chosen family.

3.  **Troubleshooting**: Is the user reporting an error (429 Resource
    Exhausted, 400 User Validation, 404 Not Found, etc.)?

    *   **Yes** -> Proceed to [3. Troubleshooting & Common Error Codes].
    *   **No** -> Proceed with the SDK choice from Step 2.

## 1. Gemini Models

For Gemini models (e.g., `gemini-2.5-pro`, `gemini-3-flash-preview`), the
**GenAI SDK** (`google-genai`) is the **PREFERRED** method. The legacy
`vertexai` SDK is still supported but GenAI SDK is recommended for new projects.

> [!IMPORTANT]
> **Preview Models (including Gemini 3.1)** are often **ONLY** available in the
> `global` region. Stable models are available in `us-central1` and other
> regions.

### Choosing the Right SDK

*   **Gemini Models**: **GenAI SDK** (`google-genai`) is **PREFERRED**. Use OpenAI SDK for compatibility, or Legacy SDK (`vertexai`) if needed.
*   **OpenMaaS Models**: **OpenAI SDK** is **HIGHLY RECOMMENDED**. Use GenAI SDK or Legacy SDK if you have specific infrastructure requirements.

### Installation

```bash
pip install google-genai
```

### Python Example (GenAI SDK - Preferred)

See [`scripts/gemini_genai_sdk.py`](scripts/gemini_genai_sdk.py) for the
complete code.

### Alternative: OpenAI SDK (Chat Completions)

Use the standard OpenAI SDK with the Agent Platform endpoint. This is great for
cross-compatibility.

See [`scripts/gemini_openai_sdk.py`](scripts/gemini_openai_sdk.py) for the
complete code.

### Legacy: Agent Platform SDK

The legacy `vertexai` SDK is still widely used but `google-genai` is preferred
for new Gemini projects.

See [`scripts/gemini_vertexai_sdk.py`](scripts/gemini_vertexai_sdk.py) for the
complete code.

**Documentation**: [Google GenAI SDK](https://github.com/googleapis/python-genai)

**Documentation**: [Agent Platform Gemini Models](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

## 2. OpenMaaS Models (Llama, DeepSeek, Qwen, etc.)

For OpenMaaS (Model-as-a-Service) models, the **HIGHLY RECOMMENDED** approach is
to use the standard **OpenAI SDK** with a specific Vertex AI endpoint.

> [!WARNING]
> While `GenerativeModel` *can* support some OpenMaaS models, it is
**discouraged**. Use the OpenAI SDK for best compatibility (especially for Chat
Completions).

### Installation

```bash
pip install openai google-auth
```

### Authentication for OpenAI SDK

You **MUST** use a Google Cloud OAuth access token as the API key for the OpenAI
SDK.

```python
import google.auth
from google.auth.transport.requests import Request

def get_gcp_access_token():
    creds, _ = google.auth.default()
    creds.refresh(Request())
    return creds.token
```

> [!NOTE]
> Google Cloud access tokens typically expire after 1 hour. The
> `get_gcp_access_token()` function above retrieves a *fresh* token at the time
> it is called.
<!-- disableFinding(LINE_OVER_80) -->
> For long-running applications, you implement a refresh mechanism. See [Refresh the access token](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate/openai/auth-and-credentials?hl=en#refresh_your_credentials) for details.
<!-- enableFinding(LINE_OVER_80) -->

### Configuration (Base URL)

<!-- disableFinding(LINE_OVER_80) -->

-   **Global Endpoint** (Recommended for most models requiring global
    availability):
    `https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/endpoints/openapi`
-   **Regional Endpoint**:
    `https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi`
    <!-- enableFinding(LINE_OVER_80) -->

### Python Example (OpenMaaS - Chat Completions)

See [`scripts/openmaas_openai_sdk.py`](scripts/openmaas_openai_sdk.py) for the
complete code.

> [!TIP]
> **Alternative: Environment Variables**
> You can set environment variables in your shell instead of updating the code.
>
> ```bash
> export OPENAI_BASE_URL="https://aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/global/endpoints/openapi"
> export OPENAI_API_KEY="$(gcloud auth print-access-token)"
> ```
> Then initialize the client without arguments: `client = OpenAI()`

### Python Example (OpenMaaS - Completions API)

The following models support the legacy Completions API: `zai-org/glm-5-maas`,
`moonshotai/kimi-k2-thinking-maas`, `minimaxai/minimax-m2-maas`,
`deepseek-ai/deepseek-v3.1-maas`, and `deepseek-ai/deepseek-v3.2-maas`.

```python
response = client.completions.create(
    model="deepseek-ai/deepseek-v3.2-maas",
    prompt="Once upon a time",
    max_tokens=100
)
print(response.choices[0].text)
```

### Python Example (OpenMaaS - Embeddings)

```python
# Verify specific Embedding Model ID on Model Garden (e.g., intfloat/multilingual-e5-small)
response = client.embeddings.create(
    model="intfloat/multilingual-e5-large-maas",
    input="The quick brown fox jumps over the lazy dog",
)
print(response.data[0].embedding)
```

### Alternative: GenAI SDK

The `google-genai` SDK can also access OpenMaaS models via the `vertexai`
backend.

See [`scripts/openmaas_genai_sdk.py`](scripts/openmaas_genai_sdk.py) for the
complete code.

> [!IMPORTANT]
> **Model ID Format**: For GenAI SDK with OpenMaaS, you **MUST** use the full
> path: `publishers/PUBLISHER/models/MODEL` (e.g.,
> `publishers/zai-org/models/glm-5-maas`).

### Legacy: Agent Platform SDK (OpenMaaS)

For OpenMaaS, you can also use `GenerativeModel` (if supported).

See [`scripts/openmaas_vertexai_sdk.py`](scripts/openmaas_vertexai_sdk.py) for
the complete code.

> [!IMPORTANT]
> **Model ID Format**: For Agent Platform SDK with OpenMaaS, you **MUST** use the
> full path: `publishers/PUBLISHER/models/MODEL`.

### Model Reference & Availability

**Documentation**: [Use Open Models on Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)

> [!TIP]
> **Self-Deployment for Control**: If you need **dedicated hardware**
> (GPUs/TPUs), **guaranteed capacity**, or **specific regional placement** not
> offered by MaaS, you can **Self-Deploy** these models to Agent Platform
> Endpoints. Search for the model in Model Garden and click "Deploy" to select
> your machine type.

> [!IMPORTANT]
> **Finding Inference Examples**: The list above is a starting point. For the
> **definitive** inference snippets (especially for Chat Completions payload
> structure):
> 1.  Consult the [Use Open Models on Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)
>     list.
> 2.  Click the link for your specific model (e.g., "DeepSeek-V3") to visit its
>     **Model Garden** page.
> 3.  Look for the **"Sample Code"** or **"Use this model"** button on the Model
>     Garden page to get the exact `curl` or Python code for that specific model
>     version.

> [!NOTE]
> This list is **INCOMPLETE**. See [Use Open Models on Agent Platform]
> (https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)
> for the full list of supported models.

| Model Family | Model ID Examples | Location | Notes |
| :--- | :--- | :--- | :--- |
| **Llama 4** | `meta/llama-4-maverick-17b-128e-instruct-maas` | `us-east5` | |
| **Llama 4** | `meta/llama-4-scout-17b-16e-instruct-maas` | `us-east5` | |
| **Llama 3.3** | `meta/llama-3.3-70b-instruct-maas` | `us-central1` | |
| **DeepSeek** | `deepseek-ai/deepseek-v3.2-maas` | `global` | Global ONLY |
| **DeepSeek** | `deepseek-ai/deepseek-v3.1-maas` | `us-west2` | US-West2 ONLY |
| **DeepSeek** | `deepseek-ai/deepseek-r1-0528-maas` | `us-central1` | |
| **Qwen 3** | `qwen/qwen3-coder-480b-a35b-instruct-maas` | `global` | |
| **Qwen 3** | `qwen/qwen3-next-80b-a3b-instruct-maas` | `global` | |
| **Kimi** | `moonshotai/kimi-k2-thinking-maas` | `global` | |
| **MiniMax** | `minimaxai/minimax-m2-maas` | `global` | |
| **GLM** | `zai-org/glm-4.7-maas`, `zai-org/glm-5-maas` | `global` | |

## 3. Troubleshooting & Common Error Codes

### 429: Resource Exhausted

*   **Cause**: OpenMaaS and Gemini models use **Dynamic Shared Quota (DSQ)**.
    Resources are pooled and allocated dynamically based on availability. A 429
    error indicates the shared pool is temporarily exhausted, not necessarily
    that *your* specific project quota is hit (though it can be).
*   **Solution**: Implement strict **exponential backoff and retry** strategies.
*   **High Throughput**: For production workloads requiring high throughput or guaranteed capacity, consider **Provisioned Throughput (PT)**.
*   **Important**: Quota increases through normal cloud processes (Cloud Console) are **NOT** applicable for DSQ constraints.
*   **Documentation**: [Quotas and limits (DSQ)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/quotas)

### 400: User Validation Error

*   **Cause**: Invalid request format, unsupported parameter, or incorrect Model ID.
*   **Action**: Double-check your request payload and parameters. Verify the Model ID and Region are correct.

### 404: Not Found / Model Not Available

*   **Cause**: The model is not enabled, or not available in the specified project or region.
*   **Action**:
    1.  **Check Location Availability**:
        *   **OpenMaaS**: Verify the model is available in your region. See [Model Availability by Location](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#genai-open-models).
        *   **Gemini**:
            <!-- disableFinding(LINE_OVER_80) -->
            *   **Source of Truth**: Always check [Gemini Model Locations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#google-models) for the authoritative list.
            <!-- enableFinding(LINE_OVER_80) -->
            *   **Preview Models**: All Preview models (e.g., Gemini 3.1, experimental versions) are often **ONLY** available in the `us-central1` or `global` regions.
            *   **Stable Models**: (e.g., Gemini 2.5 Pro) Available in `us-central1`, `europe-west4`, and many other regions.
            *   **Important**: If you get a 404/400 error, try switching your client location to `us-central1` or `global`.
    2.  **Enable Llama Models**: For **Llama 3.3** and **Llama 4**, you **MUST**
        enable the model in Model Garden before use. Go to the [Model Garden]
        (https://console.cloud.google.com/agent-platform/model-garden), search
        for the model card (e.g., "Llama 3.3 API Service"), and click
        **Enable**. Only then can you make inference requests.
