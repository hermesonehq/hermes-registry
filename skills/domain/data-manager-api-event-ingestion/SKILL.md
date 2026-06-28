---
name: data-manager-api-event-ingestion
description: Guides developers through implementing event and conversion ingestion to Google products using the Data Manager API /v1/events/ingest endpoint and its associated client libraries. Use this skill when the user wants to upload offline conversions, enhanced conversions for leads, click conversions, Google Analytics web or app events, or any other event ingestion use case supported by the Data Manager API. Don't use for uploading audience members (use the data-manager-api-audience-ingestion skill).
version: 1.0.0
author: google
license: Apache-2.0
platforms:
- linux
- macos
- windows
source: https://github.com/google/skills/tree/main/skills/ads/data-manager-api/data-manager-api-event-ingestion
metadata:
  version: 1.1
  category: GoogleAds
  hermes:
    icon: lucide:megaphone
    tags:
    - Google Ads
    - Data
    - Manager
    - Api
---

# Data Manager API Event Ingestion

## Core Directives

*   [IMPORTANT] When reading API documentation from developers.google.com, read
    the Markdown equivalent of the page by appending `.md.txt` to the URL.

## Sequential Implementation Workflow

For simple informational, configuration, or setup questions, skip any irrelevant
steps and answer using only the relevant guidelines or documentation provided
below.

### Step 1: Identify Use Case & Read Documentation

-   **Determine Destination Account Type**: [CRITICAL] If it's not
    explicitly stated, STOP and CLARIFY with the user where the data is being
    sent (e.g., Google Ads, Floodlight, Google Analytics)
    BEFORE generating any code. Do NOT assume Google Ads by default. This maps
    to the `account_type` field of the `operating_account` in the `Destination`,
    and also determines valid event identifiers and requirements.
