# Kijiji-Guard 🛡️
### The Open-Source Compliance Scanner Built for Africa

> Securing Africa's next unicorns — without the dollar-denominated 
> security tax.

Kijiji-Guard is a lightweight, open-source Security-as-Code framework 
that automatically scans your infrastructure for compliance with African 
data protection regulations. No expensive foreign tools. No Checkov 
dependency. No complex setup. Just run a scan and know exactly where 
you stand.

---

## Why Kijiji-Guard?

African startups are legally required to comply with local data 
protection laws — but every compliance tool on the market was built 
for GDPR, not NDPA. Kijiji-Guard changes that.

- **African-first:** Built specifically for NDPA 2023, Ghana DPA 2012,
  Kenya DPA 2019, Rwanda Law 058/2021, Côte d'Ivoire Loi 2013-450,
  Bénin Loi 2017-20, and Egypt PDPL 2020
- **Multi-platform:** Scans Terraform/IaC files, live Vercel projects,
  and Supabase databases — not just AWS
- **Instant setup:** No Checkov, no heavy dependencies. 
  Six packages. Installs in 10 seconds.
- **Open source:** Apache 2.0. Free forever for the community.
- **Real enforcement context:** NDPC issued compliance notices to 1,368
  Nigerian organizations in 2025. Fines reach ₦10M or 2% annual revenue.

---

## Supported Regulations

| Country | Regulation | Governing Body | Checks |
|---------|-----------|----------------|--------|
| 🇳🇬 Nigeria | NDPA 2023 + NDPC GAID 2025 | NDPC | 6 |
| 🇬🇭 Ghana | Data Protection Act 2012 (Act 843) | DPC | 5 |
| 🇰🇪 Kenya | Data Protection Act 2019 | ODPC | 6 |
| 🇷🇼 Rwanda | Law No.058/2021 | NCSA | 5 |
| 🇨🇮 Côte d'Ivoire | Loi n°2013-450 | ARTCI | 5 |
| 🇧🇯 Bénin | Loi n°2017-20 | CRIET | 5 |
| 🇪🇬 Egypt | PDPL Law No.151/2020 + Exec Regs 2025 | PDPC | 6 |

**Total: 38 compliance checks across 7 African countries**

---

## What It Scans

**Tier 1 — Infrastructure as Code**
Terraform (.tf files), Kubernetes YAML, CloudFormation.
Point Kijiji-Guard at any IaC directory and get instant 
compliance findings mapped to the exact section of each law.

**Tier 2 — PaaS Platforms**
Vercel and Supabase — the platforms most African startups 
actually use. Connect your API token and scan your live 
projects in seconds.

**Tier 3 — Live Cloud APIs** *(coming soon)*
AWS, GCP, Azure, DigitalOcean. Connect your cloud account 
and scan live infrastructure directly — no IaC needed.

---

## Quick Start

### Requirements
- Python 3.9+
- Node.js 18+ (dashboard only)
- Windows users: use `py` instead of `python`

### 1. Clone and Install

```bash
git clone https://github.com/Kijiji-Guard/kijiji-guard.git
cd kijiji-guard

# Install all Python dependencies (recommended)
pip install -r cli/requirements.txt

# Windows users:
py -m pip install -r cli/requirements.txt

# Install (takes ~10 seconds)
pip install python-hcl2 rich typer pyyaml requests python-dotenv

# Windows:
py -m pip install python-hcl2 rich typer pyyaml requests python-dotenv
```

### 2. Scan a Terraform File

```bash
# Scan included sample against Nigeria NDPA 2023
python cli/main.py scan --target sample_startup.tf --country nigeria

# Windows:
py cli/main.py scan --target sample_startup.tf --country nigeria

# Scan against ALL 7 countries at once
py cli/main.py scan --target sample_startup.tf --country all

# Scan a directory of Terraform files
py cli/main.py scan --target ./infra --country kenya
```

### 3. Scan a Vercel Project

```bash
# Get your token at: vercel.com/account/tokens
py cli/main.py scan --target vercel --country nigeria \
  --vercel-token YOUR_TOKEN_HERE

# Or set environment variable and skip the flag
export VERCEL_TOKEN=your_token_here
py cli/main.py scan --target vercel --country nigeria
```

### 4. Scan a Supabase Project

```bash
# Get your token at: supabase.com/dashboard/account/tokens
py cli/main.py scan --target supabase --country kenya \
  --supabase-token YOUR_TOKEN_HERE

# Or set environment variable
export SUPABASE_ACCESS_TOKEN=your_token_here
py cli/main.py scan --target supabase --country ghana
```

### 5. Monitor Regulatory Updates (KijijiWatch)

