"""
Automated Test 1 - Staff sign-in to the Saleor Dashboard (UI level).

Owner: Molly Viau
Workflow: Authentication
Traces to: TC-AUTH-01 (valid credentials), TC-AUTH-02 Variation A (wrong password)

This test exercises visible application behaviour through the browser, and
satisfies the "test of visible application behaviour" half of the required
automation mix.

Requires a running Saleor instance. Marked `live` so that it is excluded from
the continuous integration run, which cannot stand up the full stack.

Run locally with:
    pytest automation/ui --headed
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.live


def _sign_in(page: Page, url: str, email: str, password: str) -> None:
    """Fill and submit the Dashboard sign-in form."""
    page.goto(url)
    page.get_by_label(re.compile("email", re.IGNORECASE)).fill(email)
    page.get_by_label(re.compile("password", re.IGNORECASE)).fill(password)
    page.get_by_role("button", name=re.compile("sign in", re.IGNORECASE)).click()


def test_login_valid_credentials(page: Page, dashboard_url, staff_credentials):
    """
    TC-AUTH-01 - a registered staff account with the correct password is
    authenticated and lands on the Dashboard home view.

    Asserts on the resulting URL and on an authenticated Dashboard element,
    rather than on the redirect alone, so that a redirect occurring without a
    valid session would still fail the test.
    """
    _sign_in(
        page,
        dashboard_url,
        staff_credentials["email"],
        staff_credentials["password"],
    )

    expect(page).to_have_url(re.compile(r"/dashboard/home"), timeout=15000)
    expect(page.get_by_text(staff_credentials["email"])).to_be_visible(timeout=15000)


def test_login_rejected_wrong_password(page: Page, dashboard_url, staff_credentials):
    """
    TC-AUTH-02 Variation A (equivalence class EC2) - a registered email with an
    incorrect password is rejected and the user remains on the sign-in form.
    """
    _sign_in(
        page,
        dashboard_url,
        staff_credentials["email"],
        "WrongPass123",
    )

    expect(page.get_by_text(re.compile("incorrect", re.IGNORECASE))).to_be_visible(
        timeout=15000
    )
    expect(page).not_to_have_url(re.compile(r"/dashboard/home"))
