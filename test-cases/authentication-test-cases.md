# Authentication — Detailed Test Cases

**Workflow:** Authentication (staff sign-in and password recovery)
**Owner:** Molly Viau (A00338002)
**Application under test:** Saleor 3.23, deployed locally via `saleor-platform` Docker Compose
**Dashboard:** http://localhost:9000 · **GraphQL API:** http://localhost:8000/graphql/ · **Mailpit:** http://localhost:8025
**Report reference:** Section 12.0.2 – 12.2.2 of the CMP1979 capstone report

---

## Workflow Under Test

The authentication workflow covers how a staff user gains and regains access to the Saleor Dashboard. Two related paths are in scope:

- **Sign-in** — a staff user authenticates against the Dashboard using an email address and password. The Dashboard exchanges these for a JWT via the `tokenCreate` GraphQL mutation.
- **Password recovery** — a staff user who cannot sign in requests a reset link. The Dashboard calls `requestPasswordReset`, Saleor generates a single-use token and emails a link, and the user sets a new password through `setPassword`.

Password recovery is included deliberately. It crosses four components — Dashboard UI, GraphQL API, the outbound mail path, and the Mailpit inbox — which produces meaningfully stronger evidence than a sign-in alone.

## Black-Box Technique Used

**Equivalence partitioning.** Credential submission has an effectively unlimited input space, so inputs were divided into classes expected to be treated identically by the system, and one representative value was selected from each class. This keeps the test count proportionate while ensuring each distinct system behaviour is exercised at least once.

A secondary consideration is token state validity in the recovery path. A reset token is not a simple input value — it is valid or invalid depending on elapsed time and on account activity that occurred after the token was issued. This is treated as its own partition set.

### Equivalence Classes Identified

| Class | Input condition | Representative data | Expected system behaviour |
|---|---|---|---|
| EC1 | Registered email, correct password | `admin@example.com` / `admin` | Authentication succeeds; token issued |
| EC2 | Registered email, incorrect password | `admin@example.com` / `WrongPass123` | Authentication rejected; no token issued |
| EC3 | Unregistered email, any password | `noone@example.com` / anything | Authentication rejected; no token issued |
| EC4 | Empty required field | `admin@example.com` / (blank) | Client-side validation blocks submission |
| EC5 | Unused reset token, within validity window | Fresh token from Mailpit | Password is updated successfully |
| EC6 | Token invalidated by later account activity | Token issued, then user signs in | Token rejected — not covered, see note below |

TC-AUTH-01 through TC-AUTH-03 provide coverage of EC1, EC2, EC3, EC4 and EC5.

EC6 was carried into the time-boxed exploratory session recorded in Section 11 of the report (Azure DevOps work item 48), on the basis that its expected behaviour is not documented in the application interface and required investigation before an expected result could be stated with confidence. It was not resolved within that session: the 900-second reset lock window (`RESET_PASSWORD_LOCK_TIME`) limits how frequently tokens can be generated, which left insufficient time to test supersession and single-use enforcement. **EC6 therefore remains uncovered** and is carried forward as follow-up item 3 in Section 11.4.

---

## TC-AUTH-01 — Successful staff sign-in with valid credentials

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-01 |
| **Title** | Successful staff sign-in with valid credentials |
| **Purpose** | Confirm that a registered staff account with a correct password is authenticated and granted access to the Dashboard. Covers EC1 and establishes the baseline that all negative sign-in cases are measured against. |
| **Preconditions** | All services confirmed running via `docker compose ps`; API responds at http://localhost:8000/graphql/. Dashboard reachable at http://localhost:9000. The seeded staff account `admin@example.com` exists and is active. No active session — browser in a clean state or a private window. |
| **Test Data** | Email: `admin@example.com` · Password: `admin` |
| **Status** | **PASS** |

**Steps**

1. Navigate to http://localhost:9000.
2. Confirm the sign-in form is displayed with email and password fields.
3. Enter `admin@example.com` in the email field.
4. Enter `admin` in the password field.
5. Submit the form.
6. Observe the resulting page and the browser network activity for the `tokenCreate` request.

**Expected Result**

The sign-in request (operation `loginWithoutDetails`) returns a `tokenCreate` payload containing a token with an empty `errors` array. The browser is redirected away from the sign-in form to the Dashboard home view.

**Actual Result**

