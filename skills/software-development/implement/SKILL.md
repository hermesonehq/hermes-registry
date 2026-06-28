---
name: implement
description: Implement a piece of work based on a PRD or set of issues.
disable-model-invocation: true
version: 1.0.0
author: mattpocock
license: MIT
platforms:
- linux
- macos
- windows
source: https://github.com/mattpocock/skills/tree/main/skills/engineering/implement
metadata:
  hermes:
    icon: lucide:hammer
    tags:
    - Implementation
    - Coding
    - Workflow
---

Implement the work described by the user in the PRD or issues.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /review to review the work.

Commit your work to the current branch.
