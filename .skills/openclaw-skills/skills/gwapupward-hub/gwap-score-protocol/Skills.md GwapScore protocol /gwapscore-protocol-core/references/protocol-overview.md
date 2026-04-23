# GwapScore Protocol Overview

## Objective
GwapScore is an evidence‑based trust scoring protocol designed to measure reliability, legitimacy, and behavioral trustworthiness for wallets, users, creators, merchants, and counterparties.

## Canonical output
- **protocol score**: a value between 300–900
- **score band**: a category derived from the score range
- **confidence level**: an indicator of how certain the score is
- **attestation trail**: a record of the facts supporting the score
- **risk flags**: indicators for severe negatives or caps
- **explanation summary**: an audit‑friendly description of the result

## Design principles
- deterministic and explainable
- source‑agnostic through canonical events
- auditable and recalculable
- resistant to vanity manipulation
- conservative under uncertainty
- supportive of manual review and dispute

## Input categories
1. onchain wallet behavior
2. counterparty quality and outcomes
3. protocol‑native outcomes
4. linked social / public reputation evidence
5. partner‑issued attestations

## Processing model
raw signal → canonical event → attestation → score impact → confidence → explanation → review if needed

## Core separation
The protocol must separate:
- evidence
- interpretation
- score output
- enforcement

## Score bands
- **300–449**: high risk / low trust
- **450–599**: emerging / limited evidence
- **600–699**: stable / moderate trust
- **700–799**: strong / high trust
- **800–900**: exceptional / verified reliability