# CBSA Steel Derivative Goods Surtax System

## Overview

This application implements the **Canada Border Services Agency (CBSA) Steel Derivative Goods Surtax Order** (PC Number: 2025-0917, Program Code: 25267A) effective December 26, 2025.

The system automatically calculates:
- **Customs duties** based on HS codes
- **Steel surtax** (25%) when applicable 
-provinces Provincial sales tax (**PST/HST**) based on destination province
- **Total amounts due** with complete roll-ups

## System Architecture

### Database Tables

1. **ProvinceTaxRate** - Canadian provincial tax rates (PST/HST/GST)
2. **CountryOrigin** - Countries with surtax applicability settings
3. **HSCodeRate** - HS code classifications with duty and surtax rates
4. **SurtaxOrder** - Main customs entry orders
5. **SurtaxLineItem** - Individual goods on each order

### Business Logic (Declarative Rules)

The system uses declarative business rules that automatically:

**Line Item Calculations:**
- Calculate customs_value = quantity × unit_price
- Copy duty_rate from HS code
- Copy surtax_rate from HS code
- Calculate duty_amount = customs_value × duty_rate
- Calculate surtax_amount (only if ship_date >= 2025-12-26)
- Copy PST/HST rate from province
- Calculate PST/HST amount on (customs_value + duty + surtax)
- Calculate total_amount for the line

**Order Roll-ups:**
- Sum total_customs_value from all line items
- Sum total_duty from all line items
- Sum total_surtax from all line items
- Sum total_pst_hst from all line items
- Sum total_amount_due from all line items
- Determine surtax_applicable flag based on ship date

**Constraints:**
- Ship date cannot be before entry date
- Quantity must be positive
- Unit price must be positive

## Sample Data Loaded

### Countries
- 🇨🇳 **China (CN)** - Surtax 25%
- 🇩🇪 **Germany (DE)** - Surtax 25%
- 🇺🇸 **United States (US)** - Surtax 25%
- 🇯🇵 **Japan (JP)** - Surtax 25%
- 🇲🇽 Mexico (MX) - No surtax
- 🇨🇦 Canada (CA) - No surtax

### Canadian Provinces
All provinces loaded with current HST/PST/GST rates:
- Ontario (ON): HST 13%
- British Columbia (BC): GST+PST 12%
- Quebec (QC): GST+QST 14.975%
- Alberta (AB): GST 5%
- And all other provinces/territories

### HS Codes
8 steel derivative HS codes loaded:
- 7208.10.00 - Hot-rolled steel coils
- 7210.41.00 - Zinc-coated steel sheets
- 7213.91.00 - Hot-rolled steel bars
- 7216.50.00 - Steel angles and sections
- 7304.31.00 - Seamless steel pipes
- 7306.30.00 - Welded steel tubes
- 7308.90.00 - Steel structures
- 7318.15.00 - Steel screws and bolts

### Sample Orders
4 complete orders with line items:

1. **CBSA-2025-1001-DE** - Germany → Ontario
   - Ship: Jan 15, 2026 ✓ Surtax applies
   - Items: Hot-rolled steel coils, zinc-coated sheets

2. **CBSA-2025-1002-US** - United States → British Columbia
   - Ship: Dec 28, 2025 ✓ Surtax applies (just after cutoff)
   - Items: Seamless pipes, welded tubes

3. **CBSA-2025-1003-JP** - Japan → Quebec
   - Ship: Dec 20, 2025 ✗ NO surtax (before cutoff)
   - Items: Hot-rolled bars, steel angles

4. **CBSA-2025-1004-CN** - China → Ontario
   - Ship: Feb 1, 2026 ✓ Surtax applies
   - Items: Steel structures, screws and bolts

## How to Use

### 1. Access the Admin UI

Open your browser to: **http://localhost:5656/admin-app**

Navigate to the **SurtaxOrder** table to view customs entries.

### 2. View Sample Orders

Click on any order to see:
- Order details (order number, dates, country, province)
- Calculated totals (customs value, duty, surtax, PST/HST)
- Surtax applicability flag
- Line items tab showing individual goods

### 3. Create a New Order

**Step 1: Create the Order**
- Click "Create" in SurtaxOrder
- Enter order details:
  - Order Number (unique)
  - Entry Date (today)
  - Ship Date (controls surtax applicability)
  - Select Country of Origin
  - Select Province
  - Enter Importer Name

**Step 2: Add Line Items**
- Go to "SurtaxLineItemList" tab
- Click "Create"
- Select HS Code (duty & surtax rates auto-copy)
- Enter quantity and unit price
- Watch calculations happen automatically!

