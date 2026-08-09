# Exploratory Session 1 — Authentication

**Tester:** Molly
**Date:** 2026-08-08
**Build:** Saleor 3.23, local Docker Compose (Dashboard :9000, API :8000, Mailpit :8025)
**Time-box:** 75 minutes — Start 20:16 EDT, End 21:31 EDT
**Charter:** Explore how the authentication workflow handles unexpected input, interrupted flows, and boundary conditions outside the scripted test cases in Section 12.

Times are EDT and were reconciled against timestamps in the captured evidence (Celery worker logs and HTTP response headers are UTC, EDT + 4h).

| Time | Area | Action | Result | Interpretation | Tag | Evidence |
|---|---|---|---|---|---|---|
| 20:19 | Boundary | Reset form: set password to seeded `admin` value (5 chars) | Rejected — `PASSWORD_TOO_SHORT`, "This password is too short. It must contain at least 8 characters." | Same value authenticates successfully at sign-in | ODD / FOLLOW-UP | s1-01 |
| 20:26 | Boundary | Reset form: 7 characters, then 8 characters | 7 rejected; 8 accepted, `setPassword` returned token with empty errors array | Minimum length = 8, confirmed on both sides of the boundary | OK | s1-01, s1-02 |
| 20:31 | Boundary | Observed DevTools during short-password submit | Request fired; error returned in the `setPassword` response body | Validation is server-side (Django `AUTH_PASSWORD_VALIDATORS`), not a client-side check | OK | s1-01 |
| 20:19 | Reset | First reset request for `admin@example.com` | Worker dispatched `trigger_send_password_reset_notification` (0.209s) and `send_staff_password_reset_email_task`; email delivered | Baseline — reset path works | OK | s1-03, s1-04 |
| 20:25–20:44 | Reset | Four further reset requests for the same address | Success at 00:39 UTC (0.296s); failures at 00:25, 00:28, 00:44 UTC (~0.002s, no send task dispatched) | Suppression is time-based, not intermittent | ODD | s1-06, s1-10 |
| 20:38 | Reset | Confirmed staff account list via Django shell | `admin@example.com` present | Rules out an unresolved or mistyped address as the cause | OK | s1-06 |
| 20:52 | Reset | Traced source: `saleor/account/tasks.py` and `request_password_reset.py` | `clean_user()` sets `user = None` inside the lock window; `perform_mutation` passes `user_pk=None`; `tasks.py:32` returns at `if not user_pk` | Full causal chain identified | — | s1-05, s1-08, s1-09 |
| 20:52 | Reset | `RESET_PASSWORD_LOCK_TIME` read via Django shell | 900 seconds (15 minutes) | Matches all five observed request timings | DEFECT CANDIDATE | s1-07 |
| 20:48 | Session | Signed out of window A; checked window B (same account, separate session) | Window B still fully functional — navigates and loads data | Sign-out does not invalidate concurrent sessions | ODD / FOLLOW-UP | — |
| 20:50 | Session | Signed out, navigated directly to `/orders/` | Clean redirect to sign-in | OK | — |
| 20:50 | Session | Looked for a self-service password change in the Dashboard | None available for a staff user's own account — reset-by-email only | The reset path is the sole route for credential rotation | ODD | — |
| 20:51 | Errors | `admin@example.com` + incorrect password | 200, `INVALID_CREDENTIALS`, field `email`, "Please, enter valid credentials", 689 B | OK | s1-11, s1-12 |
| 20:55 | Errors | `nobody@example.com` + arbitrary password | Identical status, code, field, message and payload size | No user enumeration via the sign-in path | OK | s1-13, s1-14 |
| 21:03 | Malformed | `"  admin@example.com  "` (padded) + correct password | Request fired, 200, `INVALID_CREDENTIALS` | Whitespace is not trimmed; the error wrongly implies bad credentials | ODD / FOLLOW-UP | s1-15 |
| 21:04 | Malformed | `ADMIN@EXAMPLE.COM` + correct password | Signed in successfully | Email lookup is case-insensitive | OK | s1-16 |
| 21:06 | Malformed | Both fields empty, Sign In clicked | No request fired | Blocked client-side | OK | s1-17 |
| 21:11 | Malformed | Password of ~90 characters | Request fired, 200, `INVALID_CREDENTIALS` | No client-side length cap on sign-in; the API handles it | OK | s1-18 |

## Incidental corroboration

The password reset email captured in `s1-04` states that the link expires in 24 hours. The configured `PASSWORD_RESET_TIMEOUT` is three days. This independently corroborates BUG-104, which was raised separately, and the screenshot may be cited in Section 16.

## Unresolved at time-box expiry

- Per-request response times for existing versus non-existent accounts were not measured. The DevTools "Finish" figure is cumulative across the request panel, so a timing side-channel is neither confirmed nor ruled out.
- Token reuse and superseded-token behaviour was planned but not completed. The 15-minute reset lock made repeated token generation impractical within the time-box.

All evidence files referenced above are stored in evidence/exploratory/ in the project repository, named exploratory-s1-01 through exploratory-s1-18.
