---
schema_version: 2
id: "context-profile-default-research"
type: "context-profile"
title: "Default Research"
name: "default-research"
max_items: 20
include_memory: false
include_decisions: true
include_research: true
include_raw: "fallback"
created: 2026-08-09
updated: 2026-08-09
---

# Context Profile

## Purpose

Assemble the smallest connected research context without private Memory by default.

## Preferred Knowledge Types

preferred type order:
  synthesis
  comparison
  concept
  topic
  entity
  project
  investigation
  research-question
  finding
  decision

## Required Sections

Paths, deterministic scores, explicit edges, evidence fallback, and files to read.

## Expansion Rules

relationship depth: 1
memory: disabled by default
Raw: fallback only

## Exclusions

Exclude Memory and unrelated Raw evidence.

## Evidence Rules

Use exact selected source paths; never generate semantic summaries.
