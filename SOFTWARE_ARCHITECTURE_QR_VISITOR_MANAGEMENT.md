# Software Architecture Document (SAD) — Version 2.0
## Enterprise QR Code Based Visitor Management & Smart Gate Intelligence Platform

**Document Version:** 2.0  
**Target Segments:** Colleges, Corporate Campuses, Hospitals, Government, Manufacturing Parks  
**Deployment Scale:** 100K+ users, 10+ campuses, burst 5,000 scans / 30 minutes / campus  
**Design Goal:** Secure, resilient, policy-driven visitor lifecycle with real-time and offline gate continuity

---

## 1. Executive Overview

This platform is designed as a **mission-critical visitor orchestration system**, not a basic CRUD app. It combines:

1. **Identity & Trust Layer** — verified identity, fraud checks, policy scoring.
2. **Workflow & Decision Layer** — configurable approval orchestration with escalation.
3. **Gate Execution Layer** — low-latency check-in/check-out, offline-first operation.
4. **Intelligence Layer** — traffic analytics, operational KPIs, compliance evidence.

### 1.1 What is new in Version 2.0
- Stronger **feature depth** (watchlist, SLA, policy engine, geofence policies).
- Better **function logic** (risk scoring, deterministic state machine, rule priorities).
- Explicit **connectivity architecture** (API gateway, event bus, provider abstraction, retries).
- Full **enterprise readiness** (multi-tenancy, SSO/SCIM, SIEM, DR/SLO, compliance controls).

---

## 2. Role-Based Access Control (RBAC) and Responsibilities

### 2.1 Core Roles

| Role | Primary Responsibilities | Allowed Permissions |
|---|---|---|
| **Admin (Institution/Company Owner)** | Organization setup, policy governance, event governance, emergency operations | Manage campuses/departments/users/roles, define approval policies, configure retention, export reports, lock/unlock check-ins, override approvals, manage watchlists |
| **Security Guard** | Gate-side execution and incident capture | Scan QR/ID, manual search, check-in/out/reject, incident tagging, operate offline queue/sync, view minimal profile fields |
| **Staff / Faculty / Host** | Visitor ownership and approval | Approve/reject visitors assigned to self/department, set expected duration, escalate to office/admin |
| **Visitor (Event/Parent/Guest/Vendor)** | Registration and compliance | Register, complete OTP + consent, view pass status, present dynamic QR, receive notifications |

### 2.2 Enterprise RBAC Model
- **Scopes:** organization -> campus -> building -> department -> gate.
- **Policy dimensions:** resource/action/context/time window.
- **ABAC overlay (optional):** e.g., allow override only for “Admin + On-duty + Incident Mode”.
- **Principle:** least privilege + field-level masking (guards cannot view full sensitive profile).

---

## 3. Domain Model and Functional Boundaries

### 3.1 Core Domains
1. **Identity & Access Domain**
2. **Event & Invitation Domain**
3. **Visitor Registration Domain**
4. **Approval Orchestration Domain**
5. **Gate Operations Domain**
6. **Notification Domain**
7. **Analytics & Reporting Domain**
8. **Compliance & Audit Domain**

### 3.2 Functional Contracts
- **Registration Service** emits `RegistrationSubmitted`.
- **Approval Engine** consumes registration, evaluates policy, emits `ApprovalDecisionChanged`.
- **Gate Service** consumes latest status snapshots and emits `VisitorCheckedIn/Out`.
- **Analytics Service** consumes all immutable events for KPIs.

---

## 4. End-to-End Flows (Step-by-Step)

## 4.1 Admin Dashboard Flow

### A) Event Creation
1. Admin creates event with:
   - Event name
   - Department
   - Date/time
   - Visitor limit
   - Approval type (auto/manual/policy)
2. System validates:
   - Venue/time conflicts
   - Capacity thresholds
   - Event policy guardrails
3. Event transitions: `DRAFT -> PUBLISHED -> ACTIVE -> CLOSED -> ARCHIVED`.

### B) Dynamic QR Generation
1. System generates **signed short URL** per event.
2. QR resolves to server endpoint with token claims (event, expiry, nonce, tenant).
3. Token freshness enforced using replay cache in Redis.
4. Rotation profiles:
   - Standard events: 5–15 min rotation
   - Sensitive events: 30–60 sec rotation

### C) Visitor Approval Panel
- Queue segments:
  - Pending
  - Escalated
  - High-risk
  - SLA breached
- Bulk actions + mandatory reason for rejection/override.
- AI-assisted triage (optional): risk summary and suggested action.

