
   *ADAPTIVE EDI ORCHESTRATION ENGINE*

	Enterprise-ready EDI routing engine combining rules, ML similarity scoring, manual overrides, 
	and secure OAuth-based APIs for intelligent integration orchestration.

🚀 Overview

This project implements a BTP-ready AI orchestration microservice designed for high-volume structured message environments such as:

	EDI / X12 integrations
	
	SAP S/4HANA IDOC exchange
	
	Trading Partner Management (TPM) routing
	
	Integration Suite (CPI) transformation pipelines

The system acts as a primary routing intelligence layer, determining:

	Target endpoint
	
	Mapping guideline (TPM ID)
	
	Routing confidence
	
	Anomaly detection
	
	Manual override governance

CPI remains a transformation engine.
This microservice becomes the decision brain.

🏗 Architecture

	Enterprise Sources
		├── EDI/X12 Partners
		├── S/4HANA (IDOC)
		└── EDI Gateway (e.g., Seeburger)
            ↓				
	AI Routing Microservice (FastAPI on CF)
		├── Canonical Normalization
		├── Deterministic Rule Engine
		├── Similarity-Based ML Engine
		├── Confidence Scoring
		├── Human Override Loop
            ↓
	SAP CPI / Integration Suite
		├── TPM Mapping
		├── Transformation
		└── Delivery
  
🧠 Core Design Principles

1️⃣ Deterministic First

Explicit rule table (routing_rules) always takes precedence.

2️⃣ AI-Assisted Routing

When no rule matches:

Similarity-based scoring is applied

Weighted feature comparison

Decision-weight hierarchy

3️⃣ Confidence-Governed Decision

If confidence < threshold → Parked for review

4️⃣ Human-in-the-Loop Learning

Manual override:

Updates historical_routes

Influences future similarity scoring

Strengthens learning memory

5️⃣ Config-Driven Engine

No hardcoded enums.
All features, weights, and thresholds come from DB config tables.

📦 Technology Stack
| Layer         | Technology                           |
| ------------- | ------------------------------------ |
| API Framework | FastAPI                              |
| ML Logic      | NumPy (structured similarity engine) |
| Database      | PostgreSQL                           |
| Cloud Runtime | SAP BTP Cloud Foundry                |
| Security      | XSUAA / OAuth2 JWT validation        |
| Deployment    | cf push                              |
| Observability | Structured logging                   |


📊 Database Schema

🔹 routing_rules

Deterministic routing configuration

	message_type
	
	source_system
	
	receiver_system
	
	direction
	
	version
	
	partner_id
	
	target_endpoint
	
	mapping_id
	
	active

🔹 historical_routes

Adaptive learning memory

	control_number
	
	message_type
	
	msg_format
	
	source_system
	
	receiver_system
	
	partner_id
	
	direction
	
	version
	
	target_endpoint
	
	tpm
	
	decision_type
	
	confidence

🔹 routing_audit

Full routing traceability

	request_id
	
	message_type
	
	partner_id
	
	direction
	
	endpoint
	
	mapping_id
	
	decision_type
	
	confidence
	
	version
	
	timestamp

🔹 Configuration Tables

	message_types
	
	systems
	
	versions
	
	directions
	
	similarity_weights
	
	decision_weights

	confidence_thresholds

Loaded into memory at startup.

⚙ Canonical Model

All incoming messages (IDOC or EDI) are normalized into:

	message_type
	source_system
	receiver_system
	format
	partner_id (technical receiver)
	version
	control_number
	direction (inferred)

Direction inference is logic-based, not hardcoded.

🤖 Similarity Engine

Feature vector built dynamically from DB records.

Weighted Features
| Feature         | Weight |
| --------------- | ------ |
| message_type    | 2.0    |
| source_system   | 1.5    |
| receiver_system | 1.3    |
| direction       | 1.2    |
| version         | 1.0    |

Decision Weights
| Decision Type        | Weight |
| -------------------- | ------ |
| ROUTED_RULE          | 1.0    |
| MANUAL_OVERRIDE      | 1.2    |
| ROUTED_AI            | 0.8    |
| PARKED_MANUAL_REVIEW | 0.3    |


Final confidence = similarity_score × decision_weight

🔁 Routing Flow

	Normalize input
	
	Match routing_rules
	
	If match → ROUTED_RULE
	
	If no match → similarity engine
	
	If confidence ≥ threshold → ROUTED_AI
	
	Else → PARKED_MANUAL_REVIEW
	
	Manual override updates learning memory

🔐 Security

	OAuth2 / XSUAA JWT validation
	
	Protected governance endpoints
	
	Enterprise-ready authentication model

🛠 Governance APIs
	
	POST /governance/manual-override

		Corrects a routing decision and strengthens learning.

	GET /rules

		List routing rules.

	POST /rules

		Create deterministic routing rule.

☁ Cloud Deployment (BTP CF)

Project structure:

	ai-edi-orchestration-engine/
	│
	├── app/
	│   ├── api/
	│   │   ├── main.py
	│   │   └── routers/
	│   │        ├── rules.py
	│   │        └── governance.py
	│   │
	│   ├── core/
	│   │    ├── config.py
	│   │    ├── security.py
	│   │    └── logging_config.py
	│   │
	│   ├── models/
	│   │    └── canonical.py
	│   │
	│   ├── normalizer/
	│   │    └── normalizer.py
	│   │
	│   ├── routing/
	│   │    ├── rule_engine.py
	│   │    └── similarity_engine.py
	│   │
	│   ├── services/
	│   │    ├── config_cache.py
	│   │    └── governance_service.py
	│   │
	│   ├── persistence/
	│   │    ├── db.py
	│   │    └── repositories/
	│   │         ├── repository.py
	│
	├── scripts/
	│   ├── create_table.py
	│   ├── delete_table.py
	│   ├── read_table.py
	│   └── insert_config.py
	│
	├── docs/
	│   └── architecture.png
	│
	├── manifest.yml
	├── Procfile
	├── requirements.txt
	├── README.md
	└── xs-security.json

Procfile:

	web: uvicorn app.api.main:app --host 0.0.0.0 --port 8080

Deploy:

	cf push

🧪 Learning Behavior Example

	Ambiguous ORDERS message arrives
	
	No rule match
	
	Confidence = 0.58 → Parked
	
	Manual override applied
	
	Similar message arrives
	
	Confidence increases
	
	Auto-route triggered

Structured ML evolution without LLM dependency.

📈 Roadmap

	Full audit versioning
	
	Confidence drift monitoring
	
	Adaptive weight tuning
	
	Multi-tenant routing isolation
	
	Vector DB migration (optional)
	
	AI anomaly detection layer
	
	SAP Event Mesh integration
	
	CAP-based rewrite (future)

🎯 Positioning

This is not a simple router.
	
It is a:
	
	Productizable BTP-based AI Orchestration Framework
	
Designed for:
	
	High-volume EDI landscapes
	
	Multi-partner ecosystems
	
	Enterprise integration governance
	
	Adaptive routing environments

🧩 Why This Matters

Most integration platforms:

	Transform data

	Route based on static configuration

This engine:

	Learns from historical decisions

	Adjusts similarity confidence

	Allows governance control

	Reduces manual routing effort over time

Deterministic first | AI-assisted when necessary | Human-in-the-loop when required.
