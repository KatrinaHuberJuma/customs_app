#!/bin/bash
# Test script to verify date arithmetic fix for CBSA Surtax orders

echo "Testing CBSA Surtax Date Arithmetic Fix"
echo "========================================="
echo ""

# Test 1: Create order with ship date AFTER cutoff (should have surtax)
echo "Test 1: Order with ship_date = 2026-01-20 (AFTER 2025-12-26 cutoff)"
curl -s -X POST 'http://localhost:5656/api/SurtaxOrder/' \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{
    "data": {
      "type": "SurtaxOrder",
      "attributes": {
        "order_number": "TEST-2026-001",
        "entry_date": "2026-01-15",
        "ship_date": "2026-01-20",
        "country_origin_id": 2,
        "province_code_id": 1,
        "importer_name": "Test Importer - After Cutoff"
      }
    }
  }' | python3 -m json.tool | grep -E "order_number|ship_date|surtax_applicable|error"

echo ""
echo "---"
echo ""

# Test 2: Create order with ship date BEFORE cutoff (should NOT have surtax)
echo "Test 2: Order with ship_date = 2025-12-20 (BEFORE 2025-12-26 cutoff)"
curl -s -X POST 'http://localhost:5656/api/SurtaxOrder/' \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{
    "data": {
      "type": "SurtaxOrder",
      "attributes": {
        "order_number": "TEST-2025-002",
        "entry_date": "2025-12-15",
        "ship_date": "2025-12-20",
        "country_origin_id": 2,
        "province_code_id": 1,
        "importer_name": "Test Importer - Before Cutoff"
      }
    }
  }' | python3 -m json.tool | grep -E "order_number|ship_date|surtax_applicable|error"

echo ""
echo "---"
echo ""

# Test 3: Create order with ship date exactly ON cutoff
echo "Test 3: Order with ship_date = 2025-12-26 (EXACTLY ON cutoff)"
curl -s -X POST 'http://localhost:5656/api/SurtaxOrder/' \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{
    "data": {
      "type": "SurtaxOrder",
      "attributes": {
        "order_number": "TEST-2025-003",
        "entry_date": "2025-12-20",
        "ship_date": "2025-12-26",
        "country_origin_id": 2,
        "province_code_id": 1,
        "importer_name": "Test Importer - On Cutoff"
      }
    }
  }' | python3 -m json.tool | grep -E "order_number|ship_date|surtax_applicable|error"

echo ""
echo "---"
echo ""

# Test 4: Invalid - ship date before entry date (should fail constraint)
echo "Test 4: Invalid order - ship_date BEFORE entry_date (should fail)"
curl -s -X POST 'http://localhost:5656/api/SurtaxOrder/' \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{
    "data": {
      "type": "SurtaxOrder",
      "attributes": {
        "order_number": "TEST-2026-004",
        "entry_date": "2026-02-01",
        "ship_date": "2026-01-15",
        "country_origin_id": 2,
        "province_code_id": 1,
        "importer_name": "Test Invalid Date Order"
      }
    }
  }' | python3 -m json.tool | grep -E "order_number|error|constraint"

echo ""
echo "========================================="
echo "Test Complete!"
echo ""
echo "Expected Results:"
echo "  Test 1: surtax_applicable = true   (after cutoff)"
echo "  Test 2: surtax_applicable = false  (before cutoff)"
echo "  Test 3: surtax_applicable = true   (on or after cutoff)"
echo "  Test 4: Should show constraint error"
