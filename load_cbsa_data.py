"""
Load reference data and sample orders for CBSA Steel Derivative Goods Surtax system
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import models

# Database connection
DATABASE_URL = "sqlite:///database/db.sqlite"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def load_provincial_tax_rates():
    """Load Canadian provincial tax rates (PST/HST/GST)"""
    print("\n=== Loading Provincial Tax Rates ===")
    
    provinces = [
        # HST Provinces (Harmonized Sales Tax)
        {"code": "ON", "name": "Ontario", "type": "HST", "rate": Decimal("0.13")},
        {"code": "NB", "name": "New Brunswick", "type": "HST", "rate": Decimal("0.15")},
        {"code": "NS", "name": "Nova Scotia", "type": "HST", "rate": Decimal("0.15")},
        {"code": "NL", "name": "Newfoundland and Labrador", "type": "HST", "rate": Decimal("0.15")},
        {"code": "PE", "name": "Prince Edward Island", "type": "HST", "rate": Decimal("0.15")},
        
        # GST + PST Provinces
        {"code": "BC", "name": "British Columbia", "type": "GST+PST", "rate": Decimal("0.12")},  # 5% GST + 7% PST
        {"code": "SK", "name": "Saskatchewan", "type": "GST+PST", "rate": Decimal("0.11")},      # 5% GST + 6% PST
        {"code": "MB", "name": "Manitoba", "type": "GST+PST", "rate": Decimal("0.12")},          # 5% GST + 7% PST
        {"code": "QC", "name": "Quebec", "type": "GST+QST", "rate": Decimal("0.14975")},        # 5% GST + 9.975% QST
        
        # GST Only (No Provincial Tax)
        {"code": "AB", "name": "Alberta", "type": "GST", "rate": Decimal("0.05")},
        {"code": "YT", "name": "Yukon", "type": "GST", "rate": Decimal("0.05")},
        {"code": "NT", "name": "Northwest Territories", "type": "GST", "rate": Decimal("0.05")},
        {"code": "NU", "name": "Nunavut", "type": "GST", "rate": Decimal("0.05")},
    ]
    
    effective_date = date(2025, 1, 1)
    
    for prov in provinces:
        existing = session.query(models.ProvinceTaxRate).filter_by(province_code=prov["code"]).first()
        if existing:
            print(f"  ✓ {prov['name']} ({prov['code']}) - Already exists")
            continue
            
        tax_rate = models.ProvinceTaxRate(
            province_code=prov["code"],
            province_name=prov["name"],
            tax_type=prov["type"],
            tax_rate=prov["rate"],
            effective_date=effective_date
        )
        session.add(tax_rate)
        print(f"  + {prov['name']} ({prov['code']}) - {prov['type']} {float(prov['rate'])*100:.2f}%")
    
    session.commit()
    print("✓ Provincial tax rates loaded")


def load_countries():
    """Load countries of origin with surtax applicability"""
    print("\n=== Loading Countries ===")
    
    countries = [
        # Countries subject to surtax
        {"code": "CN", "name": "China", "surtax": True, "rate": Decimal("0.25")},
        {"code": "DE", "name": "Germany", "surtax": True, "rate": Decimal("0.25")},
        
        # Countries with lower or no surtax (examples)
        {"code": "US", "name": "United States", "surtax": True, "rate": Decimal("0.25")},
        {"code": "JP", "name": "Japan", "surtax": True, "rate": Decimal("0.25")},
        
        # Additional countries that might be exempt or have different rates
        {"code": "MX", "name": "Mexico", "surtax": False, "rate": Decimal("0.00")},  # USMCA partner
        {"code": "CA", "name": "Canada", "surtax": False, "rate": Decimal("0.00")},  # Domestic
    ]
    
    for country in countries:
        existing = session.query(models.CountryOrigin).filter_by(country_code=country["code"]).first()
        if existing:
            print(f"  ✓ {country['name']} ({country['code']}) - Already exists")
            continue
            
        country_origin = models.CountryOrigin(
            country_code=country["code"],
            country_name=country["name"],
            surtax_applicable=country["surtax"],
            surtax_rate=country["rate"]
        )
        session.add(country_origin)
        
        surtax_status = f"Surtax {float(country['rate'])*100:.0f}%" if country['surtax'] else "No Surtax"
        print(f"  + {country['name']} ({country['code']}) - {surtax_status}")
    
    session.commit()
    print("✓ Countries loaded")


def load_hs_codes():
    """Load HS codes for steel derivative goods"""
    print("\n=== Loading HS Codes ===")
    
    hs_codes = [
        {
            "code": "7208.10.00",
            "description": "Flat-rolled products of iron or non-alloy steel, in coils, hot-rolled",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7210.41.00",
            "description": "Flat-rolled products of iron or non-alloy steel, plated or coated with zinc",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7213.91.00",
            "description": "Bars and rods, hot-rolled, of iron or non-alloy steel",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7216.50.00",
            "description": "Angles, shapes and sections of iron or non-alloy steel",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7304.31.00",
            "description": "Tubes, pipes and hollow profiles, seamless, of circular cross-section, of iron or steel",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7306.30.00",
            "description": "Tubes, pipes and hollow profiles, welded, of circular cross-section, of iron or steel",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7308.90.00",
            "description": "Structures and parts of structures, of iron or steel",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
        {
            "code": "7318.15.00",
            "description": "Screws and bolts, of iron or steel",
            "duty": Decimal("0.00"),
            "surtax": Decimal("0.25")
        },
    ]
    
    effective_date = date(2025, 12, 26)
    
    for hs in hs_codes:
        existing = session.query(models.HSCodeRate).filter_by(hs_code=hs["code"]).first()
        if existing:
            print(f"  ✓ {hs['code']} - Already exists")
            continue
            
        hs_code = models.HSCodeRate(
            hs_code=hs["code"],
            description=hs["description"],
            base_duty_rate=hs["duty"],
            surtax_rate=hs["surtax"],
            effective_date=effective_date
        )
        session.add(hs_code)
        print(f"  + {hs['code']} - {hs['description'][:50]}...")
    
    session.commit()
    print("✓ HS Codes loaded")


def create_sample_orders():
    """Create sample orders from Germany, US, Japan, and China"""
    print("\n=== Creating Sample Orders ===")
    
    # Get reference data
    ontario = session.query(models.ProvinceTaxRate).filter_by(province_code="ON").first()
    bc = session.query(models.ProvinceTaxRate).filter_by(province_code="BC").first()
    quebec = session.query(models.ProvinceTaxRate).filter_by(province_code="QC").first()
    
    germany = session.query(models.CountryOrigin).filter_by(country_code="DE").first()
    usa = session.query(models.CountryOrigin).filter_by(country_code="US").first()
    japan = session.query(models.CountryOrigin).filter_by(country_code="JP").first()
    china = session.query(models.CountryOrigin).filter_by(country_code="CN").first()
    
    # Get HS codes
    hs_codes = session.query(models.HSCodeRate).all()
    
    # Define sample orders
    orders = [
        {
            "order_number": "CBSA-2025-1001-DE",
            "country": germany,
            "province": ontario,
            "ship_date": date(2026, 1, 15),  # After cutoff - surtax applies
            "importer": "Canadian Steel Importers Ltd.",
            "items": [
                {"hs": "7208.10.00", "desc": "Hot-rolled steel coils", "qty": 10000, "price": 850.00},
                {"hs": "7210.41.00", "desc": "Zinc-coated steel sheets", "qty": 5000, "price": 920.00},
            ]
        },
        {
            "order_number": "CBSA-2025-1002-US",
            "country": usa,
            "province": bc,
            "ship_date": date(2025, 12, 28),  # Just after cutoff - surtax applies
            "importer": "Western Canada Steel Co.",
            "items": [
                {"hs": "7304.31.00", "desc": "Seamless steel pipes", "qty": 2000, "price": 1450.00},
                {"hs": "7306.30.00", "desc": "Welded steel tubes", "qty": 3000, "price": 1200.00},
            ]
        },
        {
            "order_number": "CBSA-2025-1003-JP",
            "country": japan,
            "province": quebec,
            "ship_date": date(2025, 12, 20),  # Before cutoff - NO surtax
            "importer": "Quebec Manufacturing Inc.",
            "items": [
                {"hs": "7213.91.00", "desc": "Hot-rolled steel bars", "qty": 8000, "price": 780.00},
                {"hs": "7216.50.00", "desc": "Steel angles and sections", "qty": 4000, "price": 890.00},
            ]
        },
        {
            "order_number": "CBSA-2025-1004-CN",
            "country": china,
            "province": ontario,
            "ship_date": date(2026, 2, 1),  # Well after cutoff - surtax applies
            "importer": "Toronto Steel Distributors",
            "items": [
                {"hs": "7308.90.00", "desc": "Steel structures and parts", "qty": 15000, "price": 650.00},
                {"hs": "7318.15.00", "desc": "Steel screws and bolts", "qty": 50000, "price": 12.50},
            ]
        },
    ]
    
    for order_data in orders:
        existing = session.query(models.SurtaxOrder).filter_by(order_number=order_data["order_number"]).first()
        if existing:
            print(f"  ✓ {order_data['order_number']} - Already exists")
            continue
        
        # Create order
        order = models.SurtaxOrder(
            order_number=order_data["order_number"],
            entry_date=date.today(),
            ship_date=order_data["ship_date"],
            country_origin_id=order_data["country"].id,
            province_code_id=order_data["province"].id,
            importer_name=order_data["importer"],
            broker_name="CBSA Licensed Customs Broker"
        )
        session.add(order)
        session.flush()  # Get the order ID
        
        # Create line items
        for idx, item_data in enumerate(order_data["items"], 1):
            hs_code = session.query(models.HSCodeRate).filter_by(hs_code=item_data["hs"]).first()
            
            line_item = models.SurtaxLineItem(
                surtax_order_id=order.id,
                hs_code_id=hs_code.id,
                line_number=idx,
                description=item_data["desc"],
                quantity=Decimal(str(item_data["qty"])),
                unit_of_measure="KG",
                unit_price=Decimal(str(item_data["price"]))
            )
            session.add(line_item)
        
        print(f"  + {order_data['order_number']} - {order_data['country'].country_name} → {order_data['province'].province_code}")
        print(f"    Ship: {order_data['ship_date']} ({len(order_data['items'])} items)")
    
    session.commit()
    print("✓ Sample orders created")


def main():
    """Load all reference data and create sample orders"""
    print("\n" + "="*70)
    print("CBSA Steel Derivative Goods Surtax System - Data Loader")
    print("PC Number: 2025-0917, Program Code: 25267A")
    print("="*70)
    
    try:
        load_provincial_tax_rates()
        load_countries()
        load_hs_codes()
        create_sample_orders()
        
        print("\n" + "="*70)
        print("✓ ALL DATA LOADED SUCCESSFULLY")
        print("="*70)
        
        # Print summary
        print("\nDatabase Summary:")
        print(f"  • Provincial Tax Rates: {session.query(models.ProvinceTaxRate).count()}")
        print(f"  • Countries: {session.query(models.CountryOrigin).count()}")
        print(f"  • HS Codes: {session.query(models.HSCodeRate).count()}")
        print(f"  • Surtax Orders: {session.query(models.SurtaxOrder).count()}")
        print(f"  • Surtax Line Items: {session.query(models.SurtaxLineItem).count()}")
        
        print("\n✓ Ready to start the server and view in Admin UI!")
        print("  Run: python api_logic_server_run.py")
        print("  Then open: http://localhost:5656/admin-app")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
