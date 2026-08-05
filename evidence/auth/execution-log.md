# Authentication Workflow — Test Execution Log

Environment: Saleor 3.23 via Docker Compose (WSL2)
Dashboard: http://localhost:9000 | API: http://localhost:8000/graphql/ | Mailpit: http://localhost:8025
Tester: Molly Viau

---

## TC-AUTH-01 — Successful staff sign-in with valid credentials

**Executed:** 2026-08-04
**Status:** PASS

Sign-in request (operation `loginWithoutDetails`) returned HTTP 200 with a
`tokenCreate` payload containing a token and refreshToken, and an empty `errors`
array. Browser redirected to `/dashboard/home`. Returned `user` object confirmed
`admin@example.com` with `isStaff: true`. Eight subsequent authenticated
operations succeeded, confirming an established session.

**Evidence:**
- TC-AUTH-01_01_credentials-entered.png
- TC-AUTH-01_02_dashboard-loaded.png
- TC-AUTH-01_03_tokencreate-response.jpg

**Note:** Prior to execution, the PostgreSQL container was found exited while
other services ran; API requests failed with `[Errno -5]`. Resolved by restarting
db, then api and worker. Environment issue, not a defect. See report Section 8.4.

---

## TC-AUTH-02 — Sign-in rejected for invalid credentials

**Executed:** 2026-08-04
**Status:** PASS

Three variations covering equivalence classes EC2, EC3 and EC4.

**Variation A — incorrect password (EC2)**
Rejected. UI displayed "Your username and/or password are incorrect. Please try
again." `tokenCreate` returned HTTP 200 with `token: null`, `refreshToken: null`,
`user: null`, and one `AccountError`: `code: INVALID_CREDENTIALS`,
`field: "email"`, `message: "Please, enter valid credentials"`.

**Variation B — unregistered email (EC3)**
Rejected. UI message identical to Variation A. API response identical in both
structure and content — same error code, same field, same message. Neither layer
disclosed that the address was unregistered.

**Variation C — blank password (EC4)**
Submission blocked by browser-level field validation ("Please fill out this
field."). No requests recorded in the Network panel; no authentication attempt
reached the API.

No token was issued in any variation and no Dashboard content became accessible.

**Evidence:**
- TC-AUTH-02_01_variation-a-wrong-password.jpg
- TC-AUTH-02_02_variation-a-response.jpg
- TC-AUTH-02_03_variation-b-unregistered-email.jpg
- TC-AUTH-02_04_variation-c-blank-password.jpg

**Observations for exploratory session (ID 48):**
- Enumeration resistance holds at the API layer, not just the UI. Candidate for
  report Section 20.1 (Major Strengths).
- `field: "email"` is returned even when the password is the incorrect value.
  Consistent with not disclosing which credential failed, but reads as a
  mislabelled field on first inspection.
- Variation C confirms client-side validation only. Whether the server rejects an
  empty password is untested — would require a request issued directly against
  the GraphQL endpoint.