```bash
# Monitor Nigerian regulatory updates (NDPC, CBN, NCC)
py cli/main.py watch --country nigeria

# Monitor all 7 countries
py cli/main.py watch --country all

# Get JSON output
py cli/main.py watch --country nigeria --output json

# Show all updates including previously seen ones
py cli/main.py watch --country nigeria --all
```

### 6. Launch the Web Dashboard

```bash
# Terminal 1 — start the API server
py -m uvicorn cli.api_server:app --reload --port 8000

# Terminal 2 — start the dashboard (from the project root)
npm install && npm run dev

# Open: http://localhost:5173
```

---

## All CLI Commands

### scan — Scan infrastructure for compliance

```bash
py cli/main.py scan [OPTIONS]

Options:
  --target TEXT         Path to .tf file, directory, or platform name
                        Values: file path | vercel | supabase | aws |
                                gcp | azure | digitalocean | auto
  --country TEXT        Country regulation to check against
                        Values: nigeria | ghana | kenya | rwanda |
                                cote-divoire | benin | egypt | all
                        Default: nigeria
  --output TEXT         Output format: console | json | html
                        Default: console
  --vercel-token TEXT   Vercel API token (for --target vercel)
  --supabase-token TEXT Supabase access token (for --target supabase)
  --aws-key TEXT        AWS Access Key ID (for --target aws)
  --aws-secret TEXT     AWS Secret Access Key (for --target aws)
  --aws-region TEXT     AWS region (default: af-south-1)
  --do-token TEXT       DigitalOcean API token

Examples:
  # IaC scan
  py cli/main.py scan --target sample_startup.tf --country nigeria
  py cli/main.py scan --target ./infra --country all
  py cli/main.py scan --target ./infra --country kenya --output json

  # Vercel scan
  py cli/main.py scan --target vercel --country nigeria \
    --vercel-token YOUR_TOKEN

  # Supabase scan
  py cli/main.py scan --target supabase --country ghana \
    --supabase-token YOUR_TOKEN

  # Scan a public GitHub repo (clone first)
  git clone https://github.com/terraform-aws-modules/terraform-aws-s3-bucket
  py cli/main.py scan --target terraform-aws-s3-bucket --country all
```

### watch — Monitor regulatory updates (KijijiWatch)

```bash
py cli/main.py watch [OPTIONS]

Options:
  --country TEXT   Country to monitor
                   Values: nigeria | ghana | kenya | rwanda |
                           cote-divoire | benin | egypt | all
                   Default: nigeria
  --all            Show all updates including previously seen ones
  --output TEXT    Output format: console | json
                   Default: console

Examples:
  py cli/main.py watch --country nigeria
  py cli/main.py watch --country all
  py cli/main.py watch --country egypt --output json
  py cli/main.py watch --country nigeria --all
```

---

## Example Output
```
┌──────────────────────────────────────────────────────────────────┐
│  Kijiji-Guard Compliance Scan                                    │
│  Target: terraform-aws-s3-bucket | Country: All | Scanners: iac  │
└──────────────────────────────────────────────────────────────────┘
Check ID      Name                                    Result  Regulation
──────────────────────────────────────────────────────────────────────
CKV_NGR_001   Data residency — non-African region     FAILED  NDPA §41
CKV_NGR_002   No data retention lifecycle rule        FAILED  NDPA §24
CKV_NGR_003   S3 encryption at rest not configured    FAILED  NDPA §34
CKV_NGR_004   No CloudTrail — breach detection        FAILED  NDPA §40
CKV_NGR_005   S3 bucket may allow public access       FAILED  NDPA §41
CKV_GHA_001   S3 encryption at rest not configured    FAILED  Ghana DPA §28
CKV_GHA_002   IAM policy has no wildcard actions      PASSED  Ghana DPA §22
CKV_KEN_003   Data outside Africa                     WARN    Kenya DPA §48
CKV_RWA_002   Strict data localisation violation      FAILED  Rwanda Art.50
CKV_RWA_003   No CloudTrail — 48hr breach impossible  FAILED  Rwanda Art.34
CKV_EGY_002   No CloudTrail — 72hr breach impossible  FAILED  Egypt PDPL Art.23
CKV_EGY_003   Potential cross-border data transfer    FAILED  Egypt PDPL Art.27
Summary: 7 passed · 26 failed · 2 warnings · Pass rate: 20.59%
Fix violations before your next compliance audit cycle.
```

---

## KijijiWatch Output
```
╔══════════════════════════════════════════════════════════╗
║  KijijiWatch — Regulatory Intelligence    🇳🇬 Nigeria    ║
║  3 updates found | 3 new                                 ║
╚══════════════════════════════════════════════════════════╝
Severity  Category        Authority  Title
──────────────────────────────────────────────────────────
HIGH      DEADLINE        NDPC       2025 DPCAR Audit Returns Due — 30 May 2026
HIGH      ENFORCEMENT     NDPC       1,368 Organizations Issued Compliance Notices
HIGH      INVESTIGATION   NDPC       NDPC Investigating Temu for NDPA Violations
HIGH: 3 items requiring immediate attention
Review these updates before your next audit cycle.
```

