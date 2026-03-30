# Kijiji-Guard 🛡️
### Securing Africa's Next Unicorns without the Dollar-Denominated Security Tax.

Kijiji-Guard is an indigenous, open-source security framework designed for African startups to automate compliance with the **Nigeria Data Protection Act (NDPA) 2023** and **NDPC GAID 2025**.

In the rapidly evolving African tech ecosystem, security is often seen as a "Dollar-Denominated Security Tax"—expensive, foreign-made tools that don't understand the local regulatory landscape. Kijiji-Guard changes that. By leveraging powerful open-source engines like **Checkov**, we provide a "Sovereign Security" layer that is cost-effective, high-performing, and legally compliant within the Nigerian context.

## Why Kijiji-Guard?
- **NDPA-First Policies:** Custom Checkov policies specifically mapped to Sections 24, 34, and 41-43 of the NDPA 2023.
- **Sovereign Security:** Avoid expensive subscriptions to foreign security platforms. Own your compliance.
- **Unicorn-Ready:** Designed for the scale and speed of Africa's fastest-growing startups.

## Custom NDPA Checks (MVP)
- **CKV_NGR_001 (Data Residency):** Ensures data stays in "Adequate Protection" zones (e.g., `af-south-1`). (NDPA Section 41)
- **CKV_NGR_002 (Retention Enforcement):** Enforces storage limitation principles via S3 lifecycle rules. (NDPA Section 24)
- **CKV_NGR_003 (Encryption at Rest):** Mandates high-grade encryption (AES256/KMS) for all sensitive data. (NDPA Section 34)

## Getting Started
1. **Install Kijiji-Guard:** `pip install typer rich checkov pyyaml`
2. **Initialize:** `python main.py init`
3. **Run the Kijiji-Scan:** `python main.py scan sample_startup.tf`
4. **Review the Reference Architecture:** Check out `sample_startup.tf` for a compliant starting point.

## March 2026 NDPC Audit Cycle
The NDPC has mandated that all data controllers and processors must undergo a compliance audit by March 2026. Kijiji-Guard helps you automate the evidence gathering and security validation required for this cycle.

## How to Contribute 
We welcome contributions from the Google Developer Group (GDG) and Cybersecurity community!
- Add policies for GCP and Azure.
- Improve the CLI report output.
- Create a web-based dashboard for scan history.

---
*Kijiji-Guard: Protecting Africa's Next Unicorn.*
