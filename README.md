# storefront-testing-suite

Software testing capstone project for CMP1979 – Modern Software Development, Cambrian College.

**Application under test:** Saleor 3.23 — an open-source headless e-commerce platform.

---

## Group Members

| Name | Student ID | Role |
|---|---|---|
| Molly Viau | A00338002 | Test Automation and Infrastructure |
| Van Trinh Nguyen | A00316394 | Test Strategy and Planning |
| Rishabh Bhutani | A00244270 | Requirements and Quality Analysis |

Submitted to Professor Shashank Erukulla.

---

## Project Summary

This project is a focused testing engagement against a locally deployed instance of Saleor 3.23. Rather than attempting broad coverage of a large platform, the group selected three workflows that together form the core commercial path — a user must be able to authenticate, locate a product, and complete a purchase — and tested those in depth.

The work combines manual test case execution, exploratory testing, black-box and white-box techniques, static analysis, defect investigation, and automated testing at both the user-interface and API levels.

### Selected Workflows

| Workflow | Owner | Coverage |
|---|---|---|
| Authentication | Molly Viau | Staff sign-in, session handling, and the password reset flow including email delivery and token validation |
| Product Catalog and Search | Van Trinh Nguyen | Product listing and retrieval, keyword search, and filter behaviour through the GraphQL API and Dashboard |
| Checkout and Order Lifecycle | Rishabh Bhutani | Draft order creation, payment gating, fulfilment, and the states an order moves through |

---

## Setup

Full environment setup instructions, including WSL 2 and Docker configuration for Windows hosts, are in [SETUP.md](SETUP.md).

In brief, the application under test is deployed using the official `saleor-platform` Docker configuration, which is cloned as a sibling directory to this repository and is not committed to it.

Once running, the deployment exposes:

| Service | URL |
|---|---|
| Core API (GraphQL) | http://localhost:8000/graphql/ |
| Staff Dashboard | http://localhost:9000 |
| Mailpit (email capture) | http://localhost:8025 |
| Jaeger (request tracing) | http://localhost:16686 |

Sample data and a superuser account are created with:

```bash
docker compose run --rm api python3 manage.py populatedb --createsuperuser
```

---

## Running the Automated Tests

The automated tests require a running Saleor instance. From the repository root:

```bash
cd automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Then run all tests:

```bash
pytest
```

Or run a single level:

```bash
pytest ui/       # user-interface tests (Playwright)
pytest api/      # API tests (GraphQL)
```

To watch the browser drive the interface rather than running headless:

```bash
pytest ui/ --headed
```

Environment values are read from environment variables and default to the standard local deployment, so no code changes are needed to run against a different instance:

| Variable | Default |
|---|---|
| `SALEOR_DASHBOARD_URL` | `http://localhost:9000` |
| `SALEOR_API_URL` | `http://localhost:8000/graphql/` |
| `SALEOR_STAFF_EMAIL` | `admin@example.com` |
| `SALEOR_STAFF_PASSWORD` | `admin` |

Note that Python 3.14 is not compatible with the `greenlet` dependency required by Playwright. Use Python 3.12 or 3.13.

---

## Automated Quality Check

A GitHub Actions workflow at `.github/workflows/quality-check.yml` runs on every push and pull request to `main`. It performs Ruff linting, a formatting check, and pytest collection to confirm every test file imports cleanly.

The workflow does not execute the tests themselves. Doing so would require standing up the full Saleor stack — Core API, PostgreSQL, Valkey, and the Celery worker — for every run. Tests are executed locally instead, with their output committed to `evidence/`.

---

## Key Findings

Detailed analysis of each finding is in the Word report. In summary:

| ID | Workflow | Summary |
|---|---|---|
| BUG-66 | Product Catalog and Search | Clearing the required Product Name field and saving returns a success notification, but the empty value is not persisted. |
| BUG-67 | Checkout and Order Lifecycle | The Mark Order as Paid dialogue accepts an empty transaction reference, allowing a manual payment to be recorded with no traceable reference. |
| BUG-104 | Authentication | The password reset email states the link expires in 24 hours, while the configured `PASSWORD_RESET_TIMEOUT` is three days. |
| CR-1 | Authentication | `clean_user()` returns `None` for three distinct conditions, so a reset request suppressed by the lock window is indistinguishable from a delivered one. |
| CR-2 | Checkout and Order Lifecycle | `clean_mark_order_as_paid()` guards against duplicate manual payments, but does not require an attributable transaction reference. |

A recurring pattern across two workflows is that an operation reports success to the user when the underlying action did not take effect. This is discussed in the final quality evaluation.

Supporting evidence for each finding is committed under `evidence/`.

---

## Repository Structure

```
automation/            Automated tests
  ui/                  User-interface tests (Playwright)
  api/                 API tests (GraphQL)
  conftest.py          Shared fixtures and environment configuration
  pytest.ini           Test runner configuration
  requirements.txt     Test dependencies
evidence/              Test execution output and static analysis results
  exploratory/         Exploratory session notes and screenshots
  defects/             Defect investigation evidence
  auth/                Authentication test evidence
  catalog/             Product and catalog test evidence
  automation/          Automation evidence
models/                State transition diagram
test-cases/            Manual and API test cases
test-data/             Supporting test data
.github/workflows/     Automated quality check
```

---

## Tools

| Tool | Purpose |
|---|---|
| Playwright | Browser automation for user-interface tests |
| pytest | Test runner |
| Ruff | Static analysis and formatting |
| Docker Desktop / Docker Compose | Container runtime for the application under test |
| WSL 2 | Linux compatibility layer on Windows hosts |
| GraphQL Playground | Manual API exploration |
| Mailpit | Outbound email capture |
| Jaeger | Request tracing during defect investigation |
| GitHub Actions | Automated quality check |
| Azure DevOps Boards | Work item tracking and defect logging |

---

## Project Links

| Deliverable | Link |
|---|---|
| Word report | https://mycambrian-my.sharepoint.com/:w:/r/personal/a00338002_mycambrian_ca/Documents/CMP1979%20Capstone%20Report%20-%20Storefront%20Testing%20Suite.docx?d=w9c8f564406ff44219dc7cbf84ba27912&csf=1&web=1&e=0QYs4G |
| Azure DevOps board | https://dev.azure.com/storefront-testing-suite/Storefront%20Testing%20Suite |

---

## Course

CMP1979 – Modern Software Development
Capstone Project, Cambrian College, 2026
