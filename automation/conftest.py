"""
Shared pytest configuration and fixtures for the Storefront Testing Suite.

Environment values are read from environment variables so that the same tests
run against any group member's local Saleor instance without code changes.
Defaults match the standard saleor-platform docker configuration.
"""

import os

import pytest

DASHBOARD_URL = os.getenv("SALEOR_DASHBOARD_URL", "http://localhost:9000")
API_URL = os.getenv("SALEOR_API_URL", "http://localhost:8000/graphql/")
MAILPIT_URL = os.getenv("MAILPIT_URL", "http://localhost:8025")

STAFF_EMAIL = os.getenv("SALEOR_STAFF_EMAIL", "admin@example.com")
STAFF_PASSWORD = os.getenv("SALEOR_STAFF_PASSWORD", "admin")


@pytest.fixture(scope="session")
def dashboard_url():
    """Base URL of the Saleor staff Dashboard."""
    return DASHBOARD_URL


@pytest.fixture(scope="session")
def api_url():
    """URL of the Saleor GraphQL endpoint."""
    return API_URL


@pytest.fixture(scope="session")
def staff_credentials():
    """Seeded superuser credentials created by populatedb during setup."""
    return {"email": STAFF_EMAIL, "password": STAFF_PASSWORD}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Override the default Playwright context.

    ignore_https_errors is enabled because the local deployment is served over
    plain HTTP. The viewport is fixed so that Dashboard layout is consistent
    across group members' machines and screenshots are comparable.
    """
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1440, "height": 900},
    }