### 4. Test Surtax Applicability

**To see surtax apply:**
- Set ship_date >= 2025-12-26
- Select a country with surtax (Germany, US, Japan, China)
- Add a line item
- Observe: surtax_amount is calculated (25% of customs value)

**To see NO surtax:**
- Set ship_date < 2025-12-26, OR
- Select Mexico or Canada
- Add a line item
- Observe: surtax_amount = 0

### 5. View API

Visit: **http://localhost:5656/api**

Interactive Swagger documentation shows all endpoints:
- `/api/SurtaxOrder/` - List all orders
- `/api/SurtaxLineItem/` - List all line items
- `/api/HSCodeRate/` - HS code reference data
- `/api/CountryOrigin/` - Country reference data
- `/api/ProvinceTaxRate/` - Provincial tax rates

## API Examples

### Get All Orders
```bash
curl 'http://localhost:5656/api/SurtaxOrder/'
```

### Get Specific Order with Line Items
```bash
curl 'http://localhost:5656/api/SurtaxOrder/1/?include=SurtaxLineItemList'
```

### Create New Order via API
```bash
curl -X POST 'http://localhost:5656/api/SurtaxOrder/' \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{
    "data": {
      "type": "SurtaxOrder",
      "attributes": {
        "order_number": "CBSA-2026-1005-DE",
        "entry_date": "2026-02-17",
        "ship_date": "2026-03-01",
        "country_origin_id": 2,
        "province_code_id": 1,
        "importer_name": "Test Importer Inc."
      }
    }
  }'
```

## Business Logic in Action

### What Happens When You Create a Line Item?

1. **You enter:**
   - HS code: 7208.10.00
   - Quantity: 1000 KG
   - Unit Price: $500/KG

2. **System automatically calculates:**
   - customs_value = 1000 × 500 = **$500,000**
   - duty_rate = 0% (copied from HS code)
   - duty_amount = $500,000 × 0% = **$0**
   - surtax_rate = 25% (copied from HS code)
   - surtax_amount = $500,000 × 25% = **$125,000** (if applicable)
   - pst_hst_rate = 13% (copied from Ontario)
   - pst_hst_amount = ($500,000 + $0 + $125,000) × 13% = **$81,250**
   - total_amount = $500,000 + $0 + $125,000 + $81,250 = **$706,250**

3. **Order totals automatically update:**
   - All line item amounts roll up to order totals
   - No manual recalculation needed!

### Multi-Table Cascading

When you:
- **Add a line item** → Order totals update
- **Change quantity** → Customs value recalculates → Duty recalculates → Surtax recalculates → PST/HST recalculates → Line total updates → Order totals update
- **Change ship date** → Surtax applicability recalculates → All line item surtax amounts recalculate → Order totals update
- **Delete a line item** → Order totals adjust automatically

This is the power of **declarative business logic** - define what should be true, not how to calculate it!

## Files Created

- `database/models.py` - Database models (added CBSA tables)
- `logic/logic_discovery/cbsa_steel_surtax.py` - Business rules
- `load_cbsa_data.py` - Data loader script
- `ui/admin/admin.yaml` - UI configuration
- `database/alembic/versions/35e71709ec36_*.py` - Database migration

## Technical Details

**Framework:** API Logic Server (GenAI-Logic)
**Database:** SQLite
**Business Logic:** LogicBank (declarative rules engine)
**API:** JSON:API standard with SAFRS
**Admin UI:** React Admin

**Rules Engine Statistics:**
- 21 business rules loaded
- 14 formulas (calculations)
- 4 copy rules (rate lookups)
- 3 constraints (validations)
- 5 sum rules (rollups)
- All rules execute automatically at commit time

## Next Steps

1. **Explore the UI** - Create orders, add line items, watch calculations
2. **Test edge cases** - Try dates before/after cutoff, different provinces
3. **View API docs** - http://localhost:5656/api for interactive testing
4. **Add more HS codes** - Expand the steel goods catalog
5. **Add security** - Run `genai-logic add-auth` to enable RBAC
6. **Create custom UI** - Run `genai-logic genai-add-app --vibe` for React app
7. **Export data** - Query API for reporting/integration

## Support

For questions or issues with the CBSA surtax system, refer to:
- Logic rules: `logic/logic_discovery/cbsa_steel_surtax.py`
- Models: `database/models.py`
- API: http://localhost:5656/api
- Admin UI: http://localhost:5656/admin-app

---

**Ready to start?** Open http://localhost:5656/admin-app and explore!