The sign-in request (operation `loginWithoutDetails`) returned HTTP 200 with a `tokenCreate` payload containing both a `token` and a `refreshToken`, and an empty `errors` array. The browser was redirected from the sign-in form to http://localhost:9000/dashboard/home, where the Dashboard home view loaded. The returned `user` object confirmed the authenticated identity as `admin@example.com` with `isStaff: true`. No error message was displayed at any point during the sign-in. Following authentication, the Dashboard issued a further eight authenticated GraphQL operations — including `shopInfo`, `userDetails`, `baseChannels`, and `extensionList` — confirming that a valid session was established rather than a redirect occurring without authentication.

**Evidence**

| File | Report figure |
|---|---|
| `evidence/auth/TC-AUTH-01_01_credentials-entered.jpg` | Figure 12.4 |
| `evidence/auth/TC-AUTH-01_02_dashboard-loaded.jpg` | Figure 12.5 |
| `evidence/auth/TC-AUTH-01_03_tokencreate-response.jpg` | Figure 12.6 |

---

## TC-AUTH-02 — Sign-in rejected for invalid credentials

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-02 |
| **Title** | Sign-in rejected for invalid credentials |
| **Purpose** | Confirm that authentication fails for a wrong password, for an unregistered email address, and that a missing required field is blocked before submission. Covers EC2, EC3 and EC4. Also checks that the failure message does not disclose whether an email address is registered, which is a common account-enumeration weakness. |
| **Preconditions** | All services confirmed running via `docker compose ps`; Dashboard reachable at http://localhost:9000. No active session. The address `noone@example.com` is confirmed not to exist as a staff or customer account. |
| **Test Data** | Variation A (EC2) — `admin@example.com` / `WrongPass123`<br>Variation B (EC3) — `noone@example.com` / `WrongPass123`<br>Variation C (EC4) — `admin@example.com` / (left blank) |
| **Status** | **PASS** |

**Steps**

1. Navigate to http://localhost:9000.
2. Enter the Variation A email and password.
3. Submit the form and record the exact message displayed.
4. Confirm the browser remains on the sign-in form and no token was issued.
5. Clear both fields and repeat steps 2–4 using Variation B.
6. Compare the two messages recorded and note whether they are identical.
7. Clear both fields, enter the Variation C email, leave the password blank, and attempt to submit.

**Expected Result**

- **Variation A:** authentication is rejected, an error message is shown, and the user remains on the sign-in form.
- **Variation B:** authentication is rejected with a message identical to Variation A — the response does not reveal that the address is unregistered.
- **Variation C:** submission is blocked and the empty required field is flagged; no authentication request is sent.

In all three variations no token is issued and no Dashboard content becomes accessible.

**Actual Result**

- **Variation A (EC2):** Authentication was rejected. The Dashboard displayed: "Your username and/or password are incorrect. Please try again." The `tokenCreate` response returned HTTP 200 with `token: null` and `refreshToken: null`, and an `errors` array containing a single `AccountError` with `code: "INVALID_CREDENTIALS"`, `field: "email"`, and `message: "Please, enter valid credentials"`. The `user` field was `null` and the browser remained on the sign-in form.
- **Variation B (EC3):** Authentication was rejected. The message displayed was identical to Variation A. The `tokenCreate` response was also identical in structure and content — the same `INVALID_CREDENTIALS` code, the same `field: "email"`, and the same message. Neither the interface nor the API response indicated that the address was unregistered.
- **Variation C (EC4):** Submission was blocked by browser-level field validation, which displayed "Please fill out this field." on the empty password input. The Network panel recorded no requests at all, confirming that no authentication attempt reached the API.

In all three variations no token was issued and no Dashboard content became accessible.

**Evidence**

| File | Report figure |
|---|---|
| `evidence/auth/TC-AUTH-02_01_variation-a-wrong-password.jpg` | Figure 12.7 |
| `evidence/auth/TC-AUTH-02_02_variation-a-response.jpg` | Figure 12.8 |
| `evidence/auth/TC-AUTH-02_03_variation-b-unregistered-email.jpg` | Figure 12.9 |
| `evidence/auth/TC-AUTH-02_04_variation-c-blank-password.jpg` | Figure 12.10 |

---

## TC-AUTH-03 — End-to-end password reset via emailed token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-03 |
| **Title** | End-to-end password reset via emailed token |
| **Purpose** | Confirm that a staff user who cannot sign in can recover access: that a reset request generates and delivers an email containing a valid token, that the token allows a new password to be set, and that the new password then works while the old one does not. Covers EC5 and verifies the full Dashboard–API–mail–Dashboard path. |
| **Preconditions** | All services confirmed running via `docker compose ps`; Dashboard reachable at http://localhost:9000. Mailpit reachable at http://localhost:8025 and its inbox cleared. The staff account `admin@example.com` exists and its current password is known. No active session — performed in a private window so that no sign-in occurs between token generation and token use. |
| **Test Data** | Account: `admin@example.com` · Current password: `admin` · New password: `NewPass!2026` |
| **Status** | **PASS** |