### D) Live Visitor Tracking
- By campus/building/gate/event/department:
  - Checked in now
  - Average queue wait time
  - Pending > SLA
  - Overstay count

### E) Analytics + Export
- KPIs:
  - Peak entry windows
  - Avg visit duration
  - Department traffic
  - No-show rate
  - Event conversion
- Export modes: PDF, Excel, signed CSV with checksum.

### F) Emergency Lockdown
- `deny_new_checkins = true` globally or scoped by campus.
- Existing check-outs remain enabled.
- Broadcast alert to all guard devices + audit record enforced.

---

## 4.2 Visitor Registration Flows

### A) Event Visitor Flow
1. Visitor scans event QR.
2. Form captures:
   - Name
   - Register number / ID
   - Department / College
   - Team or individual
   - Phone number (OTP verification)
3. Device fingerprint hash captured.
4. Optional face capture (consent + legal basis required).
5. System creates `visitor_uid` and registration request.
6. Policy engine sets state: `PENDING` / `APPROVED` / `REVIEW_REQUIRED`.
7. Approved users receive dynamic QR pass + validity window.

### B) Parent / Guest Flow (At Gate)
1. Security generates temporary intake session.
2. Visitor enters:
   - Name
   - Phone
   - Department to visit
   - Staff name (directory autocomplete)
   - Purpose
   - Expected duration
3. Request routed to host approval chain.
4. If no response within SLA, auto-reminder + escalation.

### C) Vendor / Contractor Flow (V2)
- Adds vehicle number, material declaration, compliance docs.
- Mandatory check-out with seal/asset verification (optional enterprise workflow).

---

## 4.3 Smart Staff Approval Engine (Multi-Level + Policy)

### Approval Levels
- **L1:** Host Staff
- **L2:** Department Office
- **L3:** Admin Override / Security Control Room

### Rule Logic
1. Request enters `WAITING_L1`.
2. If no response in 10 min:
   - reminder to L1,
   - escalate to L2.
3. If L2 times out per policy:
   - escalate to L3.
4. Auto-approve rules:
   - within meeting hours,
   - low risk score,
   - visitor not on watchlist.
5. Auto-reject rules:
   - outside campus hours,
   - failed OTP,
   - blacklist hit,
   - risk score above threshold.

### Deterministic Decision Priority
`BLACKLIST > SECURITY_POLICY > EXCEPTION_WHITELIST > MEETING_HOURS > MANUAL_APPROVAL`

### Notification Channels
- Mobile push
- SMS
- Email
- WhatsApp Business

### Reliability for Notifications
- Provider abstraction + fallback chain (e.g., push -> SMS -> email).
- At-least-once delivery with idempotency keys.
- Dead letter queue for failed deliveries.

---

## 4.4 Security Dashboard (Offline-First, High Throughput)

### Guard Workflow
1. Scan QR or enter Visitor ID.
2. Render status in <300ms target (cache-first):
   - Approved
   - Pending
   - Rejected
   - Expired
   - Blacklisted
3. One-tap actions:
   - ✔ Check-In
   - ❌ Reject
   - 🚪 Check-Out
4. Auto-capture timestamp + guard device/gate context.
5. Duration computed at check-out.

### Offline Continuity
- Local encrypted cache contains:
  - active approved snapshots,
  - watchlist fragments,
  - active event windows,
  - last-known policies.
- Local action queue appends immutable events.
- Sync daemon flushes on connectivity restore (exponential backoff + jitter).
- Reconciliation model:
  - server is source of truth,
  - conflicts logged,
  - guard receives resolution hints.

### High-Crowd Scan Mode
- Reduced UI animation, continuous camera decoding, batch pre-validation.
- Duplicate scan debounce to avoid accidental double check-in.

---

## 5. Fraud, Misuse and Trust Controls

1. **Dynamic QR Rotation** with short TTL and nonce replay protection.
2. **Screenshot Resistance** via animated watermark + dynamic timestamp overlay.
3. **OTP Enforcement** with configurable attempt limits.
4. **Duplicate Detection** using phone hash + device fingerprint + temporal patterns.
5. **Blacklist / Watchlist Engine** with active period and reason classification.
6. **Rate Limiting & Bot Protection**
   - per IP,
   - per device,
   - per phone,
   - per event endpoint.
7. **Anomaly Detection (V2)**
   - impossible entry patterns,
   - repeated rejection attempts,
   - rapid multi-device registrations.
8. **Optional Face Match (Enterprise)** with threshold + manual override + audit.

---

## 6. Connectivity Architecture (APIs, Events, Integrations)

### 6.1 Service Connectivity Diagram

