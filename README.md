# Kijiji-Guard 🛡️
### The Open-Source Compliance Scanner Built for Africa

> Securing Africa's next unicorns — without the dollar-denominated security tax.

Kijiji-Guard is a lightweight, open-source Security-as-Code framework that automatically scans your infrastructure for compliance with African data protection regulations. No expensive foreign tools. No complex setup. Just run a scan and know exactly where you stand.

---

## Why Kijiji-Guard?

African startups are legally required to comply with local data protection laws — but every compliance tool on the market was built for GDPR, not NDPA. Kijiji-Guard changes that.

- **African-first:** Built specifically for NDPA 2023, Ghana DPA, Kenya DPA, Rwanda Law 058/2021, Côte d'Ivoire Loi 2013-450, Bénin Loi 2017-20, and Egypt PDPL 2020
- **Multi-platform:** Scans Terraform/IaC files, live Vercel projects, and Supabase databases — not just AWS
- **Instant setup:** No Checkov, no heavy dependencies. Installs in seconds.
- **Open source:** Apache 2.0. Free forever for the community.

---

## Supported Regulations

| Country | Regulation | Governing Body | Checks |
|---------|-----------|----------------|--------|
| 🇳🇬 Nigeria | NDPA 2023 + NDPC GAID 2025 | NDPC | 6 |
| 🇬🇭 Ghana | Data Protection Act 2012 | DPC | 5 |
| 🇰🇪 Kenya | Data Protection Act 2019 | ODPC | 6 |
| 🇷🇼 Rwanda | Law No.058/2021 | NCSA | 5 |
| 🇨🇮 Côte d'Ivoire | Loi n°2013-450 | ARTCI | 5 |
| 🇧🇯 Bénin | Loi n°2017-20 | CRIET | 5 |
| 🇪🇬 Egypt | PDPL Law No.151/2020 | PDPC | 6 |

**Total: 38 compliance checks across 7 African countries**

---

## What It Scans

**Tier 1 — Infrastructure as Code**
Terraform, Kubernetes YAML, CloudFormation. Upload your IaC files and get an instant compliance report mapped to your country's regulation.

**Tier 2 — Live Cloud APIs** *(coming soon)*
AWS, GCP, Azure, DigitalOcean. Connect your cloud account and scan live infrastructure — no IaC needed.

**Tier 3 — PaaS Platforms**
Vercel and Supabase — the platforms most African startups actually use. Connect your API token and scan your real projects in seconds.

---

## Quick Start

### Requirements
- Python 3.9+
- Windows: use `py` instead of `python`

### Install

```bash
# Clone the repo
git clone https://github.com/Kijiji-Guard/kijiji-guard.git
cd kijiji-guard

# Install dependencies (takes ~10 seconds)
pip install python-hcl2 rich typer pyyaml requests python-dotenv

# Windows users:
py -m pip install python-hcl2 rich typer pyyaml requests python-dotenv
```

### Scan a Terraform file

```bash
# Scan the included sample against Nigerian NDPA 2023
python cli/main.py scan --target sample_startup.tf --country nigeria

# Windows:
py cli/main.py scan --target sample_startup.tf --country nigeria

# Scan against ALL 7 country regulations at once
py cli/main.py scan --target sample_startup.tf --country all
```

### Scan your Vercel project

```bash
# Get your token at: vercel.com/account/tokens
py cli/main.py scan --target vercel --country nigeria
# You'll be prompted for your Vercel token
```

### Scan your Supabase project

```bash
# Get your token at: supabase.com/dashboard/account/tokens
py cli/main.py scan --target supabase --country kenya
```

### Launch the dashboard

```bash
# Terminal 1 — start the API server
py -m uvicorn cli.api_server:app --reload --port 8000

# Terminal 2 — start the dashboard
cd dashboard && npm install && npm run dev

# Open http://localhost:5173
```

---

## Example Output

```
┌─────────────────────────────────────────────────────────────────┐
│  Kijiji-Guard Compliance Scan                                   │
│  Target: sample_startup.tf | Country: Nigeria — NDPA 2023      │
└─────────────────────────────────────────────────────────────────┘
Check ID      Name                              Result  Regulation
───────────────────────────────────────────────────────────────────
CKV_NGR_001   Data residency — African region   PASS    NDPA §41
CKV_NGR_002   Data retention policy             FAIL    NDPA §24
CKV_NGR_003   Encryption at rest                PASS    NDPA §34
CKV_NGR_004   CloudTrail breach monitoring      FAIL    NDPA §40
CKV_NGR_005   S3 public access blocked          FAIL    NDPA §41
Summary: 2 passed · 3 failed · 0 warnings · Pass rate: 40.0%
Remediation for CKV_NGR_002:
Add lifecycle_rule with expiration to enforce data retention limits.
NDPA Section 24 requires data not be kept longer than necessary.
```

---

## Project Structure

```
kijiji-guard/
├── cli/                        # Python scanner engine
│   ├── main.py                 # CLI entry point
│   ├── core/
│   │   ├── orchestrator.py     # Routes scans to adapters
│   │   └── report.py           # Terminal, JSON, HTML output
│   └── adapters/
│       ├── iac/                # IaC scanner (python-hcl2)
│       │   └── policies/       # Country-specific policy classes
│       ├── api/                # Live cloud API scanners (coming soon)
│       └── paas/               # Vercel, Supabase, Firebase scanners
├── src/                        # React + Vite web dashboard
├── policies/                   # Legacy Checkov-style policy files
├── terraform/                  # Reference compliant IaC templates
└── docs/
    └── regulations/            # Plain-English regulation summaries
```

---

## Roadmap

- [x] IaC scanning — Terraform/HCL (7 countries, 38 checks)
- [x] PaaS scanning — Vercel (5 checks) + Supabase (6 checks)
- [x] Web dashboard with compliance overview
- [x] HTML auditor report export
- [ ] `pip install kijiji-guard` package release
- [ ] Live AWS/GCP/Azure API scanning
- [ ] GitHub Action for CI/CD compliance gates
- [ ] GCP and Azure IaC policies
- [ ] Docker image for zero-install usage
- [ ] Rwanda NCSA certificate verification API

---

## Contributing

We welcome contributions from African developers and security researchers.

**Priority areas:**
- GCP and Azure policy checks for existing countries
- New country regulations (South Africa POPIA, Senegal, Tanzania)
- PaaS adapters for Firebase, Render, Railway
- Translations of regulation summaries into French (for Francophone West Africa)

See [docs/contributing.md](docs/contributing.md) to get started.

---

## Built for AfricaCyberFest 2026

Kijiji-Guard was built for the AfricaCyberFest 2026 Solutions Hackathon Open Track — a 48-hour engineering sprint to build open-source security tools for African and global challenges.

**Track:** Open Track — Compliance Automation  
**Event:** Africa CyberFest 2026, Lagos, Nigeria

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

Copyright (c) 2026 Kijiji-Guard Contributors

---

*Kijiji (Swahili) — "village." Security for the whole village.*
