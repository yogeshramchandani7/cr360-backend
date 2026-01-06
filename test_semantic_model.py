#!/usr/bin/env python3
"""
Quick test to verify semantic_model_prod.yaml is working correctly
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_query(query, description):
    print(f"\n{'='*80}")
    print(f"TEST: {description}")
    print(f"Query: {query}")
    print(f"{'='*80}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat",
            json={"query": query, "check_ambiguity": True},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("result", {})
                print(f"✅ SUCCESS")
                print(f"Table used: {result.get('sql', '').split('FROM')[1].split()[0] if 'FROM' in result.get('sql', '') else 'N/A'}")
                print(f"Rows: {result.get('row_count')}")
                print(f"Explanation: {result.get('explanation', '')[:200]}")
            else:
                print(f"❌ FAILED: {data.get('error')}")
        elif response.status_code == 400:
            data = response.json()
            detail = data.get("detail", {})
            if detail.get("is_ambiguous"):
                print(f"⚠️  AMBIGUOUS (taxonomy working!)")
                questions = detail.get("questions", [])
                print(f"Questions asked: {len(questions)}")
                for q in questions:
                    print(f"  - {q.get('question_text')}")
            else:
                print(f"❌ ERROR: {data}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

# Run tests
print("\n" + "="*80)
print("TESTING SEMANTIC_MODEL_PROD.YAML")
print("="*80)

test_query(
    "What is the total outstanding balance for Q4 2024?",
    "Portfolio Total (should use computed_metrics)"
)

test_query(
    "What is the delinquency rate by product for Q4 2024?",
    "Breakdown by Product (should use accounts with GROUP BY)"
)

test_query(
    "Show me charge-off",
    "Ambiguous Query (should detect ambiguity with taxonomy)"
)

test_query(
    "What is the ECL coverage ratio for Q4 2024?",
    "Complex Ratio (should use computed_metrics - pre-computed)"
)

test_query(
    "Show me the average credit score for Q4 2024",
    "Credit Score (restored metric from v2_OLD)"
)

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80 + "\n")
