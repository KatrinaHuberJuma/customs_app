"""
CBSA Steel Derivative Goods Surtax Business Logic
PC Number: 2025-0917, Program Code: 25267A
Effective Date: 2025-12-26
"""
from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database import models
from datetime import date, datetime


def to_date(value):
    """
    Convert various date formats to date object for safe comparison.
    
    Bugfix: API sends datetime.datetime objects, but date comparisons expect date objects.
    Original code: row.ship_date >= effective_date 
    Error: TypeError: '>=' not supported between instances of 'datetime.datetime' and 'datetime.date'
    Fix: Convert all date types to date objects before comparison.
    """
    if value is None:
        return None
    # bugfix - Check datetime BEFORE date (datetime is subclass of date!)
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        # Handle ISO format strings like "2026-01-15"
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None
    return None


def declare_logic():
    """
    Business rules for CBSA Steel Derivative Goods Surtax calculations.
    
    Implements:
    1. Line item calculations (customs value, duty, surtax, PST/HST)
    2. Order totals (sum of line items)
    3. Surtax applicability based on ship date >= 2025-12-26
    4. Automatic rate copying from reference tables
    """
    
    # ==============================================================================
    # SURTAX LINE ITEM CALCULATIONS
    # ==============================================================================
    
    # 1. Calculate customs value = quantity * unit_price
    Rule.formula(derive=models.SurtaxLineItem.customs_value,
                 as_expression=lambda row: row.quantity * row.unit_price)
    
    # 2. Copy duty rate from HS Code reference
    Rule.copy(derive=models.SurtaxLineItem.duty_rate,
              from_parent=models.HSCodeRate.base_duty_rate)
    
    # 3. Copy surtax rate from HS Code reference
    Rule.copy(derive=models.SurtaxLineItem.surtax_rate,
              from_parent=models.HSCodeRate.surtax_rate)
    
    # 4. Calculate duty amount = customs_value * duty_rate
    Rule.formula(derive=models.SurtaxLineItem.duty_amount,
                 as_expression=lambda row: row.customs_value * (row.duty_rate or 0))
    
    # 5. Calculate surtax amount (only if order is subject to surtax)
    def calculate_surtax_amount(row: models.SurtaxLineItem, old_row: models.SurtaxLineItem, logic_row: LogicRow):
        """
        Calculate surtax only if parent order has surtax_applicable = True.
        
        Bugfix: Formula rules require return value; setting row attribute doesn't persist.
        Original code: row.surtax_amount = ... (but no return statement)
        Error: NoneType in aggregate calculations causing "unsupported operand type(s) for -: 'NoneType' and 'int'"
        Fix: Return the calculated value instead of just setting it.
        """
        if row.surtax_order and row.surtax_order.surtax_applicable : #bugfix - LogicBank error when accessing parent relationship
            result = row.customs_value * (row.surtax_rate or 0)
        else:
            result = 0
        logic_row.log(f"Surtax Amount: {result} (Applicable: {row.surtax_order.surtax_applicable if row.surtax_order else False})")
        return result  # bugfix - MUST return value for Formula rules!
    
    Rule.formula(derive=models.SurtaxLineItem.surtax_amount,
                 calling=calculate_surtax_amount)
    
    # 6. Copy PST/HST rate from province (via parent order)
    def copy_pst_hst_rate(row: models.SurtaxLineItem, old_row: models.SurtaxLineItem, logic_row: LogicRow):
        """
        Copy provincial tax rate from the order's province.
        
        Bugfix: Formula rules require return value; setting row attribute doesn't persist.
        Original code: row.pst_hst_rate = ... (but no return statement)
        Error: NoneType in aggregate calculations causing "unsupported operand type(s) for -: 'NoneType' and 'int'"
        Fix: Return the calculated value instead of just setting it.
        """
        if row.surtax_order and row.surtax_order.province_tax_rate : #bugfix - LogicBank error when accessing parent relationship
            result = row.surtax_order.province_tax_rate.tax_rate
        else:
            result = 0
        logic_row.log(f"PST/HST Rate: {result}")
        return result  # bugfix - MUST return value for Formula rules!
    
    Rule.formula(derive=models.SurtaxLineItem.pst_hst_rate,
                 calling=copy_pst_hst_rate)
    
    # 7. Calculate PST/HST amount = (customs_value + duty + surtax) * pst_hst_rate
    Rule.formula(derive=models.SurtaxLineItem.pst_hst_amount,
                 as_expression=lambda row: (row.customs_value + (row.duty_amount or 0) + 
                                           (row.surtax_amount or 0)) * (row.pst_hst_rate or 0))
    
    # 8. Calculate total amount for line item
    Rule.formula(derive=models.SurtaxLineItem.total_amount,
                 as_expression=lambda row: (row.customs_value + 
                                           (row.duty_amount or 0) + 
                                           (row.surtax_amount or 0) + 
                                           (row.pst_hst_amount or 0)))
    
    # ==============================================================================
    # SURTAX ORDER CALCULATIONS (Roll-ups from line items)
    # ==============================================================================
    
    # 9. Sum total customs value from all line items
    Rule.sum(derive=models.SurtaxOrder.total_customs_value,
             as_sum_of=models.SurtaxLineItem.customs_value)
    
    # 10. Sum total duty from all line items
    Rule.sum(derive=models.SurtaxOrder.total_duty,
             as_sum_of=models.SurtaxLineItem.duty_amount)
    
    # 11. Sum total surtax from all line items
    Rule.sum(derive=models.SurtaxOrder.total_surtax,
             as_sum_of=models.SurtaxLineItem.surtax_amount)
    
    # 12. Sum total PST/HST from all line items
    Rule.sum(derive=models.SurtaxOrder.total_pst_hst,
             as_sum_of=models.SurtaxLineItem.pst_hst_amount)
    
    # 13. Sum total amount due from all line items
    Rule.sum(derive=models.SurtaxOrder.total_amount_due,
             as_sum_of=models.SurtaxLineItem.total_amount)
    
    # ==============================================================================
    # SURTAX APPLICABILITY (Based on ship date >= 2025-12-26)
    # ==============================================================================
    
    def determine_surtax_applicability(row: models.SurtaxOrder, old_row: models.SurtaxOrder, logic_row: LogicRow):
        """
        Determine if surtax applies based on:
        1. Ship date >= 2025-12-26 (effective date)
        2. Country has surtax_applicable = True
        
        Bugfix: Original code set row.surtax_applicable but didn't return the value.
        Error: Formula rules require a return value; setting row attribute doesn't persist.
        Fix: Return the calculated result instead of just setting it.
        """
        effective_date = date(2025, 12, 26)
        
        # bugfix - Safely convert ship_date to date object for comparison (see to_date function)
        ship_date = to_date(row.ship_date)
        date_check = ship_date >= effective_date if ship_date else False
        
        country_check = False
        if row.country_origin_id :  # bugfix - LogicBank error
            # Explicitly load the country using the session if relationship not loaded
            if row.country_origin is None:
                country = logic_row.session.query(models.CountryOrigin).filter_by(id=row.country_origin_id).first()
                if country:
                    country_check = country.surtax_applicable
            else:
                country_check = row.country_origin.surtax_applicable
            
        result = date_check and country_check
        
        logic_row.log(f"Surtax Applicable: {result} " +
                     f"(Ship Date: {ship_date}, Date Check: {date_check}, " +
                     f"Country Check: {country_check}, Cutoff: {effective_date})")
        
        return result  # bugfix - MUST return value for Formula rules!
    
    Rule.formula(derive=models.SurtaxOrder.surtax_applicable,
                 calling=determine_surtax_applicability)
    
    # ==============================================================================
    # CONSTRAINTS
    # ==============================================================================
    
    # Ensure ship_date is not in the past relative to entry_date
    def validate_ship_date(row: models.SurtaxOrder):
        """
        Validate ship date is not before entry date.
        
        Bugfix: Original lambda compared dates directly without type conversion.
        Original code: lambda row: row.ship_date >= row.entry_date
        Error: TypeError when comparing datetime.datetime with datetime.date
        Fix: Use to_date() helper to ensure same type before comparison.
        """
        ship_date = to_date(row.ship_date)
        entry_date = to_date(row.entry_date)
        
        if ship_date is None or entry_date is None:
            return True  # Allow None values
        
        return ship_date >= entry_date
    
    Rule.constraint(validate=models.SurtaxOrder,
                   as_condition=validate_ship_date,
                   error_msg="Ship date cannot be before entry date")
    
    # Ensure quantity is positive
    Rule.constraint(validate=models.SurtaxLineItem,
                   as_condition=lambda row: row.quantity is None or row.quantity > 0,
                   error_msg="Quantity must be greater than zero")
    
    # Ensure unit price is positive
    Rule.constraint(validate=models.SurtaxLineItem,
                   as_condition=lambda row: row.unit_price is None or row.unit_price > 0,
                   error_msg="Unit price must be greater than zero")


# This logic will be automatically discovered and loaded by logic/logic_discovery/auto_discovery.py
