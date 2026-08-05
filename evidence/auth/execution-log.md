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
