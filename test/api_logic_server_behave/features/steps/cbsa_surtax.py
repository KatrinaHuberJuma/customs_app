"""
Behave step definitions for CBSA Steel Derivative Goods Surtax tests.

Tests cover:
- Surtax applicability based on ship_date >= 2025-12-26 and country surtax flag
- Line item calculations (customs_value, duty, surtax, PST/HST, total)
- Order roll-up totals from line items
- Constraints (ship date, quantity, unit price)

Convention (matching nw_sample):
  * When steps call test_utils.prt(msg, scenario_name) BEFORE the API call
    - This tells the server to route its logic trace to
      logs/scenario_logic_logs/<scenario_name>.log
  * Then steps verify specific logic-trace strings in that log file using
    test_utils.does_file_contain(), confirming the rules engine fired correctly
"""
from behave import given, when, then
import requests
import json
import uuid
from pathlib import Path
import test_utils

SERVER = "http://localhost:5656"
API = f"{SERVER}/api"
HEADERS = {"Content-Type": "application/vnd.api+json"}

# Absolute path to the scenario logic log directory (same convention as nw_sample)
_steps_dir = Path(__file__).parent
_behave_dir = _steps_dir.parent.parent   # .../test/api_logic_server_behave
logic_logs_dir = str(_behave_dir / "logs" / "scenario_logic_logs")

# ---------------------------------------------------------------------------
# Reference data lookups (by name)
# ---------------------------------------------------------------------------

COUNTRY_CODE_MAP = {
    "Germany": "DE",
    "United States": "US",
    "Japan": "JP",
    "China": "CN",
    "Mexico": "MX",
    "Canada": "CA",
}

PROVINCE_CODE_MAP = {
    "Ontario": "ON",
    "British Columbia": "BC",
    "Quebec": "QC",
    "Alberta": "AB",
}


def get_truncated_scenario_name(scenario_name: str) -> str:
    """Truncate to 25 chars and replace spaces/parens with underscores.
    Matches nw_sample convention for log file names."""
    trunc = scenario_name
    if trunc is not None and len(trunc) >= 26:
        trunc = scenario_name[0:25]
    trunc = trunc.replace(" ", "_").replace("(", "_").replace(")", "_")
    return trunc


def logic_log_file(scenario_name: str) -> str:
    return f'{logic_logs_dir}/{get_truncated_scenario_name(scenario_name)}.log'


def _get_country_id(country_name: str) -> int:
    iso = COUNTRY_CODE_MAP[country_name]
    r = requests.get(f"{API}/CountryOrigin/", params={"filter[country_code]": iso})
    r.raise_for_status()
    data = r.json()["data"]
    assert data, f"Country not found: {country_name} ({iso})"
    return int(data[0]["id"])


def _get_province_id(province_name: str) -> int:
    iso = PROVINCE_CODE_MAP[province_name]
    r = requests.get(f"{API}/ProvinceTaxRate/", params={"filter[province_code]": iso})
    r.raise_for_status()
    data = r.json()["data"]
    assert data, f"Province not found: {province_name} ({iso})"
    return int(data[0]["id"])


def _get_hs_code_id(hs_code: str) -> int:
    r = requests.get(f"{API}/HSCodeRate/", params={"filter[hs_code]": hs_code})
    r.raise_for_status()
    data = r.json()["data"]
    assert data, f"HS Code not found: {hs_code}"
    return int(data[0]["id"])


def _get_order(order_id: int) -> dict:
    r = requests.get(f"{API}/SurtaxOrder/{order_id}/")
    r.raise_for_status()
    return r.json()["data"]["attributes"]


def _get_line_item(line_item_id: int) -> dict:
    r = requests.get(f"{API}/SurtaxLineItem/{line_item_id}/")
    r.raise_for_status()
    return r.json()["data"]["attributes"]


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("the CBSA surtax database is loaded")
def step_database_loaded(context):
    """Verify server is reachable."""
    r = requests.get(f"{API}/SurtaxOrder/")
    assert r.status_code == 200, f"Server not reachable: {r.status_code}"