---

## Project Structure
```
kijiji-guard/
├── cli/                          # Python scanner engine
│   ├── main.py                   # CLI entry point (all commands)
│   ├── api_server.py             # FastAPI server for dashboard
│   ├── requirements.txt          # Python dependencies
│   ├── core/
│   │   ├── orchestrator.py       # Routes scans to correct adapter
│   │   ├── watcher.py            # KijijiWatch regulatory monitor
│   │   └── report.py             # Terminal, JSON, HTML output
│   └── adapters/
│       ├── iac/                  # IaC scanner (python-hcl2)
│       │   └── policies/         # Country policy classes
│       │       ├── nigeria.py    # 6 NDPA checks
│       │       ├── ghana.py      # 5 Ghana DPA checks
│       │       ├── kenya.py      # 6 Kenya DPA checks
│       │       ├── rwanda.py     # 5 Rwanda Law checks
│       │       ├── cote_divoire.py # 5 Loi 2013-450 checks
│       │       ├── benin.py      # 5 Loi 2017-20 checks
│       │       └── egypt.py      # 6 Egypt PDPL checks
│       ├── api/                  # Live cloud API scanners (coming soon)
│       │   ├── aws_adapter.py
│       │   ├── gcp_adapter.py
│       │   └── azure_adapter.py
│       ├── paas/                 # PaaS platform scanners
│       │   ├── vercel_adapter.py # 5 Vercel checks (functional)
│       │   └── supabase_adapter.py # 6 Supabase checks (functional)
│       └── watch/                # KijijiWatch country monitors
│           ├── nigeria.py        # NDPC + CBN + NCC
│           ├── ghana.py          # Ghana DPC
│           ├── kenya.py          # Kenya ODPC
│           ├── rwanda.py         # Rwanda NCSA
│           ├── egypt.py          # Egypt PDPC
│           ├── benin.py          # Bénin CRIET
│           └── cote_divoire.py   # Côte d'Ivoire ARTCI
├── src/                          # React + Vite web dashboard
│   └── components/
│       ├── Overview.tsx          # Compliance score + findings
│       ├── RunScan.tsx           # Scan form + live results
│       ├── Findings.tsx          # Filterable findings table
│       ├── Watch.tsx             # KijijiWatch alerts
│       ├── History.tsx           # Past scans
│       ├── Regulations.tsx       # Country regulation info
│       └── ExportReport.tsx      # Download JSON/HTML report
├── terraform/                    # Reference compliant IaC templates
│   └── main.tf
├── sample_startup.tf             # Demo non-compliant Terraform file
└── .env.example                  # Environment variable reference
```

---

## Environment Variables

Create a `.env` file in the root (see `.env.example`):

```bash
# Vercel
VERCEL_TOKEN=your_vercel_token_here

# Supabase
SUPABASE_ACCESS_TOKEN=your_supabase_token_here

# AWS (for live API scanning — coming soon)
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_DEFAULT_REGION=af-south-1

# GCP
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Azure
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# DigitalOcean
DIGITALOCEAN_TOKEN=your_do_token_here
```

---

## Roadmap

- [x] IaC scanning — Terraform/HCL (7 countries, 38 checks)
- [x] PaaS scanning — Vercel (5 checks) + Supabase (6 checks)
- [x] KijijiWatch — regulatory intelligence monitor
- [x] Web dashboard with compliance overview + export
- [x] HTML auditor report export
- [x] CLI credential flags (--vercel-token, --supabase-token etc)
- [ ] `pip install kijiji-guard` package release
- [ ] Live AWS/GCP/Azure API scanning
- [ ] GitHub Action for CI/CD compliance gates
- [ ] Docker image for zero-install usage
- [ ] South Africa POPIA support
- [ ] Senegal + Tanzania regulations
- [ ] French regulation summaries (Francophone West Africa)

---

## Contributing

We welcome contributions from African developers and security researchers.

**Priority areas:**
- GCP and Azure IaC policy checks
- New country regulations (South Africa POPIA, Senegal, Tanzania)
- PaaS adapters for Firebase, Render, Railway
- French translations of regulation summaries

See [docs/contributing.md](docs/contributing.md) to get started.

---

## Built for AfricaCyberFest 2026

Kijiji-Guard was built for the AfricaCyberFest 2026 Solutions Hackathon
Open Track — a sprint to build open-source security tools for African 
and global challenges.

**Track:** Open Track — Compliance Automation
**Event:** Africa CyberFest 2026, Lagos, Nigeria

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

Copyright (c) 2026 Kijiji-Guard Contributors

---

*Kijiji (Swahili) — "village." Security for the whole village.*
