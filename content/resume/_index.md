---
title: "Resume"
date: 2026-03-10
layout: "simple"
---

[Download Resume (PDF)](/files/resume.pdf)

---

## Professional Summary

Senior Software Engineer with 13+ years of experience spanning enterprise SaaS, AI/ML, and defense/aerospace. Currently designing and shipping LLM-powered agentic features at Salesforce (Tableau), backed by evaluation pipelines and statistical testing frameworks that validate AI output quality at scale. Built the core analytics platform powering trend analysis, forecasting, and anomaly detection for Tableau Pulse.

---

## Technical Skills

- **AI/ML & LLM:** LLM integration & prompt engineering, evaluation pipeline design, golden dataset creation, agentic workflows, TensorFlow, PyTorch, scikit-learn
- **Languages:** Go, Python, Java, JavaScript (LWC), Bash, C/C++, C#
- **Cloud & Infra:** AWS (S3, Lambda, EKS/ECS), Kubernetes, Docker, Redis, Splunk, Proxmox, Grafana, Prometheus
- **Architecture:** Microservice design, gRPC/Protobuf, REST, CI/CD, distributed systems
- **Data & Analytics:** Time series analysis, trend detection, forecasting, driver analysis

---

## Professional Experience

### Salesforce (Tableau) — Denver, CO
**Software Engineering SMTS** | January 2022 -- Present *(joined via acquisition of Narrative Science)*

#### Tableau Next — AI-Powered Data Insights (2024--Present)

- Architected the Metric Insight Summary, an LLM-powered agentic feature that generates natural language summaries of business metric insights, shipped to production across Tableau's analytics platform serving enterprise customers
- Implemented end-to-end LLM evaluation pipelines with golden datasets and statistical testing frameworks to validate output quality across non-deterministic responses, establishing the team's approach to AI quality assurance
- Led prompt engineering efforts including few-shot examples, iterative tuning with product stakeholders, and pre/post-processing strategies for reliable span tag preservation, reducing hallucinations in production summaries
- Built multilingual summarization supporting Japanese and other languages, designing span preservation strategies to maintain entity names and formatting integrity across translations
- Engineered cross-metric insight summarization enabling LLM-powered summaries across multiple business metrics with error side-channels, partial success handling, and LLM response caching for cost/performance optimization
- Implemented LLM gateway integration via SFAP/Connect API with user feedback mechanisms (thumbs up/down), and managed rollout across commercial and GovCloud environments
- Created FIT (Functional Integration Test) infrastructure for LLM-dependent endpoints across multiple environments, enabling automated regression detection during deployments

#### Tableau Pulse — Insights Service Platform (2022--2024)

- Engineered the core insights microservice (Go, gRPC, Protobuf) generating 12+ insight types including trend analysis, forecasting, anomaly detection, top drivers, and risk analysis for Tableau Pulse's metric monitoring platform
- Built the metric query service layer including a semantic query builder, database migrations, and query optimization with configurable retry logic and error classification that improved platform reliability and SLA compliance
- Implemented the asynchronous batch generation endpoint with concurrent multi-metric analysis, enabling parallel insight computation across metrics with polling-based result retrieval and response caching
- Developed pinned metrics microservice architecture and API for CRMA integration, producing ERD designs, component diagrams, and API specifications reviewed by cross-functional stakeholders
- Researched open-source LLM alternatives (GPT-NeoX fine-tuning) for NLG paraphrasing to reduce dependency on commercial APIs, establishing early LLM experimentation practices for the team
- Developed time series trend analysis service with model training pipelines, job management APIs, and serialized model storage in DynamoDB/S3
- Led feature rollout strategy using feature flags and gated rollout definitions across dev, test, perf, prod, and GovCloud environments, coordinating with multiple downstream teams
- Implemented template refactoring initiative replacing monolithic NLG template strings with modular, testable template architecture, improving maintainability across 12+ insight types

#### Narrative Science — Analytics Platform (2021--2022)

- Contributed to the Lexio analytics platform, building model management APIs and ML training job infrastructure using Python and AWS services (DynamoDB, S3, Step Functions)
- Built ML-based recommendation system for insight ordering, including data quality validation and event tracking pipelines
- Developed microservice endpoints for time series model CRUD operations and training job orchestration prior to Salesforce acquisition

### Sierra Nevada Corporation — Denver, CO
**Aerospace Software Engineer — Team Lead** | July 2017 -- September 2021

- Led software team for award-winning classified training system used by multiple government agencies; hired and managed engineers for a $24M program
- Integrated avionics, radios, and weapons systems onto the A-29 platform for the "Light Attack Experiment," contributing to a successful contract award
- Led customer requirements meetings, sprint planning, and code reviews; administered JIRA projects and maintained system/network architecture
- Designed and demonstrated a prototype universal cockpit input device architecture
- Refactored legacy codebases and common code repositories to modernized libraries and architectural patterns

### The Boeing Company — St. Louis, MO
**Software & Electrophysics Engineer** | June 2012 -- June 2017

- Designed embedded software for Advanced Mission Computers and cockpit displays of the F/A-18 and E/A-18G combat jets
- Implemented cockpit display formats and features for the operational flight program to enhance flight crew situational awareness
- Developed software interfacing multiple hardware components in a multi-layer architecture, collaborating with hardware vendors on transmission and messaging protocols
- Developed C# and MATLAB automation tools for data processing, saving 30% of engineering hours
- Predicted electromagnetic properties of air vehicle components using method of moments and physical optics codes
- Presented radar cross-section and antenna gain analysis to an integrated product team in support of program-level trade studies

---

## Technical Projects

**Self-Hosted Infrastructure Lab** — Operate a Proxmox virtualization environment with infrastructure-as-code practices, managing multiple VMs running containerized services via Docker Compose and systemd. Built a full observability stack with Grafana dashboards, Prometheus metrics collection, and HTTP endpoint monitoring. Deploy a Hugo-based personal website through a GitHub Actions CI/CD pipeline with Caddy reverse proxy behind Cloudflare.

---

## Education

**Arizona State University** — M.S. Computer Science (AI/ML coursework focus), August 2021

**University of Missouri** — B.S. Electrical Engineering, May 2012

---

## Security Clearance

DoD Top Secret/SSBI — held 2013--2023, eligible for reinstatement