-   **Read Documentation**: [CRITICAL] You MUST follow the
    the [Send events guide](https://developers.google.com/data-manager/api/devguides/events/send-events)
    to understand implementation steps, user/event identifier requirements, and
    how to configure the destination object.

### Step 2: Setup Auth

1.  **Enable API (Prerequisite)**: Check that the user has enabled the Data
    Manager API in their Google Cloud project.
2.  **Generate ADC**: Authenticate the local workspace using Application
    Default Credentials (ADC) via `gcloud auth application-default login`.
    *   **Required Scopes**: Include scopes
        `https://www.googleapis.com/auth/datamanager` and
        `https://www.googleapis.com/auth/cloud-platform`.
    *   **Multi-API Scopes**: If using the same credentials for other APIs,
        append their scopes (e.g.,
        `https://www.googleapis.com/auth/adwords`).
    *   **Service Accounts**: Ensure the Service Account has the
        `Service Usage Consumer` IAM role, and the user executing `gcloud`
        has the Token Creator role
        (`roles/iam.serviceAccountTokenCreator`) on that Service Account
        for impersonation.
3.  **Reference**: Refer to [Set up API access](https://developers.google.com/data-manager/api/devguides/quickstart/set-up-access)
    for a walkthrough of the `gcloud` CLI auth setup.

### Step 3: Install Client Library and Utilities

Refer to [Install a client
library](https://developers.google.com/data-manager/api/devguides/quickstart/install-library)
for detailed installation instructions.

| Language | Installation Instructions |
| :--- | :--- |
| **Python** | `pip install google-ads-datamanager` |
| **Java** | Follow the [quickstart](https://github.com/googleapis/google-cloud-java/tree/main/java-datamanager#quickstart) instructions to install the Maven/Gradle dependency. |
| **Node** | `npm install @google-ads/datamanager` |
| **PHP** | Install the `googleads/data-manager` component using Composer. |
| **.NET** | Install the `Google.Ads.DataManager.V1` NuGet package. |

[IMPORTANT] The utility library is NOT available on public package managers
(such as PyPI or Maven). Follow the below instructions to install:

1.  Clone the repository from GitHub using the commands from the table below.
2.  Always use the latest available version of the library. Determine the
    actual version identifier (`VERSION`) from the cloned repository metadata.
    - **Python**: Find the version in `pyproject.toml`.
    - **Java**: Find the version in `data-manager-util/build.gradle`.
    - **Node**: Find the version in `util/package.json` (as the `version`
      field).
3.  Follow the language-specific instructions in the next section to build
    and install the utility dependency, replacing `VERSION` with the version
    identifier you found.

| Language | Git Clone Command |
| :--- | :--- |
| **Python** | `git clone https://github.com/googleads/data-manager-python.git` |
| **Java** | `git clone https://github.com/googleads/data-manager-java.git` |
| **Node** | `git clone https://github.com/googleads/data-manager-node.git` |
| **PHP** | `git clone https://github.com/googleads/data-manager-php.git` |
| **.NET** | `git clone https://github.com/googleads/data-manager-dotnet.git` |

#### Install Utility Library

##### Python

1.  Navigate to the `data-manager-python` directory and install the utility
    library:
    
    ```shell
    pip install .
    ```
2.  Declare a dependency in your project's `requirements.txt` file (replacing
    `VERSION` with the identified version):

    ```
   google-ads-datamanager-util==VERSION
    ```

##### Java

1.  Navigate to the `data-manager-java` directory.
2.  Build and publish the utility library to your local Maven repository:

   ```shell
   ./gradlew data-manager-util:install
   ```
3.  Declare a dependency on the utility library in your project (replacing
    `VERSION` with the identified version):
    *   **Gradle**:
     ```none
     implementation 'com.google.api-ads:data-manager-util:VERSION'
     ```

    *   **Maven**:
     ```xml
     <dependency>
        <groupId>com.google.api-ads</groupId>
        <artifactId>data-manager-util</artifactId>
        <version>VERSION</version>
     </dependency>
     ```

##### Node

1.  Navigate to the `data-manager-node` directory and install dependencies:

   ```shell
   npm install
   ```
2.  Navigate to the `util` directory:

   ```shell
   cd util
   ```
3.  Pack the utility library into a `.tgz` archive:

   ```shell
   npm pack
   ```
4.  Declare a dependency in your Node.js project's `package.json` pointing to
    the path of the generated `.tgz` archive (replacing `VERSION` with the
    identified version):

   ```json
   {
      "dependencies": {
         "@google-ads/data-manager-util": "file:/path/to/google-ads-datamanager-util-VERSION.tgz"
      }
   }
   ```

##### PHP

1.  Navigate to the `data-manager-php` directory.
2.  Resolve dependencies for the library:

   ```shell
   composer update --prefer-dist
   ```
3.  Update your project's `composer.json` to declare a dependency on the utility
    library using a path repository:

   ```json
    {
        "repositories": [
            {
                "type": "path",
                "url": "/path/to/cloned/data-manager-php"
            }
        ],
        "require": {
            "googleads/data-manager-util": "@dev"
        }
    }
   ```

##### .NET

In your .NET project, declare a `ProjectReference` dependency pointing to the
cloned library's `.csproj` path:

```xml
<ProjectReference Include="\path\to\cloned\Google.Ads.DataManager.Util\src\Google.Ads.DataManager.Util.csproj" />
```

### Step 4: Retrieve Code Sample

[IMPORTANT] If writing or updating an ingestion script, ALWAYS retrieve the
relevant code sample to use as a reference:

| Language | Sample |
| :--- | :--- |
| **Python** | [`ingest_events.py`](https://github.com/googleads/data-manager-python/blob/main/samples/events/ingest_events.py) |
| **Java** | [`IngestEvents.java`](https://github.com/googleads/data-manager-java/blob/main/data-manager-samples/src/main/java/com/google/ads/datamanager/samples/IngestEvents.java) |
| **PHP** | [`ingest_events.php`](https://github.com/googleads/data-manager-php/blob/main/samples/events/ingest_events.php) |
| **Node** | [`ingest_events.ts`](https://github.com/googleads/data-manager-node/blob/main/samples/events/ingest_events.ts) |
| **.NET**| [`IngestEvents.cs`](https://github.com/googleads/data-manager-dotnet/blob/main/samples/IngestEvents.cs) |

### Step 5: Retrieve migration guides

[CRITICAL] If refactoring code to upgrade from another Google API, ALWAYS
extract the full contents of the relevant field mapping guide.

#### Google Ads

*   **Google Ads API Offline Conversions**:
    [Google Ads Offline Conversions Migration Field Mappings](https://developers.google.com/data-manager/api/devguides/events/google-ads/offline/upgrade/field-mappings)
*   **Google Ads API Store Sales**:
    [Google Ads Store Sales Migration Field Mappings](https://developers.google.com/data-manager/api/devguides/events/google-ads/store-sales/upgrade/field-mappings)

#### Google Analytics

*   **Measurement Protocol (Google Analytics)**:
    [Google Analytics Measurement Protocol Migration Field Mappings](https://developers.google.com/data-manager/api/devguides/events/analytics/measurement-protocol/upgrade/field-mappings)

#### Campaign Manager 360 (CM360)

*   **Campaign Manager 360 API Offline Conversions**:
    [Campaign Manager 360 Offline Conversions Migration Field Mappings](https://developers.google.com/data-manager/api/devguides/events/cm360/offline/upgrade/field-mappings)

### Step 6: Implementation

Implement the ingestion logic using the following checkpoints:

-   [ ] **Initialize Client**: Instantiate the Data Manager client
    (`IngestionServiceClient`).
-   [ ] **Define Destinations**: Build the `Destination` object using the
    `product_destination_id` and the appropriate account configurations:
    `operating_account` (target account receiving data), `login_account` (if
    authenticating using a manager account or a data partner account), and
    `linked_account` (if you're a data partner accessing the account via a
    partner link to a manager account). **STRONGLY RECOMMENDED**: Refer to the
    [Configure destinations and headers](https://developers.google.com/data-manager/api/devguides/concepts/destinations)
    guide for more details on configuring destinations.
-   [ ] **Prepare Event Data**: Use the utility library helpers to format and
    normalize user identifiers correctly.
-   [ ] **Construct Payload**: Build the request payload
    (`IngestEventsRequest`) containing the destinations, event records, and
    consent permissions.
-   [ ] **Send Request**: Execute `ingest_events` and record the returned
    request ID for logging/troubleshooting.

## Formatting

*   Fetch the [Format user data](https://developers.google.com/data-manager/api/devguides/concepts/formatting)
    guide and use that as the source of truth for formatting and
    normalization rules.

*   Use the utility library to format, hash, and encrypt user data
    (emails, phone numbers, addresses).

    **Python Example:**
    
    ```python
    from google.ads.datamanager_util import Formatter
    from google.ads.datamanager_util.format import Encoding

    formatter: Formatter = Formatter()

    processed_email: str = formatter.process_email_address(
        email, Encoding.HEX
    )
    ```

## Critical Gotchas

*   Format `product_destination_id` as a numeric string. It is NOT a resource
    name path.
*   Format `event_timestamp` strictly in RFC 3339 format. Use the SDK's typed
    timestamp object instead of a raw string where available.
*   Nest click identifiers (`gclid`, `gbraid`, `wbraid`) inside the
    `ad_identifiers` block, not directly on the base event payload.
*   The enum values for `ConsentStatus` are `CONSENT_GRANTED` and
    `CONSENT_DENIED`. Do not use the values `GRANTED` and `DENIED`.
*   Note that `consent` can be set globally on the `IngestEventsRequest` or on
    individual `Event`s.
*   Verify that `UserIdentifier` uses `email_address` and `phone_number`.
    Do NOT use the Google Ads API fields `hashed_email` and
    `hashed_phone_number`.
*   Ensure the currency field on the event is named `currency`, not
    `currency_code`.

## Error Handling & Troubleshooting

### Inspecting Error Payloads

[IMPORTANT] Refer to
[Understand API Errors](https://developers.google.com/data-manager/api/devguides/concepts/understand-errors)
for a detailed guide on how to understand the structure of errors returned by
the API.

## API Reference

When implementing or debugging API integrations, use the API reference to lookup
field names, types, and acceptable values. DO NOT guess values.

*   **REST API Reference:**
    https://developers.google.com/data-manager/api/reference/rest/v1/events/ingest