@given("a SurtaxOrder for {country} to {province} with ship_date {ship_date} and entry_date {entry_date}")
def step_create_order(context, country, province, ship_date, entry_date):
    """Create a new SurtaxOrder; opens a per-scenario logic log via prt."""
    country_id = _get_country_id(country)
    province_id = _get_province_id(province)

    # Open the per-scenario logic log BEFORE the first API call.
    # The server will route all subsequent logic_logger output to this file.
    # IMPORTANT: prt(msg, scenario_name) must only be called ONCE per scenario;
    # calling it again wipes the file (server removes and recreates the handler).
    scenario_name = get_truncated_scenario_name(context.scenario.name)
    context.scenario_name = scenario_name
    test_utils.prt(f'\n\n\n{scenario_name} - starting CBSA surtax test\n\n', scenario_name)

    unique_suffix = uuid.uuid4().hex[:8]
    order_number = f"TEST-{country[:2].upper()}-{unique_suffix}"

    payload = {
        "data": {
            "type": "SurtaxOrder",
            "attributes": {
                "order_number": order_number,
                "entry_date": entry_date,
                "ship_date": ship_date,
                "country_origin_id": country_id,
                "province_code_id": province_id,
                "importer_name": f"Behave Test - {country}",
            }
        }
    }

    r = requests.post(f"{API}/SurtaxOrder/", headers=HEADERS, data=json.dumps(payload))
    context.order_create_status = r.status_code
    context.order_create_text = r.text

    if r.status_code in (200, 201):
        context.order_id = int(r.json()["data"]["id"])
        context.order_rejected = False
        context.line_item_count = 0
    else:
        context.order_id = None
        context.order_rejected = True
        context.order_error_text = r.text
        # Do NOT assert here - constraint scenarios verify rejection in Then steps


@when("a line item is added with hs_code {hs_code} quantity {quantity} and unit_price {unit_price}")
def step_add_line_item(context, hs_code, quantity, unit_price):
    """Add the first (or only) line item; prt call routes logic to scenario log."""
    assert context.order_id, \
        f"No order created (order POST failed: {getattr(context, 'order_error_text', 'unknown')})"
    hs_id = _get_hs_code_id(hs_code)
    qty = float(quantity)
    price = float(unit_price)
    line_num = getattr(context, "line_item_count", 0) + 1
    context.line_item_count = line_num

    payload = {
        "data": {
            "type": "SurtaxLineItem",
            "attributes": {
                "surtax_order_id": context.order_id,
                "hs_code_id": hs_id,
                "line_number": line_num,
                "quantity": qty,
                "unit_price": price,
                "description": f"Behave test item - {hs_code}",
            }
        }
    }

    r = requests.post(f"{API}/SurtaxLineItem/", headers=HEADERS, data=json.dumps(payload))
    context.line_item_create_status = r.status_code
    context.line_item_create_text = r.text

    if r.status_code in (200, 201):
        context.line_item_id = int(r.json()["data"]["id"])
        context.line_item_rejected = False
        # No prt here - would wipe the logic log
    else:
        context.line_item_id = None
        context.line_item_rejected = True
        context.line_item_error_text = r.text


@when("a second line item is added with hs_code {hs_code} quantity {quantity} and unit_price {unit_price}")
def step_add_second_line_item(context, hs_code, quantity, unit_price):
    """Add a second line item to the current order."""
    step_add_line_item(context, hs_code, quantity, unit_price)


# ---------------------------------------------------------------------------
# Then steps - line item field assertions
# ---------------------------------------------------------------------------

@then("the line item {field} is {expected_value}")
def step_assert_line_item_field(context, field, expected_value):
    """Assert a calculated field on the most recently created line item."""
    assert not getattr(context, "line_item_rejected", False), \
        f"Line item was rejected: {getattr(context, 'line_item_error_text', '')}"

    attrs = _get_line_item(context.line_item_id)
    actual = attrs.get(field)

    try:
        assert abs(float(actual) - float(expected_value)) < 0.01, \
            f"Line item {field}: expected {expected_value}, got {actual}"
    except (TypeError, ValueError):
        assert str(actual) == expected_value, \
            f"Line item {field}: expected {expected_value}, got {actual}"

    # No prt call here - would wipe the logic log written by the server


@then("the line item is rejected with error {error_msg}")
def step_line_item_rejected(context, error_msg):
    """Assert line item creation was rejected with a specific error."""
    assert getattr(context, "line_item_rejected", False), \
        f"Expected line item rejection but it succeeded (id={context.line_item_id})"
    assert error_msg in context.line_item_error_text, \
        f"Expected error '{error_msg}' not found in: {context.line_item_error_text}"
    # No prt call here - would wipe the logic log


# ---------------------------------------------------------------------------
# Then steps - order field assertions
# ---------------------------------------------------------------------------