```text
[Web / Mobile / Guard PWA]
          |
      HTTPS + JWT
          |
 [API Gateway + WAF + Rate Limit]
          |
   -------------------------------
   | Auth | Registration | Approval |
   | Gate | Notification | Reporting|
   -------------------------------
      |        |            |
   [Redis]  [PostgreSQL]  [Object Store]
      |
   [Event Bus / Queue]
      |
 [SMS] [Email] [WhatsApp] [Push] [SIEM/BI]
```

### 6.2 API Design Principles
- Versioned APIs (`/api/v1`, `/api/v2`).
- Idempotent mutation endpoints for gate actions.
- Correlation ID for every request.
- Contract-first OpenAPI specs with backward compatibility policy.

### 6.3 External Integrations
- **Identity:** SSO via SAML/OIDC.
- **Provisioning:** SCIM user sync.
- **Messaging:** Twilio/MSG91/Meta WhatsApp adapters.
- **SIEM:** Splunk/ELK/Sentinel event forwarding.

---

## 7. Failure Handling and Business Continuity

### 7.1 Failure Matrix

| Failure | Operational Risk | Recovery / Fallback |
|---|---|---|
| Internet outage | No live API | Local approved cache, offline queue, manual ID search, deferred sync |
| API node crash | Reduced service capacity | Auto-healing pods + load balancer reroute |
| DB primary failure | write disruption | managed failover/read replica promotion |
| Redis failure | cache/queue disruption | degraded mode, direct DB read for critical checks, queue replay |
| Guard device battery drain | gate slowdown | spare devices + charging dock + kiosk fallback |
| Site power outage | gate shutdown | UPS, generator, paper protocol, post-restore reconciliation |

### 7.2 Paper Fallback Protocol (Mandatory)
1. Use pre-approved printed logbook template.
2. Capture: name, phone, host, purpose, entry time, guard ID/sign.
3. Post-recovery backfill with `source=paper_fallback` + verifier signature.

### 7.3 Disaster Recovery Targets
- **RPO:** <= 5 minutes
- **RTO:** <= 30 minutes
- Quarterly DR drills with signed audit evidence.

---

## 8. Production Data Model

### 8.1 Core Tables
- `tenants` (enterprise multi-org)
- `campuses`
- `buildings`
- `gates`
- `departments`
- `users`
- `roles`
- `permissions`
- `role_permissions`
- `staff_profiles`
- `events`
- `visitors`
- `registrations`
- `approval_steps`
- `approval_decisions`
- `checkin_logs`
- `notifications`
- `blacklist_entries`
- `consent_records`
- `policy_rules`
- `audit_logs`

### 8.2 Suggested Column Highlights
- `visitors`: `phone_enc`, `phone_hash`, `device_fingerprint_hash`, `risk_score`, `consent_id`.
- `registrations`: `status`, `source`, `approval_path`, `expires_at`.
- `checkin_logs`: `checkin_at`, `checkout_at`, `duration_sec`, `gate_id`, `device_id`.
- `audit_logs`: immutable append-only with actor, action, before/after, IP, correlation_id.

### 8.3 Indexing Strategy for Fast Scan/Lookup
- `visitors(visitor_uid)` unique.
- `visitors(phone_hash)` for duplicate detection.
- `registrations(event_id, status, created_at)` for queue operations.
- `registrations(visitor_id, event_id)` unique constraints where needed.
- `approval_decisions(registration_id, level, decided_at)`.
- `checkin_logs(registration_id, checkin_at DESC)`.
- Partial index for active events and active blacklist entries.

### 8.4 Partitioning & Archival
- Partition `checkin_logs` and `audit_logs` monthly.
- Lifecycle archival to object storage for long-term compliance.

---

## 9. Security and Privacy Architecture

1. **AuthN/AuthZ**
   - JWT access tokens + rotating refresh tokens.
   - RBAC + scoped claims.
2. **Encryption**
   - TLS 1.2+ in transit.
   - AES encryption at rest.
   - Field-level encryption/tokenization for phone and identity references.
3. **Consent & Privacy**
   - purpose-specific consent capture,
   - versioned privacy notice,
   - consent withdrawal workflow.
4. **Data Retention**
   - configurable auto-delete/anonymize schedule (e.g., 30/90/180 days).
5. **Auditability**
   - immutable tamper-evident logs.
6. **Compliance-Ready**
   - GDPR-style controls,
   - DPIA support,
   - data subject request workflows.

---

## 10. Scalability and Performance Engineering

