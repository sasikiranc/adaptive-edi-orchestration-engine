# Adaptive EDI Routing Engine with Hybrid Rule + Similarity Intelligence
Enterprise-ready EDI routing engine combining rules, ML similarity scoring, manual overrides, and secure OAuth-based APIs for intelligent integration orchestration.

🚀 Overview

This project implements an SAP BTP-ready AI orchestration microservice designed for high-volume structured message environments such as:

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


🧠 Routing Intelligence Layer

The routing engine uses a multi-stage decision strategy to determine the best routing rule for an incoming message.

The system progressively moves from deterministic routing to similarity-based routing.

	Rule Engine
	      ↓
	Feature Scoring
	      ↓
	Vector Similarity Fallback
	      ↓
	Manual Review

This design ensures deterministic routing whenever possible while still handling unknown or partially matching messages.

⚡ Candidate Index (Fast Rule Lookup)

To avoid scanning all routing rules for every message, rules are indexed in memory during application startup.

Index Key
	(message_type, direction)

Example:

	('850','INBOUND')
	('ORDERS','OUTBOUND')
	('810','INBOUND')
	Index Structure
	CANDIDATE_INDEX = {
	   ('850','INBOUND'): [rule1, rule2],
	   ('ORDERS','OUTBOUND'): [rule3]
	}

This reduces rule lookup from:

	O(n) → O(1)

which allows the system to scale to thousands of routing rules.

🧩 Feature-Based Scoring Engine

When multiple candidate rules exist, the router calculates a feature match score.

Features Used
| Feature         | Description         |
| --------------- | ------------------- |
| message_type    | Transaction type    |
| source_system   | Originating system  |
| receiver_system | Target system       |
| direction       | INBOUND / OUTBOUND  |
| version         | EDI or IDOC version |

Matching Rules

	Exact match → score 1
	Mismatch → score 0
	Null rule value → wildcard match

Example wildcard rule:

	receiver_system = NULL

means:

	match any receiver
	
Weighted Scoring

Weights are stored in the configuration table:

	similarity_weights

Example configuration:

| Feature         | Weight |
| --------------- | ------ |
| message_type    | 0.3    |
| source_system   | 0.3    |
| receiver_system | 0.2    |
| direction       | 0.1   |
| version         | 0.1    |

Score Calculation
	score =
	(match(message_type) × weight_message_type)
	+
	(match(source_system) × weight_source_system)
	+
	(match(receiver_system) × weight_receiver_system)
	+
	(match(direction) × weight_direction)
	+
	(match(version) × weight_version)

Score range:

	0.0 → no match
	1.0 → perfect match
	
🤖 Vector Similarity Fallback (AI Routing)

If no rule achieves the minimum confidence threshold, the router falls back to vector similarity matching against historical routes.

Historical routing decisions are stored in:

	historical_routes

Each historical message is converted into a feature vector.

Example vector representation:

	[message_type, source_system, receiver_system, direction, version]

The incoming message vector is compared against historical vectors using cosine similarity.

The most similar historical message determines the routing decision.

Example

	Incoming message: 850 inbound

Closest historical match:

	850 inbound from same partner

Routing decision:

	ROUTED_AI
	
🔁 Learning Behavior

When a manual override occurs:

Routing decision is stored in

	historical_routes

Audit entry is created in

	routing_audit

Future similar messages can be auto-routed using vector similarity.

This enables the system to learn routing patterns over time.

Decision Weights

| Decision Type        | Weight |
| -------------------- | ------ |
| ROUTED_RULE          | 0.9    |
| MANUAL_OVERRIDE      | 1.0    |
| ROUTED_AI            | 0.8    |
| PARKED_MANUAL_REVIEW | 0.3    |

Final confidence = similarity_score × decision_weight

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

	partner_identity_map

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

🔁 Routing Flow

	Incoming Message
	        │
	        ▼
	Payload Normalization
	(IDOC / X12)
	        │
	        ▼
	Canonical Message
	        │
	        ▼
	Candidate Index Lookup
	(message_type, direction)
	        │
	        ▼
	Feature Scoring Engine
	        │
	        ├─ High score → ROUTED_RULE
	        │
	        └─ Low score
	                │
	                ▼
	        Vector Similarity Search
	                │
	                ├─ Match → ROUTED_AI
	                │
	                └─ No match → PARKED_MANUAL_REVIEW

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

	POST /admin/reload-config

		Reloads configuration tables into the engine.

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
