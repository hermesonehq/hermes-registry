---
name: google-cloud-waf-operational-excellence
description: Generates operations-focused guidance for Google Cloud workloads based on the design principles and recommendations in the Operational Excellence pillar of the Google Cloud Well-Architected Framework (WAF). Use this skill to evaluate a workload, identify operational requirements, and provide actionable recommendations for deployment, monitoring, and incident management.
version: 1.0.0
author: google
license: Apache-2.0
platforms:
- linux
- macos
- windows
source: https://github.com/google/skills/tree/main/skills/cloud/google-cloud-waf-operational-excellence
metadata:
  category: WellArchitectedFramework
  hermes:
    icon: lucide:shield
    tags:
    - Google Cloud
    - Cloud
    - Waf
    - Operational
---

# Google Cloud Well-Architected Framework skill for the Operational Excellence pillar

## Overview

The operational excellence pillar in the Google Cloud Well-Architected Framework
provides recommendations to operate workloads efficiently on Google Cloud.
Operational excellence in the cloud involves designing, implementing, and
managing cloud solutions that provide value, performance, security, and
reliability. The recommendations in this pillar help you to continuously improve
and adapt workloads to meet the dynamic and ever-evolving needs in the cloud.

## Core principles

The recommendations in the operational excellence pillar of the Well-Architected
Framework are aligned with the following core principles:

-   **Ensure operational readiness**: Define and measure criteria for a workload
    to be considered ready for production, including staffing, processes, and
    governance. Grounding document:
    https://docs.cloud.google.com/architecture/framework/operational-excellence/operational-readiness-and-performance-using-cloudops.md.txt

-   **Manage incidents and problems**: Establish structured processes for
    incident response, communication, and root cause analysis to minimize impact
    and prevent recurrence. Grounding document:
    https://docs.cloud.google.com/architecture/framework/operational-excellence/manage-incidents-and-problems.md.txt

-   **Manage and optimize cloud resources**: Monitor resource utilization and
    right-size environments to maintain performance while ensuring operational
    efficiency. Grounding document:
    https://docs.cloud.google.com/architecture/framework/operational-excellence/manage-and-optimize-cloud-resources.md.txt

-   **Automate and manage change**: Use Infrastructure as Code (IaC) and CI/CD
    pipelines to ensure consistent, repeatable, and low-risk deployments and
    configuration changes. Grounding document:
    https://docs.cloud.google.com/architecture/framework/operational-excellence/automate-and-manage-change.md.txt

-   **Continuously improve and innovate**: Regularly review architectures,
    monitor industry trends, and adapt operations to meet evolving business
    needs. Grounding document:
    https://docs.cloud.google.com/architecture/framework/operational-excellence/continuously-improve-and-innovate.md.txt

## Relevant Google Cloud products

The following are _examples_ of Google Cloud products and features that are
relevant to operational excellence:

-   **Observability and monitoring**
    -   **Cloud Monitoring**: Full-stack observability for Google Cloud and
        hybrid environments.
    -   **Cloud Logging**: Real-time log management and analysis at scale.
    -   **Error Reporting**: Aggregates and displays errors for running cloud
        services.
    -   **Service Monitoring**: Tools for defining and tracking Service Level
        Objectives (SLOs).

-   **Automation and CI/CD**
    -   **Cloud Build**: Serverless platform for building, testing, and
        deploying software.
    -   **Cloud Deploy**: Managed continuous delivery service for GKE, Cloud
        Run, and GCE.
    -   **Terraform / Infrastructure Manager**: Managed service for
        Infrastructure as Code (IaC) automation.
    -   **Artifact Registry**: Central repository for managing build artifacts
        and container images.

-   **Resource management and optimization**
    -   **Recommender (Active Assist)**: Automatically identifies idle resources
        and right-sizing opportunities.
    -   **Resource Manager**: Hierarchical management of resources across
        organizations, folders, and projects.

-   **Incident response**
    -   **Incident response & management (IRM)**: Structured tools and processes
        for managing operational disruptions.

## Workload assessment questions

Ask appropriate questions to understand operations-related requirements and
constraints of the workload and the user's organization. Choose questions from
the following list:

-   **Operational readiness and performance**
    -   How do you define and measure operational readiness for your cloud
        workloads and what specific criteria or metrics do you use?
    -   Describe your process for defining, tracking, and achieving SLOs for
        your critical workloads.

-   **Incident and problem management**
    -   Describe your incident management process, including roles,
        responsibilities, and communication channels.
    -   How do you conduct post-incident reviews (PIRs) to identify root causes
        and implement preventive measures?

-   **Resource management and optimization**
    -   How do you ensure that your cloud resources are right-sized for your
        workloads, and what tools or techniques do you use?

-   **Change automation**
    -   Describe your change management process, including approval workflows,
        testing procedures, and deployment strategies.
    -   How do you automate deployments, ensure their consistency and manage
        configuration?

-   **Continuous improvement**
    -   How do you ensure that your cloud operations are continuously adapting
        to meet evolving business needs and technological advancements?

## Validation checklist

Use the following checklist to evaluate the architecture's alignment with
operational excellence recommendations:

-   **Operational readiness**
    -   [ ] A formal framework or set of criteria exists to assess operational
        readiness before production deployment.
    -   [ ] Service Level Objectives (SLOs) are explicitly defined and monitored
        using automated tools.

-   **Incident management**
    -   [ ] Incident response roles and communication channels are clearly
        defined and documented.
    -   [ ] A structured, blameless post-mortem process is followed for all
        major incidents.

-   **Change automation**
    -   [ ] All infrastructure changes are performed using Infrastructure as
        Code (IaC) to ensure consistency.
    -   [ ] CI/CD pipelines are integrated with automated testing for all
        deployment changes.

-   **Resource optimization**
    -   [ ] Resource utilization is regularly reviewed using recommendations
        from Active Assist or performance data.

-   **Culture of improvement**
    -   [ ] A documented strategy is in place for regularly reviewing and
        adapting cloud operations to industry advancements.