**Steps**

1. Navigate to http://localhost:9000 and select the password reset option on the sign-in form.
2. Enter `admin@example.com` and submit the reset request.
3. Record the confirmation message shown by the Dashboard.
4. Open http://localhost:8025 and confirm a reset email has arrived for that address.
5. Open the email and extract the reset link, noting the `email` and `token` parameters it carries.
6. Open the reset link in the same private window.
7. Enter `NewPass!2026` as the new password and submit.
8. Return to http://localhost:9000 and sign in with `admin@example.com` and `NewPass!2026`.
9. Sign out, then attempt to sign in once more using the old password `admin`.
10. Restore the account password to `admin` so that TC-AUTH-01 and TC-AUTH-02 remain repeatable.

**Expected Result**

- **Step 3:** the Dashboard confirms the request without disclosing whether the address is registered.
- **Step 4:** exactly one reset email is delivered to Mailpit, addressed to `admin@example.com`.
- **Step 5:** the link contains both an `email` parameter and a single-use `token` parameter.
- **Step 7:** the new password is accepted and confirmed by the `setPassword` mutation returning no errors.
- **Step 8:** sign-in with the new password succeeds and the Dashboard home view loads.
- **Step 9:** sign-in with the old password is rejected.

**Actual Result**

- **Step 3:** The Dashboard navigated to `/dashboard/reset-password/success/` and displayed: "Success! In a few minutes you'll receive a message with instructions on how to reset your password." The `requestPasswordReset` mutation returned HTTP 200 with an empty `errors` array.
- **Step 4:** One reset email was delivered to Mailpit, from `noreply@example.com` to `admin@example.com`, with the subject "Reset your Saleor password". Delivery took approximately three minutes from the request.
- **Step 5:** The email contained a "Reset my password" action linking to http://localhost:9000/dashboard/new-password/, carrying both an `email` parameter and a `token` parameter. The message stated that the link expires in 24 hours.
- **Step 7:** The new password was accepted. The `setPassword` mutation returned an empty `errors` array along with a new `token` and `refreshToken`, authenticating the session immediately.
- **Step 8:** Sign-in with the new password succeeded and the Dashboard home view loaded, with the authenticated account shown as `admin@example.com`.
- **Step 9:** Sign-in with the previous password was rejected, returning `INVALID_CREDENTIALS` with the message "Please, enter valid credentials" — confirming the original password was replaced rather than a second valid credential being added.
- **Step 10:** The account password was restored to its original value to preserve the environment state documented in TC-AUTH-01 and TC-AUTH-02.

**Note on Figure 12.14:** the Status 451 shown in that view originates from Mailpit's link-checking feature, which declines to scan private and reserved addresses such as `localhost`. It does not indicate a failure of the link itself, which resolved correctly when opened.

**Defect raised:** the 24-hour expiry stated in the reset email does not match the configured `PASSWORD_RESET_TIMEOUT` of 259,200 seconds (3 days). Recorded as **BUG-104** — see `evidence/defects/` and Section 16.2 of the report.

**Evidence**

| File | Report figure |
|---|---|
| `evidence/auth/TC-AUTH-03_01_reset-requested.jpg` | Figure 12.11 |
| `evidence/auth/TC-AUTH-03_02_mailpit-reset-email.jpg` | Figure 12.12 |
| `evidence/auth/TC-AUTH-03_03_reset-email-body.jpg` | Figure 12.13 |
| `evidence/auth/TC-AUTH-03_04_reset-link-parameters.jpg` | Figure 12.14 |
| `evidence/auth/TC-AUTH-03_05_setpassword-response.jpg` | Figure 12.15 |
| `evidence/auth/TC-AUTH-03_06_new-password-signin.jpg` | Figure 12.16 |
| `evidence/auth/TC-AUTH-03_07_old-password-rejected.jpg` | Figure 12.17 |

---

## Summary

| Test case | Equivalence classes | Status |
|---|---|---|
| TC-AUTH-01 | EC1 | PASS |
| TC-AUTH-02 | EC2, EC3, EC4 | PASS |
| TC-AUTH-03 | EC5 | PASS |
| — | EC6 | Not covered — carried forward as follow-up (Section 11.4) |

**Related automated coverage:** `automation/ui/test_auth_login.py`
**Related defects:** BUG-104 (password reset email states incorrect expiry period)
**Execution log:** `evidence/auth/execution-log.md`
