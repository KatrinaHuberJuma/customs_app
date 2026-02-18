Feature: CBSA Steel Derivative Goods Surtax

  Background: Load Sample Database
    Given the CBSA surtax database is loaded

  Scenario: Surtax applies for post-cutoff ship date with surtax country
    Given a SurtaxOrder for Germany to Ontario with ship_date 2026-01-15 and entry_date 2026-01-10
    When a line item is added with hs_code 7208.10.00 quantity 1000 and unit_price 500.00
    Then the line item customs_value is 500000.00
    And the line item surtax_amount is 125000.00
    And the line item duty_amount is 0.00
    And the line item pst_hst_amount is 81250.00
    And the line item total_amount is 706250.00
    And the order surtax_applicable is True
    And the order total_customs_value is 500000.00
    And the order total_surtax is 125000.00
    And the order total_amount_due is 706250.00
    Then Logic computes surtax applicable True for post-cutoff date
    Then Logic computes surtax_amount 125000 from customs_value times surtax_rate
    Then Logic computes PST/HST rate copied from province
    Then Logic rolls up line totals to order

  Scenario: No surtax for pre-cutoff ship date
    Given a SurtaxOrder for Japan to Quebec with ship_date 2025-12-20 and entry_date 2025-12-15
    When a line item is added with hs_code 7213.91.00 quantity 500 and unit_price 200.00
    Then the line item customs_value is 100000.00
    And the line item surtax_amount is 0.00
    And the order surtax_applicable is False
    And the order total_surtax is 0.00
    Then Logic computes surtax applicable False for pre-cutoff date
    Then Logic computes surtax_amount 0 when not applicable

  Scenario: No surtax for non-surtax country (Mexico)
    Given a SurtaxOrder for Mexico to Alberta with ship_date 2026-02-01 and entry_date 2026-01-25
    When a line item is added with hs_code 7308.90.00 quantity 200 and unit_price 150.00
    Then the line item customs_value is 30000.00
    And the line item surtax_amount is 0.00
    And the order surtax_applicable is False
    Then Logic computes surtax applicable False for non-surtax country

  Scenario: Order totals roll up from multiple line items
    Given a SurtaxOrder for United States to British Columbia with ship_date 2025-12-28 and entry_date 2025-12-20
    When a line item is added with hs_code 7304.31.00 quantity 100 and unit_price 1000.00
    And a second line item is added with hs_code 7306.30.00 quantity 50 and unit_price 800.00
    Then the order total_customs_value is 140000.00
    And the order total_surtax is 35000.00
    Then Logic rolls up multi-item totals to order

  Scenario: Constraint - ship date cannot be before entry date
    Given a SurtaxOrder for China to Ontario with ship_date 2026-01-01 and entry_date 2026-01-15
    Then the order is rejected with error Ship date cannot be before entry date

  Scenario: Constraint - quantity must be positive
    Given a SurtaxOrder for Germany to Ontario with ship_date 2026-02-01 and entry_date 2026-01-20
    When a line item is added with hs_code 7208.10.00 quantity -10 and unit_price 100.00
    Then the line item is rejected with error Quantity must be greater than zero

  Scenario: Constraint - unit price must be positive
    Given a SurtaxOrder for Germany to Ontario with ship_date 2026-02-01 and entry_date 2026-01-20
    When a line item is added with hs_code 7208.10.00 quantity 100 and unit_price -50.00
    Then the line item is rejected with error Unit price must be greater than zero
