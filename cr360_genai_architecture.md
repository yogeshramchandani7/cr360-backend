# CR360: GenAI-Powered Credit Risk Analytics Platform
## Technical Architecture Document

**Version:** 1.0  
**Date:** December 2025  
**Author:** CR360 Architecture Team

---

## Executive Summary

CR360 is an innovative credit risk analytics platform designed with Generative AI at its epicenter. This document outlines the technical architecture for enabling **Progressive AI Analytics** — a conversational intelligence layer that allows Chief Credit Officers (CCOs) and risk analysts to query financial data in natural language, receive intelligent visualizations, and conduct multi-step root cause investigations.

The architecture addresses three core challenges:
1. **Natural Language to Data Translation** — Converting user questions into accurate database queries
2. **Progressive Investigation** — Maintaining context across multi-turn conversations for root cause analysis
3. **Intelligent Visualization** — Automatically selecting the optimal chart type based on data characteristics and user intent

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Components](#2-core-components)
3. [Context Layer Design](#3-context-layer-design-semantic-model)
4. [Query Intelligence Engine](#4-query-intelligence-engine)
5. [Reliability & Quality Assurance](#5-reliability--quality-assurance) ⭐ **NEW**
6. [Progressive Investigation Agent](#6-progressive-investigation-agent)
7. [Visualization Intelligence](#7-visualization-intelligence)
8. [Credit Risk Domain Knowledge](#8-credit-risk-domain-knowledge)
9. [Data Flow Architecture](#9-data-flow-architecture)
10. [Security & Governance](#10-security--governance)
11. [Technology Stack](#11-technology-stack)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CR360 PRESENTATION LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │   Chat Interface │  │   Dashboard     │  │   Visualization Canvas          │  │
│  │   (React/Next.js)│  │   (Embedded)    │  │   (D3.js/Recharts/Plotly)       │  │
│  └────────┬────────┘  └────────┬────────┘  └────────────────┬────────────────┘  │
└───────────┼─────────────────────┼────────────────────────────┼──────────────────┘
            │                     │                            │
            ▼                     ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    AGENTIC AI ORCHESTRATOR                               │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │    │
│  │  │ Intent       │ │ Context      │ │ Task         │ │ Response     │    │    │
│  │  │ Classifier   │ │ Manager      │ │ Planner      │ │ Synthesizer  │    │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            ▼                           ▼                           ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│  QUERY INTELLIGENCE   │  │  INVESTIGATION        │  │  VISUALIZATION        │
│  ENGINE               │  │  AGENT                │  │  INTELLIGENCE         │
│  ┌─────────────────┐  │  │  ┌─────────────────┐  │  │  ┌─────────────────┐  │
│  │ NL Parser       │  │  │  │ Hypothesis Gen  │  │  │  │ Chart Selector  │  │
│  │ Query Generator │  │  │  │ Metric Mapper   │  │  │  │ Data Transformer│  │
│  │ SQL Validator   │  │  │  │ Root Cause AI   │  │  │  │ Narrative Gen   │  │
│  └─────────────────┘  │  │  └─────────────────┘  │  │  └─────────────────┘  │
└───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘
            │                          │                          │
            ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      RELIABILITY & QUALITY LAYER ⭐ NEW                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ SQL Validator   │ │ Ambiguity       │ │ Smart Retry     │ │ Golden Test  │  │
│  │ (Pre-execution) │ │ Detector        │ │ Loop            │ │ Suite        │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ └──────────────┘  │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CONTEXT LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    CREDIT RISK CONTEXT FILE (YAML)                       │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │    │
│  │  │ Metric       │ │ Dimension    │ │ Business     │ │ Schema       │    │    │
│  │  │ Definitions  │ │ Hierarchies  │ │ Rules        │ │ Docs         │    │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                             │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │ Credit Risk Mart (OFSAA)            │  │  Data Warehouse                 │  │
│  │ Your Existing Database              │  │  (Snowflake/BigQuery/Oracle)    │  │
│  └─────────────────────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

| Principle | Description |
|-----------|-------------|
| **AI-First** | Every interaction is powered by LLM understanding, not keyword matching |
| **Progressive Depth** | Start simple, drill down to root causes through conversation |
| **Context Preservation** | Multi-turn conversations maintain full analytical context |
| **Explainable Outputs** | Every answer traces back to source data with clear lineage |
| **Domain-Aware** | Deep understanding of credit risk metrics, relationships, and workflows |
| **Visualization Native** | Data is presented in the most digestible format automatically |

---

## 2. Core Components

### 2.1 Component Overview

| Component | Purpose | Key Capabilities |
|-----------|---------|------------------|
| **Agentic Orchestrator** | Central coordination of all AI operations | Intent routing, context management, multi-agent coordination |
| **Query Intelligence Engine** | Translate natural language to data queries | Text-to-SQL, context mapping, query validation |
| **Investigation Agent** | Progressive root cause analysis | Hypothesis generation, metric correlation, causal inference |
| **Visualization Intelligence** | Optimal chart selection and rendering | Data profiling, chart recommendation, narrative generation |
| **Reliability Layer** ⭐ | Ensure system works predictably | SQL validation, ambiguity detection, smart retry, golden tests |
| **Context Layer** | Business logic definitions | Metric formulas, dimension hierarchies, schema docs (YAML file) |

### 2.2 Agentic Orchestrator

The Orchestrator is the "brain" of CR360's conversational AI, coordinating specialized agents to fulfill user requests.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC ORCHESTRATOR                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    INTENT CLASSIFIER                        │ │
│  │  • Query (simple fact retrieval)                           │ │
│  │  • Investigation (multi-step analysis)                     │ │
│  │  • Comparison (benchmark/peer analysis)                    │ │
│  │  • Forecast (predictive questions)                         │ │
│  │  • Explanation (metric definition clarification)           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    CONTEXT MANAGER                          │ │
│  │  • Conversation history (sliding window + summarization)   │ │
│  │  • Active filters (region, product, time period)           │ │
│  │  • Investigation state (hypotheses, findings)              │ │
│  │  • User profile (role, permissions, preferences)           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    TASK PLANNER                             │ │
│  │  • Decompose complex queries into sub-tasks                │ │
│  │  • Route to appropriate specialist agents                  │ │
│  │  • Manage parallel vs sequential execution                 │ │
│  │  • Handle error recovery and fallbacks                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    RESPONSE SYNTHESIZER                     │ │
│  │  • Aggregate results from multiple agents                  │ │
│  │  • Generate natural language explanations                  │ │
│  │  • Attach visualizations and drill-down options            │ │
│  │  • Suggest follow-up questions                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### Orchestrator Workflow

```python
# Pseudo-code for Orchestrator flow
async def process_user_message(message: str, session: Session):
    
    # 1. Classify Intent
    intent = await intent_classifier.classify(
        message=message,
        context=session.context,
        conversation_history=session.history[-10:]
    )
    
    # 2. Update Context
    session.context = await context_manager.update(
        message=message,
        intent=intent,
        existing_context=session.context
    )
    
    # 3. Plan Tasks
    task_plan = await task_planner.create_plan(
        intent=intent,
        context=session.context,
        available_agents=[
            QueryAgent,
            InvestigationAgent,
            VisualizationAgent,
            ExplanationAgent
        ]
    )
    
    # 4. Execute Tasks
    results = await execute_task_plan(task_plan)
    
    # 5. Synthesize Response
    response = await response_synthesizer.create(
        results=results,
        context=session.context,
        user_preferences=session.user.preferences
    )
    
    return response
```

---

## 3. Context Layer Design (Semantic Model)

### 3.1 Why a Context Layer is Critical

The context layer is a **YAML/JSON configuration file** that provides the LLM with everything it needs to generate accurate queries. Without it, LLMs struggle with:
- Ambiguous metric names (e.g., "exposure" could mean 10 different things)
- Complex joins across 100+ tables
- Business-specific calculations (e.g., Net Charge-Off = Gross Write-offs - Recoveries)
- Consistent definitions across all queries

**Note:** This is NOT a complex "semantic layer tool" like Cube or dbt — it's simply a well-structured configuration file loaded into the LLM prompt.

### 3.2 Credit Risk Semantic Model

```yaml
# CR360 Semantic Model Definition (YAML-based)
model:
  name: credit_risk_analytics
  version: "1.0"
  
  # METRICS - What we measure
  metrics:
    
    # Exposure Metrics
    gross_credit_exposure:
      definition: "Total credit exposure before any risk mitigation"
      formula: "SUM(BPCRA013)"
      unit: "currency"
      synonyms: ["GCE", "total exposure", "gross exposure"]
      
    adjusted_outstanding_balance:
      definition: "Outstanding balance adjusted for accounting treatments"
      formula: "SUM(BPCRA097)"
      unit: "currency"
      synonyms: ["AOB", "adjusted balance", "adjusted outstanding"]
      
    net_credit_exposure:
      definition: "Exposure after deducting collateral and guarantees"
      formula: "gross_credit_exposure - mitigant_value"
      unit: "currency"
      
    # Delinquency Metrics
    delinquency_rate_30:
      definition: "Percentage of portfolio 30+ days past due"
      formula: "SUM(CASE WHEN BPCRA081='Y' THEN BPCRA097 ELSE 0 END) / SUM(BPCRA097)"
      unit: "percentage"
      synonyms: ["30+ DPD rate", "DQ30", "30 day delinquency"]
      
    delinquency_rate_60:
      definition: "Percentage of portfolio 60+ days past due"
      formula: "SUM(CASE WHEN BPCRA082='Y' THEN BPCRA097 ELSE 0 END) / SUM(BPCRA097)"
      unit: "percentage"
      
    delinquency_rate_90:
      definition: "Percentage of portfolio 90+ days past due"
      formula: "SUM(CASE WHEN BPCRA083='Y' THEN BPCRA097 ELSE 0 END) / SUM(BPCRA097)"
      unit: "percentage"
      synonyms: ["90+ DPD rate", "serious delinquency rate", "SDQ"]
      
    # Loss Metrics
    net_charge_off_rate:
      definition: "Net charge-offs as a percentage of average outstanding"
      formula: "SUM(BPCRA143) / AVG(BPCRA097) * 12"  # Annualized
      unit: "percentage"
      synonyms: ["NCO rate", "write-off rate", "loss rate"]
      time_grain: ["MTD", "QTD", "YTD"]
      
    expected_credit_loss:
      definition: "IFRS 9 Expected Credit Loss provision"
      formula: "SUM(BPCRA041)"
      unit: "currency"
      synonyms: ["ECL", "provision", "allowance"]
      
    # Risk Score Metrics
    average_pd:
      definition: "Portfolio weighted average probability of default"
      formula: "SUM(BPCRA326 * BPCRA097) / SUM(BPCRA097)"
      unit: "percentage"
      synonyms: ["PD", "default probability", "1-year PD"]
      
    average_credit_score:
      definition: "Portfolio weighted average credit score"
      formula: "SUM(BPCRA279 * BPCRA097) / SUM(BPCRA097)"
      unit: "score"
      synonyms: ["bureau score", "FICO", "credit score"]
      
    # Origination Metrics
    origination_volume:
      definition: "Total new credit originations"
      formula: "SUM(CASE WHEN is_new_origination THEN funded_amount END)"
      unit: "currency"
      synonyms: ["new originations", "production", "bookings"]
      
    origination_count:
      definition: "Number of new credit originations"
      formula: "COUNT(CASE WHEN is_new_origination THEN 1 END)"
      unit: "count"
      
    # LTV Metrics
    average_ltv:
      definition: "Portfolio weighted average loan-to-value ratio"
      formula: "SUM(BPCRA102 * BPCRA097) / SUM(BPCRA097)"
      unit: "percentage"
      synonyms: ["LTV", "loan to value"]
      
  # DIMENSIONS - How we slice data
  dimensions:
    
    region:
      definition: "Geographic region"
      hierarchy: ["country", "state", "city", "branch"]
      values: ["North", "South", "East", "West", "Central"]
      
    product:
      definition: "Credit product type"
      hierarchy: ["product_family", "product_type", "product_code"]
      values: ["Mortgage", "Auto", "Credit Card", "Personal Loan", "Commercial"]
      
    customer_segment:
      definition: "Customer classification"
      hierarchy: ["segment_group", "segment"]
      retail_values: ["Prime", "Near-Prime", "Subprime"]
      wholesale_values: ["Investment Grade", "Non-Investment Grade", "Watch List"]
      
    vintage:
      definition: "Origination cohort"
      hierarchy: ["year", "quarter", "month"]
      
    risk_grade:
      definition: "Internal risk rating"
      hierarchy: ["risk_category", "risk_grade"]
      values: ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]
      
    delinquency_bucket:
      definition: "Days past due classification"
      values: ["Current", "1-29 DPD", "30-59 DPD", "60-89 DPD", "90-119 DPD", "120+ DPD"]
      
    time:
      definition: "Reporting time period"
      hierarchy: ["year", "quarter", "month", "week", "day"]
      
  # RELATIONSHIPS - How entities connect
  relationships:
    
    account_to_customer:
      type: "many-to-one"
      from: "account"
      to: "customer"
      
    account_to_credit_line:
      type: "many-to-one"
      from: "account"
      to: "credit_line"
      
    credit_line_hierarchy:
      type: "parent-child"
      entity: "credit_line"
      description: "Ultimate Parent > Parent > Child > Grand Child"
      
    customer_to_party:
      type: "many-to-many"
      from: "customer"
      to: "party"
      roles: ["primary_borrower", "co_borrower", "guarantor"]
```

### 3.3 Context Layer Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT FILE STRUCTURE                        │
│                    (credit_risk_context.yaml)                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              METRICS SECTION                                │ │
│  │  • 100+ key metrics with SQL formulas                      │ │
│  │  • Synonyms for NLP matching                               │ │
│  │  • Units and formatting rules                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              TABLES & SCHEMA SECTION                        │ │
│  │  • Table names and descriptions                            │ │
│  │  • Column definitions                                       │ │
│  │  • Join relationships                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              DIMENSIONS SECTION                             │ │
│  │  • Region: Country > State > City > Branch                 │ │
│  │  • Product: Family > Type > Code                           │ │
│  │  • Time: Year > Quarter > Month > Week > Day               │ │
│  │  • Valid values for each dimension                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              RULES SECTION                                  │ │
│  │  • Default time period = current quarter                   │ │
│  │  • Use RCY columns for currency                            │ │
│  │  • Always apply tenant filter                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  TOTAL SIZE: ~25,000 tokens (fits easily in 200K context)       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Query Intelligence Engine

### 4.1 Text-to-SQL Architecture

The Query Intelligence Engine converts natural language questions into accurate SQL queries against the credit risk data model.

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY INTELLIGENCE ENGINE                     │
│                                                                  │
│  User Question: "How are originations looking in various        │
│                  regions this quarter?"                         │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 1: NL UNDERSTANDING                       │ │
│  │                                                             │ │
│  │  Intent: QUERY (fact retrieval)                            │ │
│  │  Entities Extracted:                                        │ │
│  │    • Metric: "originations" → origination_volume            │ │
│  │    • Dimension: "regions" → region                          │ │
│  │    • Time: "this quarter" → current_quarter                 │ │
│  │  Aggregation: GROUP BY region                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 2: SEMANTIC MAPPING                       │ │
│  │                                                             │ │
│  │  Map to Semantic Model:                                     │ │
│  │    • origination_volume → BPMV043, BPMV044, etc.           │ │
│  │    • region → dim_geography.region_name                     │ │
│  │    • current_quarter → WHERE period = 'Q4-2025'            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 3: QUERY GENERATION                       │ │
│  │                                                             │ │
│  │  SELECT                                                     │ │
│  │      g.region_name AS region,                               │ │
│  │      SUM(f.origination_volume_rcy) AS origination_amount,   │ │
│  │      COUNT(DISTINCT f.application_skey) AS count            │ │
│  │  FROM fact_credit_risk f                                    │ │
│  │  JOIN dim_geography g ON f.geo_skey = g.geo_skey            │ │
│  │  JOIN dim_time t ON f.time_skey = t.time_skey               │ │
│  │  WHERE t.fiscal_quarter = 'Q4-2025'                         │ │
│  │  GROUP BY g.region_name                                     │ │
│  │  ORDER BY origination_amount DESC                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 4: VALIDATION & EXECUTION                 │ │
│  │                                                             │ │
│  │  • Syntax validation                                        │ │
│  │  • Permission check (user can access this data?)           │ │
│  │  • Execute against database                                 │ │
│  │  • Error handling & retry with corrections                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              RESULT                                         │ │
│  │                                                             │ │
│  │  | Region  | Origination Amount | Count |                  │ │
│  │  |---------|-------------------|-------|                   │ │
│  │  | South   | $2.4B             | 15,420|                   │ │
│  │  | North   | $1.8B             | 12,150|                   │ │
│  │  | East    | $1.6B             | 10,890|                   │ │
│  │  | West    | $1.5B             | 9,750 |                   │ │
│  │  | Central | $1.2B             | 8,200 |                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Full-Context Prompting

Since the credit risk context (~100 key metrics, schema, rules) fits within the LLM's context window, we load everything directly into the system prompt — no retrieval needed:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL-CONTEXT PROMPTING                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              CONTEXT FILE (credit_risk_context.yaml)        │ │
│  │              Loaded once at startup (~25K tokens)           │ │
│  │                                                             │ │
│  │  • Metric definitions (100+ key metrics with formulas)     │ │
│  │  • Table schemas with column descriptions                  │ │
│  │  • Dimension hierarchies and valid values                  │ │
│  │  • Business rules and calculation logic                    │ │
│  │  • Example queries for common patterns                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              SYSTEM PROMPT STRUCTURE                        │ │
│  │                                                             │ │
│  │  System: You are a credit risk SQL expert.                 │ │
│  │                                                             │ │
│  │  METRICS:                                                   │ │
│  │  {full metric definitions from YAML}                       │ │
│  │                                                             │ │
│  │  TABLES:                                                    │ │
│  │  {full schema definitions}                                 │ │
│  │                                                             │ │
│  │  DIMENSIONS:                                                │ │
│  │  {hierarchies and valid values}                            │ │
│  │                                                             │ │
│  │  RULES:                                                     │ │
│  │  - Always use table aliases                                │ │
│  │  - Default time period is current quarter                  │ │
│  │  - Use RCY (reporting currency) columns                    │ │
│  │                                                             │ │
│  │  User Question: {question}                                 │ │
│  │  Conversation Context: {recent messages}                   │ │
│  │                                                             │ │
│  │  Generate SQL query:                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  WHY THIS WORKS:                                                │
│  • Your context: ~25,000 tokens                                 │
│  • Gemini 2.5 Flash context window: 1,000,000 tokens            │
│  • Everything fits — no retrieval complexity needed             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Pre-Execution SQL Validation

Before executing any LLM-generated SQL, the system validates that all referenced tables and columns actually exist. This prevents runtime errors from hallucinated schema elements.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQL VALIDATION PIPELINE                       │
│                                                                  │
│  LLM Output: SELECT region, delinquency_rate FROM metrics       │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 1: PARSE SQL                              │ │
│  │                                                             │ │
│  │  Extract identifiers:                                       │ │
│  │    • Tables referenced: ["metrics"]                        │ │
│  │    • Columns referenced: ["region", "delinquency_rate"]    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 2: SCHEMA VALIDATION                      │ │
│  │                                                             │ │
│  │  Check against known schema:                                │ │
│  │    ✗ Table "metrics" does not exist                        │ │
│  │    ✗ Column "delinquency_rate" does not exist              │ │
│  │                                                             │ │
│  │  Known tables: [FCT_CREDIT_RISK, DIM_GEOGRAPHY, ...]       │ │
│  │  Known columns: [BPCRA081, BPCRA097, region_name, ...]     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 3: VALIDATION RESULT                      │ │
│  │                                                             │ │
│  │  If INVALID → Trigger self-correction with specific errors │ │
│  │  If VALID → Proceed to execution                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

```python
import sqlparse
import re
from dataclasses import dataclass
from typing import List, Set

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    invalid_tables: List[str]
    invalid_columns: List[str]

class SQLValidator:
    """Validates LLM-generated SQL against actual database schema"""
    
    def __init__(self, schema_config: dict):
        # Load known tables and columns from context file
        self.known_tables: Set[str] = set(
            t.upper() for t in schema_config.get('tables', {}).keys()
        )
        self.known_columns: Set[str] = set()
        for table_info in schema_config.get('tables', {}).values():
            for col in table_info.get('columns', []):
                self.known_columns.add(col.upper())
        
        # Also add metric names as valid "virtual columns"
        for metric in schema_config.get('metrics', {}).keys():
            self.known_columns.add(metric.upper())
    
    def extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL using regex patterns"""
        patterns = [
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        tables = []
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.extend(matches)
        return list(set(tables))
    
    def extract_columns(self, sql: str) -> List[str]:
        """Extract column names from SQL"""
        # Parse SQL to find column references
        parsed = sqlparse.parse(sql)[0]
        columns = []
        
        # Simple extraction - look for identifiers
        # (Production version would use proper SQL parsing)
        select_match = re.search(
            r'SELECT\s+(.*?)\s+FROM', 
            sql, 
            re.IGNORECASE | re.DOTALL
        )
        if select_match:
            select_clause = select_match.group(1)
            # Extract column names (simplified)
            col_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,|$|AS)'
            columns = re.findall(col_pattern, select_clause, re.IGNORECASE)
        
        return list(set(columns))
    
    def validate(self, sql: str) -> ValidationResult:
        """Validate SQL against known schema"""
        errors = []
        invalid_tables = []
        invalid_columns = []
        
        # Check tables
        tables = self.extract_tables(sql)
        for table in tables:
            if table.upper() not in self.known_tables:
                invalid_tables.append(table)
                errors.append(f"Table '{table}' does not exist in schema")
        
        # Check columns (if we have table context)
        columns = self.extract_columns(sql)
        for col in columns:
            # Skip common SQL keywords and functions
            if col.upper() in ['SUM', 'COUNT', 'AVG', 'MAX', 'MIN', 'AS', 'DISTINCT']:
                continue
            if col.upper() not in self.known_columns:
                invalid_columns.append(col)
                errors.append(f"Column '{col}' does not exist in schema")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            invalid_tables=invalid_tables,
            invalid_columns=invalid_columns
        )
```

### 4.4 Smart Self-Correction Loop

When SQL validation or execution fails, the system uses contextual error information to guide the LLM toward a correct solution.

```python
from enum import Enum
from typing import Optional

class ErrorCategory(Enum):
    SCHEMA_HALLUCINATION = "schema"      # Table/column doesn't exist
    SYNTAX_ERROR = "syntax"               # SQL syntax problem
    SEMANTIC_ERROR = "semantic"           # Logic/aggregation issue
    EXECUTION_ERROR = "execution"         # Runtime error (timeout, etc.)

class SmartCorrector:
    """Intelligent retry logic with categorized error handling"""
    
    def __init__(self, llm_client, sql_validator: SQLValidator, db_client):
        self.llm = llm_client
        self.validator = sql_validator
        self.db = db_client
        
        # Different retry strategies per error type
        self.retry_config = {
            ErrorCategory.SCHEMA_HALLUCINATION: {
                "max_retries": 2,
                "prompt_template": self._schema_correction_prompt
            },
            ErrorCategory.SYNTAX_ERROR: {
                "max_retries": 2,
                "prompt_template": self._syntax_correction_prompt
            },
            ErrorCategory.SEMANTIC_ERROR: {
                "max_retries": 1,
                "prompt_template": self._semantic_correction_prompt
            },
            ErrorCategory.EXECUTION_ERROR: {
                "max_retries": 1,
                "prompt_template": self._execution_correction_prompt
            }
        }
    
    async def generate_and_execute(
        self, 
        question: str, 
        context: dict
    ) -> QueryResult:
        """Main entry point: generate SQL, validate, execute with retries"""
        
        attempt_history = []
        
        for attempt in range(3):  # Overall max attempts
            # Step 1: Generate SQL
            sql = await self._generate_sql(question, context, attempt_history)
            
            # Step 2: Pre-execution validation
            validation = self.validator.validate(sql)
            
            if not validation.valid:
                # Schema hallucination - fix before hitting database
                attempt_history.append({
                    "sql": sql,
                    "error_type": ErrorCategory.SCHEMA_HALLUCINATION,
                    "errors": validation.errors
                })
                
                if attempt < 2:
                    continue  # Retry with error context
                else:
                    return self._fallback_response(question, attempt_history)
            
            # Step 3: Execute validated SQL
            try:
                result = await self.db.execute(sql)
                return QueryResult(
                    success=True,
                    sql=sql,
                    data=result,
                    attempts=attempt + 1
                )
                
            except SyntaxError as e:
                attempt_history.append({
                    "sql": sql,
                    "error_type": ErrorCategory.SYNTAX_ERROR,
                    "errors": [str(e)]
                })
                
            except SemanticError as e:
                attempt_history.append({
                    "sql": sql,
                    "error_type": ErrorCategory.SEMANTIC_ERROR,
                    "errors": [str(e)]
                })
                
            except Exception as e:
                attempt_history.append({
                    "sql": sql,
                    "error_type": ErrorCategory.EXECUTION_ERROR,
                    "errors": [str(e)]
                })
        
        # All retries exhausted
        return self._fallback_response(question, attempt_history)
    
    async def _generate_sql(
        self, 
        question: str, 
        context: dict, 
        attempt_history: list
    ) -> str:
        """Generate SQL, incorporating error context from previous attempts"""
        
        if not attempt_history:
            # First attempt - standard generation
            prompt = f"""
            Question: {question}
            
            Generate a SQL query to answer this question.
            Use only the tables and columns defined in the schema.
            """
        else:
            # Retry attempt - include error context
            last_attempt = attempt_history[-1]
            error_context = self._build_error_context(last_attempt)
            
            prompt = f"""
            Question: {question}
            
            Previous attempt failed with these errors:
            {error_context}
            
            Please fix the SQL query. Remember:
            - Only use tables that exist: {list(self.validator.known_tables)[:10]}...
            - Only use columns that exist in those tables
            - Check your JOIN conditions and aggregations
            """
        
        response = await self.llm.generate(prompt, context)
        return self._extract_sql(response)
    
    def _schema_correction_prompt(self, errors: list) -> str:
        return f"""
        The SQL references tables/columns that don't exist:
        {errors}
        
        Available tables: {list(self.validator.known_tables)}
        
        Please regenerate using only valid schema elements.
        """
    
    def _fallback_response(
        self, 
        question: str, 
        attempt_history: list
    ) -> QueryResult:
        """Graceful degradation when all retries fail"""
        
        return QueryResult(
            success=False,
            sql=None,
            data=None,
            attempts=len(attempt_history),
            fallback_message=f"""
            I had trouble generating the right query for "{question}".
            
            Here's what happened:
            - Attempts made: {len(attempt_history)}
            - Last error: {attempt_history[-1]['errors'][0] if attempt_history else 'Unknown'}
            
            You could try:
            • Rephrasing your question with specific metric names
            • Example: "Show me the 30+ day delinquency rate by region for Q4"
            • Or ask me: "What metrics are available for delinquency?"
            """,
            suggested_questions=[
                "What metrics can you report on?",
                "Show me originations by region",
                "What is the current delinquency rate?"
            ]
        )
```
```

---

## 5. Reliability & Quality Assurance

This section covers critical components that ensure the system works reliably during demonstrations and real-world usage.

### 12.1 Ambiguity Detection & Clarification

Credit risk terminology is often ambiguous. When users ask vague questions, the system should ask for clarification rather than guess wrong.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AMBIGUITY HANDLING FLOW                       │
│                                                                  │
│  User: "What's our exposure?"                                    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              AMBIGUITY DETECTION                            │ │
│  │                                                             │ │
│  │  Term detected: "exposure"                                  │ │
│  │                                                             │ │
│  │  Possible meanings:                                         │ │
│  │    • Gross Credit Exposure (BPCRA013)                      │ │
│  │    • Net Credit Exposure (BPCRA094)                        │ │
│  │    • Exposure at Default (BPCRA156)                        │ │
│  │    • Credit Line Exposure (BPCRA203)                       │ │
│  │                                                             │ │
│  │  Missing context:                                           │ │
│  │    • Time period not specified                             │ │
│  │    • Region/product filter not specified                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              CLARIFICATION RESPONSE                         │ │
│  │                                                             │ │
│  │  "I want to make sure I give you the right data.           │ │
│  │                                                             │ │
│  │   Which type of exposure are you interested in?            │ │
│  │   • Gross Credit Exposure (total exposure before           │ │
│  │     risk mitigation)                                        │ │
│  │   • Net Credit Exposure (after collateral/guarantees)      │ │
│  │   • Exposure at Default (for ECL calculations)             │ │
│  │                                                             │ │
│  │   Or I can show you Gross Credit Exposure by region        │ │
│  │   for the current quarter — just say 'go ahead'."          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class AmbiguousTerm:
    term: str
    options: List[Dict[str, str]]  # {name, description, metric_id}
    default: str
    
@dataclass 
class ClarificationRequest:
    message: str
    ambiguities: List[AmbiguousTerm]
    default_action: str
    example_query: str

class AmbiguityDetector:
    """Detects ambiguous terms and missing context in user questions"""
    
    # Credit risk terms with multiple meanings
    AMBIGUOUS_TERMS = {
        "exposure": {
            "options": [
                {"name": "Gross Credit Exposure", "description": "Total exposure before risk mitigation", "metric": "gross_credit_exposure"},
                {"name": "Net Credit Exposure", "description": "Exposure after collateral deductions", "metric": "net_credit_exposure"},
                {"name": "Exposure at Default", "description": "Expected exposure at time of default", "metric": "ead"},
            ],
            "default": "gross_credit_exposure",
            "triggers": ["exposure", "total exposure"]
        },
        "delinquency": {
            "options": [
                {"name": "30+ Days Past Due", "description": "Accounts 30 or more days delinquent", "metric": "delinquency_rate_30"},
                {"name": "60+ Days Past Due", "description": "Accounts 60 or more days delinquent", "metric": "delinquency_rate_60"},
                {"name": "90+ Days Past Due", "description": "Serious delinquency (90+ days)", "metric": "delinquency_rate_90"},
            ],
            "default": "delinquency_rate_30",
            "triggers": ["delinquency", "delinquent", "past due", "dpd"]
        },
        "loss": {
            "options": [
                {"name": "Net Charge-Off", "description": "Gross write-offs minus recoveries", "metric": "nco_rate"},
                {"name": "Expected Credit Loss", "description": "IFRS 9 provision amount", "metric": "ecl"},
                {"name": "Gross Write-Off", "description": "Total amounts written off", "metric": "gross_writeoff"},
            ],
            "default": "nco_rate",
            "triggers": ["loss", "losses", "write-off", "charge-off"]
        },
        "balance": {
            "options": [
                {"name": "Outstanding Balance", "description": "Current principal outstanding", "metric": "outstanding_balance"},
                {"name": "Adjusted Outstanding Balance", "description": "Balance adjusted for accounting", "metric": "adjusted_outstanding"},
                {"name": "Average Balance", "description": "Average over period", "metric": "avg_balance"},
            ],
            "default": "outstanding_balance",
            "triggers": ["balance", "outstanding"]
        }
    }
    
    # Context that should be specified
    RECOMMENDED_CONTEXT = {
        "time_period": {
            "patterns": ["q1", "q2", "q3", "q4", "quarter", "month", "year", "ytd", "mtd", "2024", "2025"],
            "prompt": "For which time period?",
            "default": "current quarter"
        },
        "region": {
            "patterns": ["north", "south", "east", "west", "central", "region", "all regions"],
            "prompt": "For which region?",
            "default": "all regions"
        },
        "product": {
            "patterns": ["mortgage", "auto", "credit card", "personal", "commercial", "product"],
            "prompt": "For which product?",
            "default": "all products"
        }
    }
    
    def detect_ambiguity(self, question: str) -> Optional[ClarificationRequest]:
        """Analyze question for ambiguous terms and missing context"""
        
        question_lower = question.lower()
        ambiguities = []
        
        # Check for ambiguous terms
        for term_key, term_config in self.AMBIGUOUS_TERMS.items():
            for trigger in term_config["triggers"]:
                if trigger in question_lower:
                    # Check if user already specified which type
                    already_specified = any(
                        opt["name"].lower() in question_lower 
                        for opt in term_config["options"]
                    )
                    
                    if not already_specified:
                        ambiguities.append(AmbiguousTerm(
                            term=term_key,
                            options=term_config["options"],
                            default=term_config["default"]
                        ))
                    break
        
        # Check for missing context (optional - don't always ask)
        missing_context = []
        for context_key, context_config in self.RECOMMENDED_CONTEXT.items():
            has_context = any(p in question_lower for p in context_config["patterns"])
            if not has_context:
                missing_context.append(context_key)
        
        # Only ask for clarification if there are ambiguous terms
        # Missing context alone shouldn't block - use defaults
        if ambiguities:
            return self._build_clarification(question, ambiguities, missing_context)
        
        return None
    
    def _build_clarification(
        self, 
        question: str, 
        ambiguities: List[AmbiguousTerm],
        missing_context: List[str]
    ) -> ClarificationRequest:
        """Build a helpful clarification request"""
        
        primary_ambiguity = ambiguities[0]
        
        # Build option list
        options_text = "\n".join([
            f"  • **{opt['name']}**: {opt['description']}"
            for opt in primary_ambiguity.options
        ])
        
        # Build default action
        default_opt = next(
            (o for o in primary_ambiguity.options if o['metric'] == primary_ambiguity.default),
            primary_ambiguity.options[0]
        )
        
        message = f"""I want to make sure I give you the right data.

Which type of **{primary_ambiguity.term}** are you interested in?
{options_text}

Or I can show you **{default_opt['name']}** by region for the current quarter — just say "go ahead"."""
        
        # Build example of a clear query
        example = f"Show me {default_opt['name'].lower()} by region for Q4 2025"
        
        return ClarificationRequest(
            message=message,
            ambiguities=ambiguities,
            default_action=f"Show {default_opt['name']} by region for current quarter",
            example_query=example
        )
    
    def apply_defaults(self, question: str, ambiguities: List[AmbiguousTerm]) -> str:
        """When user says 'go ahead', apply default interpretations"""
        
        enhanced_question = question
        for amb in ambiguities:
            default_opt = next(
                (o for o in amb.options if o['metric'] == amb.default),
                amb.options[0]
            )
            # Add clarification to question
            enhanced_question += f" (using {default_opt['name']})"
        
        return enhanced_question
```

### 12.2 Conversation Flow with Clarification

```
┌─────────────────────────────────────────────────────────────────┐
│              CLARIFICATION INTEGRATION FLOW                      │
│                                                                  │
│  ┌──────────────┐                                               │
│  │ User Message │                                               │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Ambiguity Detector                                        │   │
│  │ detect_ambiguity(question)                                │   │
│  └──────┬───────────────────────────────────────┬───────────┘   │
│         │                                       │                │
│    [Ambiguous]                            [Clear]                │
│         │                                       │                │
│         ▼                                       ▼                │
│  ┌──────────────────┐                ┌──────────────────────┐   │
│  │ Return           │                │ Proceed to SQL       │   │
│  │ Clarification    │                │ Generation           │   │
│  │ Request          │                │                      │   │
│  └──────┬───────────┘                └──────────────────────┘   │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ User Response Options:                                    │   │
│  │                                                           │   │
│  │ • "Gross exposure" → Re-process with clarified term      │   │
│  │ • "Go ahead" → Apply defaults, proceed                   │   │
│  │ • "Net Credit Exposure by product" → Full clarification  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 12.3 Golden Test Dataset

Before any demonstration, validate the system against a curated set of known-good queries. This ensures predictable behavior during live demos.

```yaml
# golden_test_queries.yaml
# Run these tests before every demo to ensure system reliability

version: "1.0"
last_updated: "2025-12-14"

test_suites:

  # ============================================
  # SUITE 1: Basic Single-Metric Queries
  # These should work 100% of the time
  # ============================================
  basic_queries:
    description: "Simple fact retrieval - must pass for demo"
    
    - id: basic_001
      question: "What are the total originations by region?"
      expected:
        tables_used: ["FCT_CREDIT_RISK", "DIM_GEOGRAPHY"]
        has_group_by: true
        returns_data: true
      tags: ["demo-critical", "simple"]
      
    - id: basic_002
      question: "Show me the delinquency rate for Q4 2025"
      expected:
        metric_used: "delinquency_rate_30"
        time_filter: "Q4-2025"
        returns_data: true
      tags: ["demo-critical", "simple"]
      
    - id: basic_003
      question: "What is our total outstanding balance?"
      expected:
        metric_used: "outstanding_balance"
        aggregation: "SUM"
        returns_data: true
      tags: ["demo-critical", "simple"]
      
    - id: basic_004
      question: "How many accounts do we have by product type?"
      expected:
        tables_used: ["FCT_CREDIT_RISK", "DIM_PRODUCT"]
        aggregation: "COUNT"
        has_group_by: true
      tags: ["demo-critical", "simple"]

  # ============================================
  # SUITE 2: Comparison Queries
  # Region vs region, period vs period
  # ============================================
  comparison_queries:
    description: "Comparative analysis queries"
    
    - id: compare_001
      question: "Compare originations between North and South regions"
      expected:
        regions_filtered: ["North", "South"]
        returns_multiple_rows: true
      tags: ["demo-critical", "comparison"]
      
    - id: compare_002
      question: "How does Q4 delinquency compare to Q3?"
      expected:
        time_periods: ["Q3", "Q4"]
        metric_used: "delinquency_rate"
      tags: ["comparison", "time-series"]
      
    - id: compare_003
      question: "Show credit quality metrics for Auto vs Mortgage"
      expected:
        products_filtered: ["Auto", "Mortgage"]
        multiple_metrics: true
      tags: ["comparison", "product"]

  # ============================================
  # SUITE 3: Investigation Flow Queries
  # Multi-step analysis - the "wow" factor
  # ============================================
  investigation_queries:
    description: "Progressive investigation capabilities"
    
    - id: investigate_001
      question: "Originations in South seem high - is credit quality deteriorating?"
      expected:
        intent: "investigation"
        generates_hypotheses: true
        checks_multiple_metrics: true
        metrics_checked:
          - "credit_score_trend"
          - "subprime_mix"
          - "ltv_ratio"
      tags: ["demo-wow", "investigation"]
      
    - id: investigate_002
      question: "Why is delinquency increasing in the Auto portfolio?"
      expected:
        intent: "investigation"
        drills_down: true
        suggests_follow_ups: true
      tags: ["demo-wow", "investigation"]

  # ============================================
  # SUITE 4: Edge Cases & Ambiguity
  # Test clarification flow
  # ============================================
  edge_cases:
    description: "Ambiguous or incomplete queries"
    
    - id: edge_001
      question: "What's our exposure?"
      expected:
        triggers_clarification: true
        offers_options: ["Gross Credit Exposure", "Net Credit Exposure", "EAD"]
      tags: ["clarification"]
      
    - id: edge_002
      question: "Show me the losses"
      expected:
        triggers_clarification: true
        offers_options: ["Net Charge-Off", "ECL", "Gross Write-Off"]
      tags: ["clarification"]
      
    - id: edge_003
      question: "How are we doing?"
      expected:
        triggers_clarification: true
        asks_for_specifics: true
      tags: ["clarification", "vague"]

  # ============================================
  # SUITE 5: Negative Tests (Should Handle Gracefully)
  # ============================================
  negative_tests:
    description: "Queries that should fail gracefully"
    
    - id: negative_001
      question: "What's the weather like today?"
      expected:
        graceful_decline: true
        suggests_alternatives: true
      tags: ["out-of-scope"]
      
    - id: negative_002
      question: "Show me data from the CUSTOMERS table"
      expected:
        error_handling: true  # Table doesn't exist
        suggests_valid_tables: true
      tags: ["invalid-schema"]
```

```python
import yaml
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class TestResult:
    test_id: str
    question: str
    passed: bool
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    error: str = None
    execution_time_ms: float = 0

@dataclass
class TestSuiteResult:
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    results: List[TestResult]

class GoldenTestRunner:
    """Runs golden test suite to validate system before demos"""
    
    def __init__(self, query_engine, config_path: str = "golden_test_queries.yaml"):
        self.query_engine = query_engine
        self.config = self._load_config(config_path)
        
    def _load_config(self, path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)
    
    async def run_all_tests(self) -> Dict[str, TestSuiteResult]:
        """Run all test suites"""
        results = {}
        
        for suite_name, suite_config in self.config.get('test_suites', {}).items():
            suite_result = await self._run_suite(suite_name, suite_config)
            results[suite_name] = suite_result
            
        return results
    
    async def run_critical_tests_only(self) -> Dict[str, TestSuiteResult]:
        """Run only tests tagged as 'demo-critical' - fast pre-demo check"""
        results = {}
        
        for suite_name, suite_config in self.config.get('test_suites', {}).items():
            critical_tests = [
                t for t in suite_config.get('tests', suite_config)
                if isinstance(t, dict) and 'demo-critical' in t.get('tags', [])
            ]
            
            if critical_tests:
                suite_result = await self._run_suite(
                    f"{suite_name}_critical", 
                    critical_tests
                )
                results[suite_name] = suite_result
                
        return results
    
    async def _run_suite(self, suite_name: str, tests: list) -> TestSuiteResult:
        """Run a single test suite"""
        results = []
        
        # Handle both list of tests and dict with description
        test_list = tests if isinstance(tests, list) else tests.get('tests', [])
        
        for test in test_list:
            if not isinstance(test, dict) or 'question' not in test:
                continue
                
            result = await self._run_single_test(test)
            results.append(result)
        
        passed = sum(1 for r in results if r.passed)
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=len(results),
            passed=passed,
            failed=len(results) - passed,
            results=results
        )
    
    async def _run_single_test(self, test: dict) -> TestResult:
        """Run a single test case"""
        start_time = datetime.now()
        
        try:
            # Execute the query
            response = await self.query_engine.process(test['question'])
            
            # Validate against expectations
            passed, actual = self._validate_response(response, test['expected'])
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestResult(
                test_id=test.get('id', 'unknown'),
                question=test['question'],
                passed=passed,
                expected=test['expected'],
                actual=actual,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return TestResult(
                test_id=test.get('id', 'unknown'),
                question=test['question'],
                passed=False,
                expected=test['expected'],
                actual={},
                error=str(e)
            )
    
    def _validate_response(self, response, expected: dict) -> tuple:
        """Validate response against expected criteria"""
        actual = {}
        all_passed = True
        
        # Check if data was returned
        if 'returns_data' in expected:
            actual['returns_data'] = response.data is not None and len(response.data) > 0
            if expected['returns_data'] != actual['returns_data']:
                all_passed = False
        
        # Check if clarification was triggered
        if 'triggers_clarification' in expected:
            actual['triggers_clarification'] = response.needs_clarification
            if expected['triggers_clarification'] != actual['triggers_clarification']:
                all_passed = False
        
        # Check tables used (from SQL)
        if 'tables_used' in expected:
            actual['tables_used'] = self._extract_tables(response.sql)
            if not set(expected['tables_used']).issubset(set(actual['tables_used'])):
                all_passed = False
        
        # Check for graceful error handling
        if 'graceful_decline' in expected:
            actual['graceful_decline'] = response.is_out_of_scope
            if expected['graceful_decline'] != actual['graceful_decline']:
                all_passed = False
        
        return all_passed, actual
    
    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        if not sql:
            return []
        import re
        pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        return re.findall(pattern, sql, re.IGNORECASE)
    
    def print_report(self, results: Dict[str, TestSuiteResult]):
        """Print a formatted test report"""
        print("\n" + "="*60)
        print("CR360 GOLDEN TEST REPORT")
        print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        total_passed = 0
        total_tests = 0
        
        for suite_name, suite_result in results.items():
            status = "✅" if suite_result.failed == 0 else "❌"
            print(f"\n{status} {suite_name}: {suite_result.passed}/{suite_result.total_tests} passed")
            
            total_passed += suite_result.passed
            total_tests += suite_result.total_tests
            
            # Show failed tests
            for result in suite_result.results:
                if not result.passed:
                    print(f"   ❌ {result.test_id}: {result.question[:50]}...")
                    if result.error:
                        print(f"      Error: {result.error}")
        
        print("\n" + "-"*60)
        overall_status = "✅ READY FOR DEMO" if total_passed == total_tests else "⚠️ FIX ISSUES BEFORE DEMO"
        print(f"OVERALL: {total_passed}/{total_tests} tests passed")
        print(overall_status)
        print("="*60 + "\n")


# Pre-demo smoke test script
async def run_pre_demo_check():
    """Quick check to run before any demo"""
    
    from cr360.query_engine import QueryEngine
    
    engine = QueryEngine()
    runner = GoldenTestRunner(engine)
    
    print("🔍 Running pre-demo checks...")
    results = await runner.run_critical_tests_only()
    runner.print_report(results)
    
    # Return True if all critical tests pass
    all_passed = all(r.failed == 0 for r in results.values())
    
    if not all_passed:
        print("⚠️  WARNING: Some critical tests failed!")
        print("    Review failures before proceeding with demo.\n")
    
    return all_passed

# Usage:
# python -c "import asyncio; from cr360.tests import run_pre_demo_check; asyncio.run(run_pre_demo_check())"
```

### 12.4 Pre-Demo Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRE-DEMO VALIDATION CHECKLIST                 │
│                                                                  │
│  Run this 30 minutes before any demo:                           │
│                                                                  │
│  □ 1. Run golden test suite                                     │
│       $ python -m cr360.tests.run_pre_demo_check                │
│       Expected: "✅ READY FOR DEMO"                              │
│                                                                  │
│  □ 2. Verify database connectivity                              │
│       $ python -m cr360.health.check_db                         │
│       Expected: "Database: Connected"                            │
│                                                                  │
│  □ 3. Verify LLM API connectivity                               │
│       $ python -m cr360.health.check_llm                        │
│       Expected: "Gemini API: Available"                          │
│                                                                  │
│  □ 4. Test specific demo questions manually                     │
│       Try the exact questions you plan to demo                  │
│                                                                  │
│  □ 5. Clear any cached responses (fresh demo)                   │
│       $ python -m cr360.cache.clear                             │
│                                                                  │
│  □ 6. Check context file is loaded                              │
│       $ python -m cr360.context.verify                          │
│       Expected: "Context loaded: 127 metrics, 23 tables"        │
│                                                                  │
│  IF ANY CHECK FAILS:                                             │
│  • Do NOT proceed with demo                                      │
│  • Fix the issue or reschedule                                  │
│  • Never discover bugs during a live demo                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Progressive Investigation Agent

### 12.1 Investigation Philosophy

The Investigation Agent enables **root cause analysis through conversation**. When a user observes an anomaly (e.g., "South region originations are too high"), the agent:

1. **Acknowledges** the observation
2. **Maps** to relevant credit quality metrics
3. **Retrieves** the data
4. **Synthesizes** insights
5. **Suggests** further investigation paths

### 12.2 Investigation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROGRESSIVE INVESTIGATION AGENT               │
│                                                                  │
│  User: "Originations in South are too high compared to others,  │
│         figure out whether credit quality is eroding in South"  │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 1: HYPOTHESIS GENERATION                  │ │
│  │                                                             │ │
│  │  Observation: High originations in South                    │ │
│  │  User Concern: Credit quality erosion                       │ │
│  │                                                             │ │
│  │  Generated Hypotheses:                                      │ │
│  │  H1: Credit scores of new originations are declining        │ │
│  │  H2: Higher risk segments (subprime) increasing             │ │
│  │  H3: LTV ratios are increasing                             │ │
│  │  H4: DTI ratios are deteriorating                          │ │
│  │  H5: Approval rates have loosened                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 2: METRIC MAPPING                         │ │
│  │                                                             │ │
│  │  "Credit Quality" Domain Knowledge:                         │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │ Credit Quality Indicators                            │   │ │
│  │  ├─────────────────────────────────────────────────────┤   │ │
│  │  │ • Average Credit Score (BPCRA279, BPMV103)           │   │ │
│  │  │ • 1-Year PD (BPCRA326, BPMV040)                      │   │ │
│  │  │ • LTV Ratio (BPCRA102, BPMV080)                      │   │ │
│  │  │ • DTI/TDS Ratio (BPCRA132, BPMV101)                  │   │ │
│  │  │ • Risk Grade Distribution                            │   │ │
│  │  │ • Subprime Mix %                                     │   │ │
│  │  │ • Approval Rate                                      │   │ │
│  │  │ • Exception Rate                                     │   │ │
│  │  └─────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 3: MULTI-QUERY EXECUTION                  │ │
│  │                                                             │ │
│  │  Execute queries for each hypothesis:                       │ │
│  │                                                             │ │
│  │  Query 1: Credit score trends by region (originations)     │ │
│  │  Query 2: Customer segment mix by region                   │ │
│  │  Query 3: LTV distribution by region                       │ │
│  │  Query 4: DTI distribution by region                       │ │
│  │  Query 5: Approval rates by region over time               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 4: INSIGHT SYNTHESIS                      │ │
│  │                                                             │ │
│  │  Findings:                                                  │ │
│  │  ✓ H1: CONFIRMED - Avg credit score in South dropped       │ │
│  │        from 720 to 695 (-25 pts) vs stable elsewhere       │ │
│  │  ✓ H2: CONFIRMED - Subprime mix increased from 15% to 28%  │ │
│  │  ✓ H3: CONFIRMED - Average LTV increased from 78% to 85%   │ │
│  │  ✗ H4: NOT CONFIRMED - DTI stable across all regions       │ │
│  │  ✓ H5: CONFIRMED - Approval rate in South: 72% vs          │ │
│  │        industry avg 65%                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              STEP 5: RESPONSE WITH VISUALIZATIONS           │ │
│  │                                                             │ │
│  │  "Based on my analysis, credit quality IS deteriorating    │ │
│  │   in the South region. Here's what I found:                │ │
│  │                                                             │ │
│  │   [Bar Chart: Credit Score by Region - Originations]       │ │
│  │   [Line Chart: Subprime Mix Trend by Region]               │ │
│  │   [Table: Comparative Metrics Summary]                      │ │
│  │                                                             │ │
│  │   Key concerns:                                             │ │
│  │   1. Credit scores dropped 25 points vs stable elsewhere   │ │
│  │   2. Subprime mix nearly doubled (15% → 28%)               │ │
│  │   3. LTV ratios increased 7 percentage points              │ │
│  │                                                             │ │
│  │   Would you like me to:                                     │ │
│  │   • Drill down by product type in the South?               │ │
│  │   • Compare to historical vintages?                        │ │
│  │   • Identify specific branches driving this trend?"        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 12.3 Credit Risk Domain Knowledge Graph

The Investigation Agent uses a domain knowledge graph to understand relationships between metrics:

```
┌─────────────────────────────────────────────────────────────────┐
│              CREDIT RISK KNOWLEDGE GRAPH                         │
│                                                                  │
│                    ┌─────────────────┐                          │
│                    │ CREDIT QUALITY  │                          │
│                    └────────┬────────┘                          │
│           ┌─────────────────┼─────────────────┐                 │
│           ▼                 ▼                 ▼                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Origination  │  │ Portfolio    │  │ Performance  │          │
│  │ Quality      │  │ Composition  │  │ Indicators   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│    ┌────┴────┐       ┌────┴────┐       ┌────┴────┐             │
│    ▼         ▼       ▼         ▼       ▼         ▼             │
│ Credit    LTV     Segment   Product  DQ Rate   NCO            │
│ Score     DTI     Mix       Mix      Trend     Rate           │
│                                                                  │
│  CAUSAL RELATIONSHIPS:                                          │
│  • Lower credit scores → Higher PD → Higher ECL                │
│  • Higher LTV → Higher LGD → Higher NCO                        │
│  • More subprime → Higher DQ rates                             │
│  • Higher approval rates → Lower credit quality                │
│                                                                  │
│  INVESTIGATION PATHS:                                           │
│  "High originations" → Check credit quality metrics            │
│  "Rising delinquency" → Check vintage, product, segment mix    │
│  "NCO increase" → Check LGD drivers, collateral, recovery      │
└─────────────────────────────────────────────────────────────────┘
```

### 12.4 Investigation State Machine

```python
class InvestigationState:
    """Tracks the state of a progressive investigation"""
    
    def __init__(self):
        self.observation = None           # Initial user observation
        self.hypotheses = []              # Generated hypotheses
        self.tested_hypotheses = {}       # Results of hypothesis tests
        self.confirmed_findings = []      # Validated insights
        self.investigation_path = []      # Breadcrumb trail
        self.active_filters = {}          # Current dimension filters
        self.suggested_next_steps = []    # AI-suggested follow-ups
        
    def add_finding(self, hypothesis: str, result: HypothesisResult):
        """Add a tested hypothesis result"""
        self.tested_hypotheses[hypothesis] = result
        if result.confirmed:
            self.confirmed_findings.append({
                'hypothesis': hypothesis,
                'evidence': result.evidence,
                'metrics': result.metrics,
                'visualizations': result.visualizations
            })
            
    def suggest_next_steps(self) -> List[str]:
        """Generate contextual follow-up suggestions"""
        suggestions = []
        
        # Based on confirmed findings, suggest deeper dives
        for finding in self.confirmed_findings:
            if 'credit_score' in finding['metrics']:
                suggestions.append("Drill down by customer segment")
                suggestions.append("Compare to origination vintage trends")
            if 'segment_mix' in finding['metrics']:
                suggestions.append("Analyze pricing for each segment")
                suggestions.append("Check approval rate by segment")
                
        return suggestions[:3]  # Top 3 suggestions
```

---

## 7. Visualization Intelligence

### 12.1 Automatic Chart Selection

The Visualization Intelligence module analyzes data characteristics and user intent to select the optimal visualization.

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION INTELLIGENCE                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              DATA PROFILER                                  │ │
│  │                                                             │ │
│  │  Analyzes:                                                  │ │
│  │  • Number of dimensions (1, 2, 3+)                         │ │
│  │  • Number of measures (1, 2, multiple)                     │ │
│  │  • Cardinality of dimensions (5, 20, 100+)                 │ │
│  │  • Data type (categorical, temporal, numeric)              │ │
│  │  • Data distribution (normal, skewed, outliers)            │ │
│  │  • Time series presence (yes/no)                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              INTENT ANALYZER                                │ │
│  │                                                             │ │
│  │  Determines visualization purpose:                          │ │
│  │  • Comparison (A vs B vs C)                                │ │
│  │  • Trend (change over time)                                │ │
│  │  • Distribution (spread of values)                         │ │
│  │  • Composition (parts of a whole)                          │ │
│  │  • Relationship (correlation)                              │ │
│  │  • Geographic (spatial patterns)                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              CHART RECOMMENDER                              │ │
│  │                                                             │ │
│  │  Decision Matrix:                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │ Intent      │ Dimensions │ Measures │ Chart Type    │   │ │
│  │  ├─────────────┼────────────┼──────────┼───────────────┤   │ │
│  │  │ Comparison  │ 1 (low)    │ 1        │ Bar Chart     │   │ │
│  │  │ Comparison  │ 1 (high)   │ 1        │ Horizontal Bar│   │ │
│  │  │ Comparison  │ 2          │ 1        │ Grouped Bar   │   │ │
│  │  │ Trend       │ Time       │ 1        │ Line Chart    │   │ │
│  │  │ Trend       │ Time       │ 2+       │ Multi-Line    │   │ │
│  │  │ Distribution│ 1          │ 1        │ Histogram     │   │ │
│  │  │ Composition │ 1 (low)    │ 1        │ Pie Chart     │   │ │
│  │  │ Composition │ 1 (high)   │ 1        │ Treemap       │   │ │
│  │  │ Composition │ Time       │ 1        │ Stacked Area  │   │ │
│  │  │ Relationship│ 2          │ 0        │ Scatter Plot  │   │ │
│  │  │ Geographic  │ Location   │ 1        │ Choropleth Map│   │ │
│  │  │ Tabular     │ Many       │ Many     │ Data Table    │   │ │
│  │  └─────────────┴────────────┴──────────┴───────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 Chart Selection Algorithm

```python
class VisualizationIntelligence:
    
    def recommend_chart(
        self, 
        data: DataFrame, 
        intent: str,
        context: InvestigationContext
    ) -> ChartRecommendation:
        
        # Profile the data
        profile = self.profile_data(data)
        
        # Determine best chart type
        if intent == "comparison":
            if profile.dimension_cardinality <= 7:
                chart_type = "bar"
            elif profile.dimension_cardinality <= 15:
                chart_type = "horizontal_bar"
            else:
                chart_type = "table"  # Too many categories for chart
                
        elif intent == "trend":
            if profile.has_time_dimension:
                if profile.num_series <= 5:
                    chart_type = "line"
                else:
                    chart_type = "multi_line_with_legend"
            else:
                chart_type = "line"  # Treat as sequential
                
        elif intent == "composition":
            if profile.has_time_dimension:
                chart_type = "stacked_area"
            elif profile.dimension_cardinality <= 5:
                chart_type = "pie"
            else:
                chart_type = "treemap"
                
        elif intent == "distribution":
            chart_type = "histogram"
            
        elif intent == "relationship":
            chart_type = "scatter"
            
        elif intent == "geographic":
            chart_type = "choropleth_map"
            
        else:
            chart_type = "table"  # Safe fallback
            
        # Generate chart config
        return ChartRecommendation(
            chart_type=chart_type,
            config=self.generate_config(chart_type, data, profile),
            explanation=self.explain_choice(chart_type, profile, intent)
        )
```

### 12.3 Visualization Examples for Credit Risk

| User Question | Data Characteristics | Recommended Visualization |
|---------------|---------------------|---------------------------|
| "Show originations by region" | 1 dimension (5 categories), 1 measure | **Bar Chart** |
| "How has delinquency trended this year?" | Time series, 1 measure | **Line Chart** |
| "Compare credit quality across segments" | 1 dimension, multiple measures | **Grouped Bar / Radar** |
| "What's the portfolio composition by product?" | 1 dimension (7 categories), 1 measure | **Pie / Donut Chart** |
| "Show LTV distribution for new originations" | 1 continuous measure | **Histogram** |
| "Is there a relationship between DTI and delinquency?" | 2 continuous measures | **Scatter Plot** |
| "Show NCO by state" | Geographic dimension, 1 measure | **Choropleth Map** |
| "Give me full details on South region" | Many dimensions, many measures | **Data Table** |
| "How has segment mix changed over time?" | Time + categories, 1 measure | **Stacked Area Chart** |

### 12.4 Narrative Generation

Along with visualizations, the system generates natural language narratives:

```python
def generate_narrative(
    data: DataFrame,
    chart_type: str,
    context: InvestigationContext
) -> str:
    """Generate a natural language summary of the visualization"""
    
    # Key statistics
    max_value = data['value'].max()
    max_label = data.loc[data['value'].idxmax(), 'label']
    min_value = data['value'].min()
    min_label = data.loc[data['value'].idxmin(), 'label']
    total = data['value'].sum()
    
    # Generate narrative based on context
    if context.intent == "comparison":
        narrative = f"""
        **Key Insights:**
        - {max_label} leads with ${max_value:,.0f} ({max_value/total*100:.1f}% of total)
        - {min_label} has the lowest at ${min_value:,.0f}
        - The gap between highest and lowest is ${max_value - min_value:,.0f}
        """
    
    elif context.intent == "trend":
        first_value = data.iloc[0]['value']
        last_value = data.iloc[-1]['value']
        change_pct = (last_value - first_value) / first_value * 100
        
        direction = "increased" if change_pct > 0 else "decreased"
        narrative = f"""
        **Trend Summary:**
        - Overall {direction} by {abs(change_pct):.1f}%
        - Started at ${first_value:,.0f}, ended at ${last_value:,.0f}
        """
    
    return narrative
```

---

## 8. Credit Risk Domain Knowledge

### 12.1 Pre-built Investigation Templates

The system includes domain-specific investigation templates for common credit risk scenarios:

```yaml
investigation_templates:
  
  credit_quality_deterioration:
    trigger_keywords: ["credit quality", "deteriorating", "declining", "eroding"]
    metrics_to_analyze:
      - average_credit_score_originations
      - average_pd
      - segment_mix_subprime_pct
      - average_ltv
      - average_dti
      - approval_rate
      - exception_rate
    comparison_dimensions: [region, product, vintage]
    visualizations:
      - type: trend_line
        metrics: [credit_score, subprime_pct]
        by: time
      - type: bar_comparison
        metrics: [ltv, dti]
        by: region
        
  delinquency_spike:
    trigger_keywords: ["delinquency", "DPD", "past due", "spike", "increase"]
    metrics_to_analyze:
      - dq_rate_30
      - dq_rate_60
      - dq_rate_90
      - roll_rate_30_to_60
      - roll_rate_60_to_90
      - cure_rate
    comparison_dimensions: [vintage, product, segment]
    root_cause_hypotheses:
      - "Recent vintages underperforming"
      - "Specific product driving delinquency"
      - "Economic factors in specific regions"
      - "Credit policy changes"
      
  loss_rate_analysis:
    trigger_keywords: ["loss", "NCO", "charge-off", "write-off"]
    metrics_to_analyze:
      - gross_charge_off_rate
      - recovery_rate
      - net_charge_off_rate
      - lgd
      - collateral_coverage
    comparison_dimensions: [vintage, product, recovery_channel]
    
  concentration_risk:
    trigger_keywords: ["concentration", "exposure", "top", "largest"]
    metrics_to_analyze:
      - top_10_exposure_pct
      - hhi_index
      - single_name_exposure
      - industry_concentration
    visualizations:
      - type: treemap
        dimension: counterparty
        measure: exposure
      - type: pie
        dimension: industry
        measure: exposure
```

### 12.2 Credit Risk Metric Relationships

```yaml
metric_relationships:
  
  # Causal chains
  causal_chains:
    - path: [lower_credit_score → higher_pd → higher_ecl]
      explanation: "Lower credit scores indicate higher likelihood of default"
      
    - path: [higher_ltv → higher_lgd → higher_loss]
      explanation: "Higher LTV means less equity cushion, higher loss given default"
      
    - path: [higher_dti → payment_stress → higher_delinquency]
      explanation: "Higher debt burden increases payment difficulty"
      
    - path: [relaxed_underwriting → higher_approval_rate → lower_credit_quality]
      explanation: "Easier approvals typically mean accepting higher risk"
      
  # Leading indicators
  leading_indicators:
    delinquency:
      - credit_score_at_origination
      - economic_indicators
      - payment_behavior_score
    loss:
      - delinquency_rate
      - collateral_values
      - unemployment_rate
      
  # Composite metrics
  composite_metrics:
    portfolio_health_score:
      components:
        - metric: delinquency_rate_30
          weight: 0.25
          direction: inverse
        - metric: average_credit_score
          weight: 0.25
          direction: direct
        - metric: net_charge_off_rate
          weight: 0.25
          direction: inverse
        - metric: coverage_ratio
          weight: 0.25
          direction: direct
```

---

## 9. Data Flow Architecture

### 12.1 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW ARCHITECTURE                                 │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    1. DATA INGESTION                                       │  │
│  │                                                                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Core Banking│  │ OFSAA/Risk  │  │ External    │  │ Market      │      │  │
│  │  │ Systems     │  │ Systems     │  │ Bureau Data │  │ Data        │      │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │  │
│  │         │                │                │                │              │  │
│  │         └────────────────┴────────────────┴────────────────┘              │  │
│  │                                   │                                        │  │
│  │                                   ▼                                        │  │
│  │                    ┌─────────────────────────────┐                        │  │
│  │                    │    ETL / Data Pipeline      │                        │  │
│  │                    │    (Airflow / dbt)          │                        │  │
│  │                    └──────────────┬──────────────┘                        │  │
│  └───────────────────────────────────┼───────────────────────────────────────┘  │
│                                      │                                          │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐  │
│  │                    2. DATA STORAGE                                         │  │
│  │                                   ▼                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │              DATA WAREHOUSE (Snowflake / BigQuery / Databricks)      │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │  │  │
│  │  │  │ Raw Layer   │  │ Curated     │  │ Aggregated / Mart Layer     │  │  │  │
│  │  │  │ (Staging)   │  │ Layer       │  │ (Pre-computed metrics)      │  │  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────┼───────────────────────────────────────┘  │
│                                      │                                          │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐  │
│  │                    3. CONTEXT LAYER                                        │  │
│  │                                   ▼                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │              CONTEXT FILE (credit_risk_context.yaml)                 │  │  │
│  │  │  • Metric definitions with SQL formulas                             │  │  │
│  │  │  • Table schemas and join relationships                             │  │  │
│  │  │  • Dimension hierarchies and valid values                           │  │  │
│  │  │  • Business rules for query generation                              │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────┼───────────────────────────────────────┘  │
│                                      │                                          │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐  │
│  │                    4. AI/ML LAYER                                          │  │
│  │                                   ▼                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │              LLM INFERENCE (Claude / GPT-4 / Fine-tuned Model)       │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │  │  │
│  │  │  │ Query Gen   │  │ Investigation│  │ Narrative Generation       │  │  │  │
│  │  │  │ Agent       │  │ Agent        │  │ Agent                       │  │  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────┼───────────────────────────────────────┘  │
│                                      │                                          │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐  │
│  │                    5. APPLICATION LAYER                                    │  │
│  │                                   ▼                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │              CR360 APPLICATION (Next.js / React)                     │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │  │  │
│  │  │  │ Chat UI     │  │ Dashboard   │  │ Visualization Canvas        │  │  │  │
│  │  │  │             │  │ Builder     │  │                              │  │  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 12.2 Query Execution Flow

```
User Message                 Processing Steps                    Response
──────────────────────────────────────────────────────────────────────────────

"How are originations      ┌────────────────────────┐
 looking in various        │ 1. Intent Classification│
 regions?"                 │    → QUERY intent       │
                          └───────────┬────────────┘
                                      │
                          ┌───────────▼────────────┐
                          │ 2. Entity Extraction    │
                          │    → metric: originations│
                          │    → dim: region        │
                          │    → time: current      │
                          └───────────┬────────────┘
                                      │
                          ┌───────────▼────────────┐
                          │ 3. Load Context        │
                          │    → Full metric defs   │
                          │    → Schema (from YAML) │
                          │    → Business rules     │
                          └───────────┬────────────┘
                                      │
                          ┌───────────▼────────────┐
                          │ 4. SQL Generation      │
                          │    → SELECT region,    │
                          │      SUM(orig_amt)...  │
                          └───────────┬────────────┘
                                      │
                          ┌───────────▼────────────┐
                          │ 5. Query Execution     │
                          │    → Execute via       │
                          │      Semantic Layer    │
                          └───────────┬────────────┘
                                      │
                          ┌───────────▼────────────┐     "Here are originations
                          │ 6. Visualization       │      by region:
                          │    → Profile data      │
                          │    → Select: Bar Chart │      [Bar Chart]
                          └───────────┬────────────┘
                                      │               South: $2.4B ████████
                          ┌───────────▼────────────┐   North: $1.8B ██████
                          │ 7. Narrative Generation│   East:  $1.6B █████
                          │    → Key insights      │   West:  $1.5B █████
                          │    → Suggested drilldowns│  Central:$1.2B ████
                          └────────────────────────┘
                                                      South leads with 28% of
                                                      total originations..."
```

---

## 10. Security & Governance

### 12.1 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              AUTHENTICATION                                 │ │
│  │  • SSO Integration (SAML 2.0 / OIDC)                       │ │
│  │  • Multi-Factor Authentication                              │ │
│  │  • Session Management                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              AUTHORIZATION (RBAC + ABAC)                    │ │
│  │                                                             │ │
│  │  Roles:                                                     │ │
│  │  • CCO: Full portfolio access                              │ │
│  │  • Regional Manager: Region-scoped access                  │ │
│  │  • Product Manager: Product-scoped access                  │ │
│  │  • Analyst: Read-only, assigned segments                   │ │
│  │                                                             │ │
│  │  Attributes:                                                │ │
│  │  • Region assignment                                        │ │
│  │  • Product assignment                                       │ │
│  │  • Sensitivity clearance level                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              DATA-LEVEL SECURITY                            │ │
│  │                                                             │ │
│  │  Row-Level Security (RLS):                                  │ │
│  │  • Applied at Semantic Layer                               │ │
│  │  • Based on user attributes                                │ │
│  │                                                             │ │
│  │  Column-Level Security (CLS):                              │ │
│  │  • Mask sensitive fields (SSN, Account #)                  │ │
│  │  • Aggregate-only access for PII                           │ │
│  │                                                             │ │
│  │  Query Injection Prevention:                                │ │
│  │  • Parameterized queries only                              │ │
│  │  • SQL validation before execution                         │ │
│  │  • LLM output sanitization                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              AUDIT & COMPLIANCE                             │ │
│  │                                                             │ │
│  │  • Full query logging                                       │ │
│  │  • User action audit trail                                 │ │
│  │  • LLM prompt/response logging (anonymized)                │ │
│  │  • Data lineage tracking                                   │ │
│  │  • Compliance reports (SOX, Basel III, GDPR)               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 AI Governance

```yaml
ai_governance:
  
  prompt_safety:
    - Sanitize user inputs before LLM processing
    - Block prompt injection attempts
    - Validate LLM outputs against schema
    
  hallucination_prevention:
    - Ground all responses in actual data
    - Require citations for all facts
    - Flag low-confidence responses
    - Human review for anomalous outputs
    
  explainability:
    - Log all queries generated
    - Show "how we got this answer" on request
    - Maintain investigation audit trail
    
  model_governance:
    - Version control for prompts
    - A/B testing for prompt improvements
    - Performance monitoring (accuracy, latency)
    - Fallback to simpler models on failure
```

---

## 11. Technology Stack

### 11.1 Recommended Stack

| Layer | Component | Recommended Technologies |
|-------|-----------|-------------------------|
| **Frontend** | Chat UI | React, Next.js 14, TailwindCSS |
| | Visualization | D3.js, Recharts, Plotly, Apache ECharts |
| | State Management | Zustand, React Query |
| **Backend** | API Gateway | FastAPI (Python) / Node.js |
| | Orchestration | LangChain / LangGraph (optional) |
| | Caching | Redis |
| | Task Queue | Celery / Bull |
| **AI/ML** | LLM | Google Gemini 2.5 Flash (recommended for prototype) |
| **Context** | Metric Definitions | YAML/JSON config file |
| | Schema Docs | YAML/JSON config file |
| **Data** | Warehouse | Snowflake / Databricks / BigQuery / Oracle |
| | ETL | dbt, Airflow |
| **Infrastructure** | Cloud | AWS / Azure / GCP |
| | Containers | Kubernetes, Docker |
| | Observability | Datadog / New Relic |

### 11.2 Gemini API Integration

#### Setup and Installation

```bash
# Install the Google Generative AI SDK
pip install google-generativeai

# Set your API key (get from https://aistudio.google.com/apikey)
export GOOGLE_API_KEY="your-api-key-here"
```

#### Core LLM Client for CR360

```python
"""
cr360/llm/gemini_client.py

Gemini API client for CR360 Text-to-SQL generation.
Optimized for credit risk analytics queries.
"""

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os
import yaml
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structured response from LLM"""
    sql: str
    explanation: str
    confidence: float
    tokens_used: Dict[str, int]
    latency_ms: float
    cost_usd: float


class GeminiClient:
    """
    Gemini API client optimized for CR360 Text-to-SQL.
    
    Uses Gemini 2.5 Flash for cost-effective SQL generation.
    Supports automatic retry, token tracking, and cost estimation.
    """
    
    # Pricing as of Dec 2025 (per 1M tokens)
    PRICING = {
        "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    }
    
    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash",
        context_file: str = "credit_risk_context.yaml"
    ):
        # Configure API
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Load credit risk context
        self.context = self._load_context(context_file)
        
        # Build system prompt
        self.system_prompt = self._build_system_prompt()
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        logger.info(f"GeminiClient initialized with {model_name}")
        logger.info(f"Context loaded: {len(self.context.get('metrics', {}))} metrics")
    
    def _load_context(self, context_file: str) -> dict:
        """Load credit risk context from YAML file"""
        try:
            with open(context_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Context file {context_file} not found, using empty context")
            return {}
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with full credit risk context"""
        
        # Extract metric definitions
        metrics_section = ""
        if 'metrics' in self.context:
            metrics_section = "## AVAILABLE METRICS\n\n"
            for metric_name, metric_def in self.context['metrics'].items():
                metrics_section += f"- **{metric_name}**: {metric_def.get('description', '')}\n"
                metrics_section += f"  - Column: {metric_def.get('column', 'N/A')}\n"
                metrics_section += f"  - Formula: {metric_def.get('formula', 'N/A')}\n\n"
        
        # Extract table schemas
        tables_section = ""
        if 'tables' in self.context:
            tables_section = "## DATABASE SCHEMA\n\n"
            for table_name, table_def in self.context['tables'].items():
                tables_section += f"### {table_name}\n"
                tables_section += f"{table_def.get('description', '')}\n"
                tables_section += "Columns:\n"
                for col in table_def.get('columns', []):
                    tables_section += f"  - {col}\n"
                tables_section += "\n"
        
        # Extract dimensions
        dimensions_section = ""
        if 'dimensions' in self.context:
            dimensions_section = "## DIMENSIONS & HIERARCHIES\n\n"
            for dim_name, dim_def in self.context['dimensions'].items():
                dimensions_section += f"- **{dim_name}**: {dim_def.get('values', [])}\n"
        
        system_prompt = f"""You are a Credit Risk SQL Expert for the CR360 analytics platform.

Your job is to convert natural language questions about credit risk into accurate SQL queries.

{metrics_section}

{tables_section}

{dimensions_section}

## RULES
1. Only use tables and columns defined in the schema above
2. Always use table aliases (e.g., f for fact tables, d for dimensions)
3. Default time period is current quarter unless specified
4. Use SUM/AVG/COUNT appropriately based on metric type
5. Include ORDER BY for ranked results
6. Limit results to 1000 rows max

## OUTPUT FORMAT
Return your response in this exact format:

```sql
<your SQL query here>
```

**Explanation:** <one sentence explaining what the query does>

**Confidence:** <HIGH|MEDIUM|LOW>
"""
        return system_prompt
    
    async def generate_sql(
        self, 
        question: str,
        conversation_history: Optional[list] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        """
        Generate SQL from natural language question.
        
        Args:
            question: User's natural language question
            conversation_history: Optional list of previous messages for context
            temperature: LLM temperature (lower = more deterministic)
        
        Returns:
            LLMResponse with SQL, explanation, and metadata
        """
        start_time = time.time()
        
        # Build the full prompt
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                messages.append(msg)
        
        # Add current question
        user_message = f"""Question: {question}

Generate a SQL query to answer this question. Follow the rules and output format specified."""
        
        try:
            # Call Gemini API
            response = self.model.generate_content(
                contents=[
                    {"role": "user", "parts": [{"text": self.system_prompt}]},
                    {"role": "model", "parts": [{"text": "I understand. I'm ready to generate SQL queries for credit risk analytics. Please ask your question."}]},
                    {"role": "user", "parts": [{"text": user_message}]}
                ],
                generation_config=GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Parse response
            response_text = response.text
            sql, explanation, confidence = self._parse_response(response_text)
            
            # Track tokens (estimate if not provided)
            input_tokens = self._estimate_tokens(self.system_prompt + user_message)
            output_tokens = self._estimate_tokens(response_text)
            
            # Calculate cost
            pricing = self.PRICING.get(self.model_name, self.PRICING["gemini-2.5-flash"])
            cost = (input_tokens * pricing["input"] / 1_000_000) + \
                   (output_tokens * pricing["output"] / 1_000_000)
            
            # Update totals
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost
            
            logger.info(f"Query generated in {latency_ms:.0f}ms, cost: ${cost:.4f}")
            
            return LLMResponse(
                sql=sql,
                explanation=explanation,
                confidence=confidence,
                tokens_used={"input": input_tokens, "output": output_tokens},
                latency_ms=latency_ms,
                cost_usd=cost
            )
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise
    
    def _parse_response(self, response_text: str) -> tuple:
        """Parse LLM response to extract SQL, explanation, and confidence"""
        import re
        
        # Extract SQL from code block
        sql_match = re.search(r'```sql\s*(.*?)\s*```', response_text, re.DOTALL)
        sql = sql_match.group(1).strip() if sql_match else ""
        
        # Extract explanation
        explanation_match = re.search(r'\*\*Explanation:\*\*\s*(.*?)(?:\n|$)', response_text)
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        # Extract confidence
        confidence_match = re.search(r'\*\*Confidence:\*\*\s*(HIGH|MEDIUM|LOW)', response_text, re.IGNORECASE)
        confidence_str = confidence_match.group(1).upper() if confidence_match else "MEDIUM"
        confidence = {"HIGH": 0.9, "MEDIUM": 0.7, "LOW": 0.5}.get(confidence_str, 0.7)
        
        return sql, explanation, confidence
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 4 chars = 1 token)"""
        return len(text) // 4
    
    def get_usage_stats(self) -> dict:
        """Get cumulative usage statistics"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "model": self.model_name
        }
    
    def reset_usage_stats(self):
        """Reset usage tracking (e.g., at start of new session)"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0


# Synchronous wrapper for non-async code
class GeminiClientSync(GeminiClient):
    """Synchronous version of GeminiClient"""
    
    def generate_sql(
        self, 
        question: str,
        conversation_history: Optional[list] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        """Synchronous SQL generation"""
        import asyncio
        return asyncio.run(super().generate_sql(question, conversation_history, temperature))
```

#### Example Usage

```python
# Quick start example
from cr360.llm.gemini_client import GeminiClientSync

# Initialize client
client = GeminiClientSync(
    model_name="gemini-2.5-flash",
    context_file="credit_risk_context.yaml"
)

# Generate SQL
response = client.generate_sql(
    "What are the originations by region for Q4 2025?"
)

print(f"SQL: {response.sql}")
print(f"Explanation: {response.explanation}")
print(f"Confidence: {response.confidence}")
print(f"Cost: ${response.cost_usd:.4f}")
print(f"Latency: {response.latency_ms:.0f}ms")

# Check usage
print(client.get_usage_stats())
```

#### Integration with SQL Validator

```python
"""
cr360/query_engine.py

Complete query engine integrating Gemini + SQL Validation + Smart Retry
"""

from cr360.llm.gemini_client import GeminiClient, LLMResponse
from cr360.validators.sql_validator import SQLValidator
from cr360.handlers.ambiguity import AmbiguityDetector
from dataclasses import dataclass
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    success: bool
    sql: Optional[str]
    data: Optional[list]
    explanation: str
    confidence: float
    attempts: int
    cost_usd: float
    needs_clarification: bool = False
    clarification_options: Optional[list] = None


class CR360QueryEngine:
    """
    Main query engine for CR360.
    
    Integrates:
    - Gemini LLM for SQL generation
    - SQL validation before execution
    - Ambiguity detection and clarification
    - Smart retry on failure
    """
    
    def __init__(
        self,
        gemini_client: GeminiClient,
        sql_validator: SQLValidator,
        db_client,  # Your database client
        ambiguity_detector: Optional[AmbiguityDetector] = None
    ):
        self.llm = gemini_client
        self.validator = sql_validator
        self.db = db_client
        self.ambiguity_detector = ambiguity_detector or AmbiguityDetector()
    
    async def process_question(
        self, 
        question: str,
        skip_clarification: bool = False
    ) -> QueryResult:
        """
        Process a natural language question end-to-end.
        
        Steps:
        1. Check for ambiguity (unless skipped)
        2. Generate SQL via Gemini
        3. Validate SQL against schema
        4. Execute query
        5. Return results with metadata
        """
        total_cost = 0.0
        
        # Step 1: Check for ambiguity
        if not skip_clarification:
            clarification = self.ambiguity_detector.detect_ambiguity(question)
            if clarification:
                return QueryResult(
                    success=False,
                    sql=None,
                    data=None,
                    explanation=clarification.message,
                    confidence=0.0,
                    attempts=0,
                    cost_usd=0.0,
                    needs_clarification=True,
                    clarification_options=clarification.ambiguities
                )
        
        # Step 2-4: Generate, Validate, Execute with retry
        max_attempts = 3
        attempt_errors = []
        
        for attempt in range(max_attempts):
            try:
                # Generate SQL
                if attempt == 0:
                    prompt = question
                else:
                    # Include error context for retry
                    prompt = f"""Previous attempt failed with error: {attempt_errors[-1]}

Original question: {question}

Please fix the SQL query. Use only valid table and column names from the schema."""
                
                llm_response = await self.llm.generate_sql(prompt)
                total_cost += llm_response.cost_usd
                
                # Validate SQL
                validation = self.validator.validate(llm_response.sql)
                
                if not validation.valid:
                    error_msg = "; ".join(validation.errors)
                    attempt_errors.append(f"Validation failed: {error_msg}")
                    logger.warning(f"Attempt {attempt + 1}: SQL validation failed - {error_msg}")
                    continue
                
                # Execute SQL
                try:
                    result = await self.db.execute(llm_response.sql)
                    
                    return QueryResult(
                        success=True,
                        sql=llm_response.sql,
                        data=result,
                        explanation=llm_response.explanation,
                        confidence=llm_response.confidence,
                        attempts=attempt + 1,
                        cost_usd=total_cost
                    )
                    
                except Exception as db_error:
                    attempt_errors.append(f"Execution failed: {str(db_error)}")
                    logger.warning(f"Attempt {attempt + 1}: SQL execution failed - {db_error}")
                    continue
                    
            except Exception as e:
                attempt_errors.append(f"Generation failed: {str(e)}")
                logger.error(f"Attempt {attempt + 1}: LLM error - {e}")
                continue
        
        # All attempts failed
        return QueryResult(
            success=False,
            sql=None,
            data=None,
            explanation=f"Failed after {max_attempts} attempts. Errors: {attempt_errors}",
            confidence=0.0,
            attempts=max_attempts,
            cost_usd=total_cost
        )
```

#### Cost Tracking Dashboard

```python
"""
cr360/monitoring/cost_tracker.py

Track and report Gemini API costs
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List
import json


@dataclass
class QueryLog:
    timestamp: datetime
    question: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    success: bool
    latency_ms: float


@dataclass 
class CostTracker:
    """Track API costs for budget management"""
    
    budget_usd: float = 300.0  # Your $300 credit
    queries: List[QueryLog] = field(default_factory=list)
    
    def log_query(self, log: QueryLog):
        """Log a query for cost tracking"""
        self.queries.append(log)
    
    @property
    def total_spent(self) -> float:
        """Total amount spent"""
        return sum(q.cost_usd for q in self.queries)
    
    @property
    def remaining_budget(self) -> float:
        """Remaining budget"""
        return self.budget_usd - self.total_spent
    
    @property
    def queries_remaining_estimate(self) -> int:
        """Estimated queries remaining based on average cost"""
        if not self.queries:
            return int(self.budget_usd / 0.004)  # Default estimate
        avg_cost = self.total_spent / len(self.queries)
        return int(self.remaining_budget / avg_cost) if avg_cost > 0 else 0
    
    def get_daily_summary(self, date: datetime = None) -> dict:
        """Get summary for a specific date"""
        date = date or datetime.now()
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        day_queries = [q for q in self.queries if start <= q.timestamp < end]
        
        return {
            "date": start.strftime("%Y-%m-%d"),
            "query_count": len(day_queries),
            "total_cost": sum(q.cost_usd for q in day_queries),
            "avg_latency_ms": sum(q.latency_ms for q in day_queries) / len(day_queries) if day_queries else 0,
            "success_rate": sum(1 for q in day_queries if q.success) / len(day_queries) if day_queries else 0
        }
    
    def print_status(self):
        """Print current budget status"""
        print(f"""
╔══════════════════════════════════════════════════════╗
║              CR360 COST TRACKING                     ║
╠══════════════════════════════════════════════════════╣
║  Budget:              ${self.budget_usd:>8.2f}                  ║
║  Spent:               ${self.total_spent:>8.4f}                  ║
║  Remaining:           ${self.remaining_budget:>8.2f}                  ║
║  Queries Executed:    {len(self.queries):>8}                    ║
║  Est. Queries Left:   {self.queries_remaining_estimate:>8,}                    ║
╚══════════════════════════════════════════════════════╝
        """)
```

### 11.3 Conversation Memory for Follow-up Questions

CR360 needs to handle multi-turn conversations where users ask follow-up questions:

```
User: "Show originations by region"
Bot:  [Returns data - South: $2.4B, North: $1.8B, ...]

User: "Why is South so high?"           ← Needs context: "South" = region, "high" = originations
Bot:  [Investigates South region]

User: "Compare to last quarter"         ← Needs context: South + originations + current quarter
Bot:  [Compares Q4 vs Q3 for South originations]
```

#### Memory Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONVERSATION MEMORY                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  SLIDING WINDOW (Last 5 turns)                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ User: "Show originations by region"                  │  │ │
│  │  │ Bot:  "South: $2.4B, North: $1.8B..." [SQL: ...]     │  │ │
│  │  │ User: "Why is South so high?"                        │  │ │
│  │  │ Bot:  "Looking at credit quality factors..." [SQL]   │  │ │
│  │  │ User: "Compare to last quarter"                      │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              +                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  ACTIVE CONTEXT (Extracted entities)                       │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ • region_focus: "South"                              │  │ │
│  │  │ • metric_focus: "originations"                       │  │ │
│  │  │ • time_period: "Q4-2025"                             │  │ │
│  │  │ • product_filter: null (all products)                │  │ │
│  │  │ • comparison_mode: "quarter-over-quarter"            │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              +                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAST QUERY CONTEXT                                        │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ • last_sql: "SELECT region, SUM(...)..."             │  │ │
│  │  │ • last_result_summary: "4 regions, South highest"    │  │ │
│  │  │ • last_metric: "origination_volume"                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### Conversation Memory Implementation

```python
"""
cr360/memory/conversation_memory.py

Conversation memory for multi-turn credit risk Q&A.
Combines sliding window + extracted context for efficient follow-ups.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import re


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Single conversation message"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sql: Optional[str] = None
    result_summary: Optional[str] = None


@dataclass
class ActiveContext:
    """
    Extracted entities from conversation.
    These are the "remembered" filters and focus areas.
    """
    region_focus: Optional[str] = None          # e.g., "South"
    product_focus: Optional[str] = None         # e.g., "Auto", "Mortgage"
    segment_focus: Optional[str] = None         # e.g., "Subprime", "Prime"
    metric_focus: Optional[str] = None          # e.g., "originations", "delinquency"
    time_period: Optional[str] = None           # e.g., "Q4-2025"
    comparison_period: Optional[str] = None     # e.g., "Q3-2025"
    comparison_mode: Optional[str] = None       # e.g., "quarter-over-quarter", "year-over-year"
    
    def to_prompt_context(self) -> str:
        """Convert active context to prompt-friendly format"""
        parts = []
        
        if self.region_focus:
            parts.append(f"Region focus: {self.region_focus}")
        if self.product_focus:
            parts.append(f"Product focus: {self.product_focus}")
        if self.segment_focus:
            parts.append(f"Segment focus: {self.segment_focus}")
        if self.metric_focus:
            parts.append(f"Metric focus: {self.metric_focus}")
        if self.time_period:
            parts.append(f"Time period: {self.time_period}")
        if self.comparison_period:
            parts.append(f"Comparing to: {self.comparison_period}")
        
        if parts:
            return "Current conversation context:\n" + "\n".join(f"  • {p}" for p in parts)
        return ""
    
    def clear(self):
        """Reset all context"""
        self.region_focus = None
        self.product_focus = None
        self.segment_focus = None
        self.metric_focus = None
        self.time_period = None
        self.comparison_period = None
        self.comparison_mode = None


class ConversationMemory:
    """
    Manages conversation memory for CR360.
    
    Features:
    - Sliding window of recent messages
    - Extracted active context (entities)
    - Last query tracking for continuity
    - Automatic context extraction from questions
    """
    
    # Entity extraction patterns
    REGION_PATTERNS = [
        r'\b(South|North|East|West|Central)\b',
        r'\b(south|north|east|west|central)\s+region\b'
    ]
    
    PRODUCT_PATTERNS = [
        r'\b(Auto|Mortgage|Credit\s*Card|Personal|Commercial|HELOC)\b',
    ]
    
    SEGMENT_PATTERNS = [
        r'\b(Subprime|Prime|Near-?prime|Super-?prime)\b',
    ]
    
    METRIC_PATTERNS = {
        "originations": [r'\b(origination|originations|new\s+loans?)\b'],
        "delinquency": [r'\b(delinquen|dpd|past\s+due|30\+|60\+|90\+)\b'],
        "exposure": [r'\b(exposure|ead|credit\s+exposure)\b'],
        "nco": [r'\b(charge.?off|nco|write.?off|loss)\b'],
        "balance": [r'\b(balance|outstanding)\b'],
    }
    
    TIME_PATTERNS = [
        (r'\b(Q[1-4])[\s-]*(\d{4})\b', r'\1-\2'),          # Q4 2025 → Q4-2025
        (r'\b(Q[1-4])\b', None),                            # Q4 (infer year)
        (r'\b(this|current)\s+(quarter|month|year)\b', None),
        (r'\b(last|previous)\s+(quarter|month|year)\b', None),
    ]
    
    def __init__(self, max_turns: int = 5):
        """
        Initialize conversation memory.
        
        Args:
            max_turns: Maximum number of turn pairs to keep in sliding window
        """
        self.max_turns = max_turns
        self.messages: List[Message] = []
        self.active_context = ActiveContext()
        self.last_sql: Optional[str] = None
        self.last_result_summary: Optional[str] = None
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_user_message(self, content: str):
        """Add user message and extract context"""
        message = Message(role=MessageRole.USER, content=content)
        self.messages.append(message)
        
        # Extract entities from the message
        self._extract_context(content)
        
        # Trim to max window
        self._trim_window()
    
    def add_assistant_message(
        self, 
        content: str, 
        sql: Optional[str] = None,
        result_summary: Optional[str] = None
    ):
        """Add assistant response with optional SQL and result summary"""
        message = Message(
            role=MessageRole.ASSISTANT, 
            content=content,
            sql=sql,
            result_summary=result_summary
        )
        self.messages.append(message)
        
        # Track last query
        if sql:
            self.last_sql = sql
        if result_summary:
            self.last_result_summary = result_summary
        
        self._trim_window()
    
    def _extract_context(self, text: str):
        """Extract entities from user message to update active context"""
        text_lower = text.lower()
        
        # Extract region
        for pattern in self.REGION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.active_context.region_focus = match.group(1).title()
                break
        
        # Extract product
        for pattern in self.PRODUCT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.active_context.product_focus = match.group(1).title()
                break
        
        # Extract segment
        for pattern in self.SEGMENT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.active_context.segment_focus = match.group(1).title()
                break
        
        # Extract metric focus
        for metric_name, patterns in self.METRIC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    self.active_context.metric_focus = metric_name
                    break
        
        # Extract time period
        for pattern, replacement in self.TIME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if "last" in text_lower or "previous" in text_lower:
                    self.active_context.comparison_period = match.group(0)
                    self.active_context.comparison_mode = "period-over-period"
                else:
                    self.active_context.time_period = match.group(0)
                break
    
    def _trim_window(self):
        """Keep only the last N turns (user + assistant pairs)"""
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
    
    def get_context_for_prompt(self) -> str:
        """
        Build context string to inject into LLM prompt.
        
        Returns formatted context with:
        - Recent conversation history
        - Active context (extracted entities)
        - Last query info
        """
        parts = []
        
        # Part 1: Active context (extracted entities)
        active_ctx = self.active_context.to_prompt_context()
        if active_ctx:
            parts.append(active_ctx)
        
        # Part 2: Last query context
        if self.last_sql and self.last_result_summary:
            parts.append(f"""Last query context:
  • SQL: {self.last_sql[:200]}{'...' if len(self.last_sql) > 200 else ''}
  • Result: {self.last_result_summary}""")
        
        # Part 3: Recent conversation (last 3 turns for prompt)
        recent_messages = self.messages[-6:]  # Last 3 turns
        if recent_messages:
            conv_lines = ["Recent conversation:"]
            for msg in recent_messages:
                role = "User" if msg.role == MessageRole.USER else "Assistant"
                # Truncate long messages
                content = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                conv_lines.append(f"  {role}: {content}")
            parts.append("\n".join(conv_lines))
        
        if parts:
            return "\n\n".join(parts)
        return ""
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """
        Get messages formatted for Gemini API.
        
        Returns list of {"role": "user"|"model", "parts": [{"text": "..."}]}
        """
        api_messages = []
        for msg in self.messages:
            role = "user" if msg.role == MessageRole.USER else "model"
            api_messages.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        return api_messages
    
    def clear(self):
        """Clear all memory (start fresh conversation)"""
        self.messages = []
        self.active_context.clear()
        self.last_sql = None
        self.last_result_summary = None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get memory summary for debugging"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "active_context": {
                "region": self.active_context.region_focus,
                "product": self.active_context.product_focus,
                "metric": self.active_context.metric_focus,
                "time_period": self.active_context.time_period,
            },
            "has_last_query": self.last_sql is not None
        }
```

#### Updated Gemini Client with Memory

```python
"""
cr360/llm/gemini_client_with_memory.py

Gemini client with conversation memory integration.
"""

from cr360.llm.gemini_client import GeminiClient, LLMResponse
from cr360.memory.conversation_memory import ConversationMemory
from typing import Optional


class GeminiClientWithMemory(GeminiClient):
    """
    Gemini client that maintains conversation memory
    for multi-turn credit risk Q&A.
    """
    
    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash",
        context_file: str = "credit_risk_context.yaml",
        max_memory_turns: int = 5
    ):
        super().__init__(model_name, context_file)
        self.memory = ConversationMemory(max_turns=max_memory_turns)
    
    async def generate_sql_with_memory(
        self, 
        question: str,
        temperature: float = 0.1
    ) -> LLMResponse:
        """
        Generate SQL with conversation memory context.
        
        This method:
        1. Adds user question to memory
        2. Extracts context from question
        3. Builds prompt with conversation context
        4. Generates SQL
        5. Stores response in memory
        """
        # Add to memory (this also extracts context)
        self.memory.add_user_message(question)
        
        # Build enhanced prompt with memory context
        memory_context = self.memory.get_context_for_prompt()
        
        enhanced_question = question
        if memory_context:
            enhanced_question = f"""{memory_context}

---
Current question: {question}

Use the conversation context above to understand references like "it", "that region", "compare to last quarter", etc."""
        
        # Generate SQL using parent method
        response = await self.generate_sql(enhanced_question, temperature=temperature)
        
        # Store response in memory
        result_summary = self._generate_result_summary(response)
        self.memory.add_assistant_message(
            content=response.explanation,
            sql=response.sql,
            result_summary=result_summary
        )
        
        return response
    
    def _generate_result_summary(self, response: LLMResponse) -> str:
        """Generate a brief summary of the response for memory"""
        # In production, this would summarize actual query results
        # For now, use the explanation
        return response.explanation[:100] if response.explanation else "Query generated"
    
    def clear_memory(self):
        """Clear conversation memory (start new session)"""
        self.memory.clear()
    
    def get_memory_summary(self) -> dict:
        """Get memory state for debugging"""
        return self.memory.get_summary()
```

#### Example: Multi-turn Conversation

```python
"""
Example: Multi-turn conversation with memory
"""

import asyncio
from cr360.llm.gemini_client_with_memory import GeminiClientWithMemory


async def demo_conversation():
    # Initialize client with memory
    client = GeminiClientWithMemory(
        model_name="gemini-2.5-flash",
        context_file="credit_risk_context.yaml",
        max_memory_turns=5
    )
    
    # Conversation flow
    questions = [
        "Show me originations by region for Q4 2025",
        "Why is South so high?",                        # References "South" from results
        "Compare it to last quarter",                   # "it" = South originations
        "What about the credit quality there?",         # "there" = South
        "Show me the trend over the past 4 quarters",   # Still about South + credit quality
    ]
    
    print("=" * 60)
    print("CR360 Multi-turn Conversation Demo")
    print("=" * 60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Turn {i}] User: {question}")
        
        response = await client.generate_sql_with_memory(question)
        
        print(f"[Turn {i}] SQL: {response.sql[:100]}...")
        print(f"[Turn {i}] Explanation: {response.explanation}")
        print(f"[Turn {i}] Confidence: {response.confidence}")
        print(f"[Turn {i}] Cost: ${response.cost_usd:.4f}")
        
        # Show memory state
        memory_state = client.get_memory_summary()
        print(f"[Memory] Active context: {memory_state['active_context']}")
    
    # Final stats
    print("\n" + "=" * 60)
    print("Session Summary")
    print("=" * 60)
    usage = client.get_usage_stats()
    print(f"Total queries: {len(questions)}")
    print(f"Total tokens: {usage['total_input_tokens'] + usage['total_output_tokens']:,}")
    print(f"Total cost: ${usage['total_cost_usd']:.4f}")


# Run the demo
# asyncio.run(demo_conversation())
```

#### How Memory Affects the Prompt

```
┌─────────────────────────────────────────────────────────────────┐
│  WITHOUT MEMORY                                                  │
│                                                                  │
│  User: "Compare it to last quarter"                             │
│                                                                  │
│  LLM sees: "Compare it to last quarter"                         │
│  LLM thinks: Compare WHAT? Which metric? Which region?          │
│  Result: ❌ Ambiguous, likely wrong SQL                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  WITH MEMORY                                                     │
│                                                                  │
│  User: "Compare it to last quarter"                             │
│                                                                  │
│  LLM sees:                                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Current conversation context:                              │ │
│  │   • Region focus: South                                    │ │
│  │   • Metric focus: originations                             │ │
│  │   • Time period: Q4-2025                                   │ │
│  │                                                             │ │
│  │ Last query context:                                         │ │
│  │   • SQL: SELECT region, SUM(origination_volume)...         │ │
│  │   • Result: South region had highest originations          │ │
│  │                                                             │ │
│  │ Recent conversation:                                        │ │
│  │   User: Show me originations by region for Q4 2025         │ │
│  │   Assistant: South: $2.4B, North: $1.8B...                 │ │
│  │   User: Why is South so high?                              │ │
│  │   Assistant: Looking at credit factors in South...         │ │
│  │                                                             │ │
│  │ Current question: Compare it to last quarter               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  LLM understands: Compare South originations Q4 vs Q3          │
│  Result: ✅ Correct SQL with proper context                     │
└─────────────────────────────────────────────────────────────────┘
```

### 11.4 Architecture Decision Records (ADRs)

**ADR-001: LLM Selection — Google Gemini 2.5 Flash**
- Decision: Use **Google Gemini 2.5 Flash** as primary LLM for prototype
- Rationale: 
  - Excellent SQL generation (strong performance on BirdSQL benchmark)
  - 1M token context window (our 25K context fits easily)
  - Cost-effective: ~$0.004 per query
  - Fast response times (~163 tokens/sec)
  - $300 free credits = ~75,000 queries for prototyping
- Pricing (as of Dec 2025):
  - Input: $0.15 per 1M tokens
  - Output: $0.60 per 1M tokens
- Alternative: Gemini 2.5 Pro for complex investigation queries ($1.25/$10.00 per 1M tokens — use sparingly)
- Trade-offs: Slightly less capable than Claude/GPT-4 on complex reasoning, but excellent for Text-to-SQL

**ADR-002: Full-Context vs RAG**
- Decision: Use full-context prompting (load all metrics/schema into system prompt)
- Rationale: Credit risk context (~25K tokens) fits easily in Gemini's 1M context window. Eliminates retrieval complexity, reduces latency, simpler architecture
- Trade-offs: If context grows beyond 100K tokens, may need to revisit

**ADR-003: Context Storage**
- Decision: Use YAML/JSON files for metric definitions and schema
- Rationale: Simple, version-controllable, no additional infrastructure. Can be loaded at application startup
- Trade-offs: Manual updates required when schema changes

**ADR-004: Conversation Memory — Hybrid Approach**
- Decision: Use sliding window (5 turns) + extracted entities for conversation memory
- Rationale:
  - Sliding window provides natural conversation flow
  - Entity extraction (region, metric, time) ensures critical context isn't lost
  - Last SQL + result summary enables "compare to..." and "what about..." follow-ups
  - Adds only ~2-3K tokens per query (cost-effective)
- Alternatives rejected:
  - Full history → Too expensive, excessive tokens
  - LangChain memory → Adds framework dependency, overkill
  - LLM-based summarization → Adds latency and cost
- Trade-offs: Regex-based extraction may miss edge cases; can enhance later

---

## 12. Implementation Roadmap

### 12.1 Phase 1: Foundation (Months 1-3)

**Deliverables:**
- [ ] Context file setup with core metrics (top 50)
- [ ] Basic Text-to-SQL with simple queries
- [ ] Chat UI with single-turn Q&A
- [ ] Bar, Line, Table visualizations
- [ ] Authentication integration

**Success Criteria:**
- 80% accuracy on simple factual queries
- < 3 second response time for cached queries
- 10 pilot users onboarded

### 12.2 Phase 2: Progressive Intelligence (Months 4-6)

**Deliverables:**
- [ ] Multi-turn conversation support
- [ ] Investigation Agent with hypothesis generation
- [ ] Expanded metric coverage (200+ metrics)
- [ ] Automatic chart selection
- [ ] Narrative generation

**Success Criteria:**
- Support for 3+ turn investigations
- 75% accuracy on complex analytical queries
- 50 users onboarded

### 12.3 Phase 3: Advanced Analytics (Months 7-9)

**Deliverables:**
- [ ] Full investigation templates
- [ ] Anomaly detection alerts
- [ ] Comparative analysis (peer benchmarking)
- [ ] Custom dashboard generation
- [ ] Mobile support

**Success Criteria:**
- 90% user satisfaction score
- 50% reduction in ad-hoc reporting requests
- 200+ users onboarded

### 12.4 Phase 4: Autonomous Intelligence (Months 10-12)

**Deliverables:**
- [ ] Proactive insights ("You should know...")
- [ ] Automated monitoring agents
- [ ] Natural language report generation
- [ ] Self-improving query accuracy
- [ ] Full audit/compliance integration

**Success Criteria:**
- Proactive alerts with 80%+ relevance
- 95%+ query accuracy
- Full regulatory compliance

---

## Appendix A: Sample Conversation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ CCO Dashboard - AI Chat                                    [x] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ User: How are originations looking in various regions?          │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ CR360: Here are Q4 2025 originations by region:             │ │
│ │                                                             │ │
│ │ [Bar Chart: Origination Volume by Region]                   │ │
│ │                                                             │ │
│ │ South   ████████████████████ $2.4B (28%)                   │ │
│ │ North   ███████████████ $1.8B (21%)                        │ │
│ │ East    █████████████ $1.6B (19%)                          │ │
│ │ West    ████████████ $1.5B (18%)                           │ │
│ │ Central █████████ $1.2B (14%)                              │ │
│ │                                                             │ │
│ │ Key Insight: South leads significantly at 28% of total     │ │
│ │ originations, up from 22% last quarter.                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ User: Originations in South are too high compared to others.    │
│       Figure out whether credit quality is eroding in South.    │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ CR360: I'll analyze credit quality indicators for the      │ │
│ │ South region compared to others. Let me check several      │ │
│ │ metrics...                                                  │ │
│ │                                                             │ │
│ │ [Multi-line Chart: Credit Score Trend by Region]           │ │
│ │ [Bar Chart: Subprime Mix by Region]                        │ │
│ │ [Table: Credit Quality Comparison]                          │ │
│ │                                                             │ │
│ │ ⚠️ Findings: Credit quality IS deteriorating in South:     │ │
│ │                                                             │ │
│ │ 1. Average credit score dropped 25 pts (720→695)           │ │
│ │    while other regions remained stable                      │ │
│ │                                                             │ │
│ │ 2. Subprime mix nearly doubled (15%→28%)                   │ │
│ │                                                             │ │
│ │ 3. Average LTV increased 7 pts (78%→85%)                   │ │
│ │                                                             │ │
│ │ 4. Approval rate is 72% vs 65% industry average            │ │
│ │                                                             │ │
│ │ Would you like me to:                                       │ │
│ │ • Drill down by product type in South?                     │ │
│ │ • Identify specific branches driving this?                 │ │
│ │ • Compare to historical vintages?                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ User: Yes, drill down by product in South                       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ CR360: Here's the product-level breakdown for South:        │ │
│ │                                                             │ │
│ │ [Stacked Bar: Credit Quality by Product - South Region]    │ │
│ │                                                             │ │
│ │ 🚨 Auto Loans are the primary concern:                      │ │
│ │                                                             │ │
│ │ • Auto: Credit score dropped 35 pts (most severe)          │ │
│ │ • Auto: Subprime mix at 42% (vs 18% portfolio avg)         │ │
│ │ • Auto: Approval rate at 78% (highest of all products)     │ │
│ │                                                             │ │
│ │ Mortgages and Credit Cards remain stable.                   │ │
│ │                                                             │ │
│ │ Recommendation: Review Auto underwriting criteria in       │ │
│ │ South region branches.                                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Type your message...]                              [Send]      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Appendix B: API Specifications

### Chat API

```yaml
POST /api/v1/chat
Content-Type: application/json

Request:
{
  "message": "How are originations looking in various regions?",
  "session_id": "sess_abc123",
  "context": {
    "active_filters": {
      "time_period": "Q4-2025"
    }
  }
}

Response:
{
  "response_id": "resp_xyz789",
  "message": "Here are Q4 2025 originations by region...",
  "visualizations": [
    {
      "type": "bar",
      "title": "Origination Volume by Region",
      "data": [...],
      "config": {...}
    }
  ],
  "data_tables": [
    {
      "title": "Originations Summary",
      "columns": ["Region", "Amount", "Count", "% of Total"],
      "rows": [...]
    }
  ],
  "follow_up_suggestions": [
    "Drill down by product",
    "Compare to last quarter",
    "Show trend over time"
  ],
  "metadata": {
    "query_generated": "SELECT region, SUM(amount)...",
    "data_sources": ["fact_originations"],
    "confidence_score": 0.95,
    "processing_time_ms": 1250
  }
}
```

---

**Document Control:**
- Version: 1.0
- Last Updated: December 2025
- Next Review: March 2026
- Owner: CR360 Architecture Team