@then("the order {field} is {expected_value}")
def step_assert_order_field(context, field, expected_value):
    """Assert a field on the current order after line item roll-up."""
    assert context.order_id, "No order to check"
    attrs = _get_order(context.order_id)
    actual = attrs.get(field)

    if expected_value in ("True", "False"):
        assert str(actual) == expected_value or bool(actual) == (expected_value == "True"), \
            f"Order {field}: expected {expected_value}, got {actual}"
    else:
        try:
            assert abs(float(actual) - float(expected_value)) < 0.01, \
                f"Order {field}: expected {expected_value}, got {actual}"
        except (TypeError, ValueError):
            assert str(actual) == expected_value, \
                f"Order {field}: expected {expected_value}, got {actual}"

    # No prt call here - would wipe the logic log


@then("the order is rejected with error {error_msg}")
def step_order_rejected(context, error_msg):
    """Assert that order creation was rejected with a specific error."""
    assert getattr(context, "order_rejected", False), \
        f"Expected order rejection but it succeeded (id={context.order_id})"
    assert error_msg in context.order_error_text, \
        f"Expected error '{error_msg}' not found in: {context.order_error_text}"
    # No prt call here - would wipe the logic log


# ---------------------------------------------------------------------------
# Then steps - Logic Log verification (rules report integration)
# These verify that the declarative rules engine actually fired correctly
# by inspecting the server's logic trace log for this scenario.
# ---------------------------------------------------------------------------

@then("Logic computes surtax applicable True for post-cutoff date")
def step_logic_surtax_applicable_true(context):
    """Verify logic log shows surtax_applicable=True determination."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Surtax Applicable: True",
        in_file=log_file), \
        f"Logic Log missing 'Surtax Applicable: True' in {log_file}"


@then("Logic computes surtax applicable False for pre-cutoff date")
def step_logic_surtax_applicable_false_date(context):
    """Verify logic log shows surtax_applicable=False for pre-cutoff ship date."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Surtax Applicable: False",
        in_file=log_file), \
        f"Logic Log missing 'Surtax Applicable: False' in {log_file}"


@then("Logic computes surtax applicable False for non-surtax country")
def step_logic_surtax_applicable_false_country(context):
    """Verify logic log shows surtax_applicable=False for non-surtax country."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Surtax Applicable: False",
        in_file=log_file), \
        f"Logic Log missing 'Surtax Applicable: False' in {log_file}"


@then("Logic computes surtax_amount 125000 from customs_value times surtax_rate")
def step_logic_surtax_amount_calculated(context):
    """Verify logic log shows surtax_amount calculation with Applicable: True."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Surtax Amount: 125000",
        in_file=log_file), \
        f"Logic Log missing 'Surtax Amount: 125000' in {log_file}"
    assert test_utils.does_file_contain(
        search_for="Formula surtax_amount",
        in_file=log_file), \
        f"Logic Log missing 'Formula surtax_amount' in {log_file}"


@then("Logic computes surtax_amount 0 when not applicable")
def step_logic_surtax_amount_zero(context):
    """Verify logic log shows surtax_amount=0 (Applicable: False)."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Surtax Amount: 0",
        in_file=log_file), \
        f"Logic Log missing 'Surtax Amount: 0' in {log_file}"


@then("Logic computes PST/HST rate copied from province")
def step_logic_pst_hst_rate(context):
    """Verify logic log shows PST/HST rate copied from province reference table."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="PST/HST Rate:",
        in_file=log_file), \
        f"Logic Log missing 'PST/HST Rate:' in {log_file}"
    assert test_utils.does_file_contain(
        search_for="Formula pst_hst_amount",
        in_file=log_file), \
        f"Logic Log missing 'Formula pst_hst_amount' in {log_file}"


@then("Logic rolls up line totals to order")
def step_logic_rollup_to_order(context):
    """Verify logic log shows SurtaxOrder sums adjusted from line item insert."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Formula total_amount",
        in_file=log_file), \
        f"Logic Log missing 'Formula total_amount' in {log_file}"
    assert test_utils.does_file_contain(
        search_for="total_customs_value",
        in_file=log_file), \
        f"Logic Log missing 'total_customs_value' rollup in {log_file}"
    assert test_utils.does_file_contain(
        search_for="total_surtax",
        in_file=log_file), \
        f"Logic Log missing 'total_surtax' rollup in {log_file}"


@then("Logic rolls up multi-item totals to order")
def step_logic_multi_item_rollup(context):
    """Verify logic log shows multi-item rollups adjusting SurtaxOrder totals."""
    log_file = logic_log_file(context.scenario.name)
    assert test_utils.does_file_contain(
        search_for="Adjusting surtax_order",
        in_file=log_file), \
        f"Logic Log missing 'Adjusting surtax_order' in {log_file}"
    assert test_utils.does_file_contain(
        search_for="total_customs_value",
        in_file=log_file), \
        f"Logic Log missing 'total_customs_value' in {log_file}"