### 10.1 Capacity Strategy (5,000 scans / 30 mins)
- Stateless API services behind load balancer.
- Horizontal autoscaling by CPU + RPS + queue depth.
- Redis pre-warmed approval snapshots by active event.
- Read replicas for high read workloads.
- Async pipelines for non-blocking operations (notifications/reports).

### 10.2 Latency Targets
- Gate validation p95: <300 ms (online).
- Dashboard query p95: <1.5 sec for active-day views.
- Notification dispatch start: <5 sec from trigger.

### 10.3 Architecture Choice: Modular Monolith -> Microservices
- **Phase 1:** modular monolith for speed + consistency.
- **Phase 2:** extract Notification, Analytics, and Approval engines first.
- **Why:** best balance of delivery velocity, reliability, and operational complexity.

---

## 11. Recommended Tech Stack (Recruiter-Respected)

### Frontend
- **Next.js + React + TypeScript** (Admin/Staff web)
- **PWA mode** for Security guard app (offline cache + camera APIs)

### Backend
- **NestJS (Node.js + TypeScript)**
  - modular architecture,
  - strong guards/interceptors for RBAC,
  - good async/event integration.
- Alternative: **FastAPI** for AI-heavy extensions.

### Data & Infra
- **PostgreSQL** (system of record)
- **Redis** (cache + rate limiting + queue)
- **Kafka/SQS/RabbitMQ** (event backbone)
- **S3/GCS/Azure Blob** (exports, archived logs, consent docs)

### Cloud
- AWS/GCP/Azure with:
  - WAF + CDN,
  - managed DB,
  - autoscaling compute,
  - centralized observability.

### Tradeoff Summary
- NestJS + PostgreSQL + Redis yields strong hiring market alignment and maintainable enterprise architecture with predictable cost.

---

## 12. MVP vs Advanced vs Enterprise 2.0

### 🔥 MVP (Must Build)
- Core RBAC (Admin/Security/Staff/Visitor)
- Event setup + secure QR registration
- OTP verification
- Multi-level approvals (basic escalation)
- Gate check-in/check-out
- Basic analytics and CSV export
- Audit logs and retention config

### ⭐ Advanced
- Offline-first guard app with sync + reconciliation
- Dynamic QR rotation and stronger anti-fraud controls
- Multi-channel notifications with fallback routing
- SLA dashboards + delay alerts
- PDF/Excel scheduled reports

### 🚀 Enterprise 2.0
- Multi-tenant, multi-campus architecture
- SSO (SAML/OIDC) + SCIM provisioning
- SIEM integration and policy-based incident workflows
- Face match, watchlist alerts, advanced anomaly detection
- Contractual SLOs, DR drills, compliance automation

---

## 13. UX Principles for Non-Technical Guards

1. **2-click path:** scan -> confirm.
2. **Large touch targets** and icon-first UI.
3. **Traffic-light states:** green/amber/red.
4. **Error-proof prompts:** always show next best action.
5. **Local language support** + dark mode.
6. **Accessibility:** high contrast, readable type, vibration/audio feedback.
7. **Training minimization:** embedded guided tooltips and shift-start checklists.

---

## 14. Enterprise Features and Future Innovation

- Visitor heatmaps and occupancy intelligence.
- AI crowd prediction for gate staffing optimization.
- Repeat visitor trust scoring.
- Watchlist and threat-intel federation.
- Smart parking pass + EV charging integration.
- Self-service kiosks with multilingual voice guidance.
- Unified identity for cafeteria/library/access control convergence.

---

## 15. Observability, Governance, and SRE

### 15.1 SLOs
- Gate validation availability: **99.95%**
- Approval workflow availability: **99.9%**
- Notification dispatch success: **>=99%**

### 15.2 Telemetry
- Central logs + metrics + traces.
- Business KPIs and technical KPIs in one operations dashboard.
- Alerting on queue depth, latency spikes, sync failures, and SLA breaches.

### 15.3 Governance
- Change management with feature flags.
- Policy updates are versioned and auditable.
- Quarterly security assessments and penetration tests.

---

## 16. Canonical State Machine (Version 2.0)

```text
DRAFT_REGISTRATION
  -> OTP_VERIFIED
  -> RISK_EVALUATED
  -> PENDING_APPROVAL
      -> ESCALATED_L2
      -> ESCALATED_L3
  -> APPROVED
  -> PASS_ISSUED
  -> CHECKED_IN
  -> CHECKED_OUT
  -> CLOSED

Any state -> REJECTED
Any active state -> EXPIRED
Any active state -> MANUAL_HOLD (security incident)
```

This state machine provides deterministic behavior, clear auditability, and enterprise-grade operational control.
