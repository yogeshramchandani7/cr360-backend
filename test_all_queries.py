#!/usr/bin/env python3
"""
Test all 20 queries from TEST_QUERIES.md
Handles ambiguous queries with automatic clarification
"""

import requests
import json
from typing import Dict, Any, List, Optional
import time

API_BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

# Test queries organized by category
QUERIES = {
    "Category 1: Portfolio-Level Aggregates": [
        {
            "id": 1,
            "query": "What is the total outstanding balance for the latest quarter?",
            "expected": "Success, 1 row, uses computed_metrics"
        },
        {
            "id": 2,
            "query": "Show me the total outstanding balance for Q4 2024",
            "expected": "Success, 1 row, specific value"
        },
        {
            "id": 3,
            "query": "What is the 30+ day delinquency rate for Q4 2024?",
            "expected": "Success, 1 row, percentage"
        },
        {
            "id": 4,
            "query": "What is the ECL coverage ratio for the latest quarter?",
            "expected": "Success, 1 row from computed_metrics"
        },
    ],
    "Category 2: Breakdowns by Dimension": [
        {
            "id": 5,
            "query": "Show me outstanding balance by product for Q4 2024",
            "expected": "Success, 5 rows (MTG, AUTO, CC, PL, HELOC)"
        },
        {
            "id": 6,
            "query": "What is the outstanding balance by region for the latest quarter?",
            "expected": "Success, 5 rows (regions)"
        },
        {
            "id": 7,
            "query": "Show me delinquency rates by customer segment for Q4 2024",
            "expected": "Success, multiple rows with segments"
        },
        {
            "id": 8,
            "query": "Compare outstanding balance across products and regions for Q4 2024",
            "expected": "Success, multiple rows with 2 dimensions"
        },
    ],
    "Category 3: Ambiguous Queries": [
        {
            "id": 9,
            "query": "What is the total outstanding balance?",
            "expected": "Ambiguity - missing time period",
            "clarifications": {
                "time_period": "Q4 2024"  # Will be mapped to question_id
            }
        },
        {
            "id": 10,
            "query": "Show me delinquency rates",
            "expected": "Ambiguity - missing time period and dimension",
            "clarifications": {
                "time_period": "Q4 2024"
            }
        },
        {
            "id": 11,
            "query": "What is the ECL?",
            "expected": "Ambiguity - unclear metric, missing time period",
            "clarifications": {
                "ecl_type": "Total ECL",
                "time_period": "Q4 2024"
            }
        },
        {
            "id": 12,
            "query": "Show me the data",
            "expected": "Ambiguity - extremely vague",
            "clarifications": {
                "metric": "Outstanding Balance",
                "time_period": "Q4 2024"
            }
        },
    ],
    "Category 4: Time-Based Queries": [
        {
            "id": 13,
            "query": "Show me all available quarters in the data",
            "expected": "Success, 8 rows (Q1 2024 through Q4 2025)"
        },
        {
            "id": 14,
            "query": "What is the outstanding balance trend over all quarters?",
            "expected": "Success, 8 rows with quarterly data"
        },
        {
            "id": 15,
            "query": "Compare Q1 2024 vs Q4 2025 outstanding balance",
            "expected": "Success, 2 rows or comparative analysis"
        },
    ],
    "Category 5: Edge Cases - No Data": [
        {
            "id": 16,
            "query": "What is the total outstanding balance for Q3 2023?",
            "expected": "Success but 0 rows (data doesn't exist)"
        },
        {
            "id": 17,
            "query": "Show me outstanding balance for December 2020",
            "expected": "Success but 0 rows (before data range)"
        },
    ],
    "Category 6: Complex Metrics": [
        {
            "id": 18,
            "query": "What is the net charge-off rate for Q4 2024?",
            "expected": "Success, 1 row from computed_metrics"
        },
        {
            "id": 19,
            "query": "Show me the number of accounts by ECL stage for the latest quarter",
            "expected": "Success, 3 rows (Stage 1, 2, 3)"
        },
        {
            "id": 20,
            "query": "What is the average credit score for subprime customers in the Southeast region for Q4 2024?",
            "expected": "Success, 1 row, complex multi-filter query"
        },
    ],
}


def send_query(query: str, clarifications: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Send a query to the API"""
    url = f"{API_BASE_URL}/api/{API_VERSION}/chat"

    payload = {
        "query": query,
        "check_ambiguity": True if not clarifications else False
    }

    if clarifications:
        payload["clarifications"] = clarifications

    response = requests.post(url, json=payload)

    # For chat endpoint, 400 can be valid (ambiguity)
    if response.status_code == 400:
        # Extract detail field which contains actual response
        data = response.json()
        return data.get("detail", data)

    response.raise_for_status()
    return response.json()


def handle_ambiguous_query(query: str, questions: List[Dict], predefined_clarifications: Dict[str, str]) -> Dict[str, Any]:
    """Handle ambiguous query by providing clarifications"""
    print(f"  ⚠️  Query is ambiguous. Questions received:")

    clarifications = []

    for question in questions:
        question_id = question["question_id"]
        question_text = question["question_text"]
        options = question["options"]

        print(f"     Q: {question_text}")
        print(f"     Options: {', '.join(options)}")

        # Try to find matching clarification from predefined ones
        selected_option = None

        # Map predefined clarifications to actual options
        if question_id in predefined_clarifications:
            desired_value = predefined_clarifications[question_id]
            # Find matching option (case-insensitive partial match)
            for option in options:
                if desired_value.lower() in option.lower() or option.lower() in desired_value.lower():
                    selected_option = option
                    break

        # If no predefined match, select first option
        if not selected_option:
            selected_option = options[0]

        print(f"     Selected: {selected_option}")

        clarifications.append({
            "question_id": question_id,
            "selected_option": selected_option
        })

    print(f"  🔄 Sending clarified query...")

    # Send query again with clarifications
    return send_query(query, clarifications)


def format_result(response: Dict[str, Any], query_id: int, query: str) -> str:
    """Format query result for display"""
    result = f"\n{'='*80}\n"
    result += f"Query {query_id}: {query}\n"
    result += f"{'-'*80}\n"

    if response.get("success"):
        # Success response
        result_data = response.get("result", {})
        results = result_data.get("results", [])
        row_count = result_data.get("row_count", len(results))
        sql = result_data.get("sql", "")
        explanation = result_data.get("explanation", "")

        result += f"✅ SUCCESS\n"
        result += f"Rows: {row_count}\n"
        result += f"Explanation: {explanation}\n"
        result += f"SQL: {sql}\n\n"

        if results:
            result += "Results:\n"
            # Show first 5 rows
            for i, row in enumerate(results[:5], 1):
                result += f"  Row {i}: {json.dumps(row, indent=2)}\n"

            if row_count > 5:
                result += f"  ... and {row_count - 5} more rows\n"
        else:
            result += "No data returned (0 rows)\n"

    elif response.get("is_ambiguous"):
        result += f"⚠️  AMBIGUOUS (Handled with clarifications)\n"

    else:
        # Error response
        error_type = response.get("error_type", "Unknown")
        error_msg = response.get("error", "Unknown error")

        result += f"❌ ERROR\n"
        result += f"Type: {error_type}\n"
        result += f"Message: {error_msg}\n"

    result += f"{'='*80}\n"

    return result


def run_all_tests():
    """Run all test queries"""
    print("\n" + "="*80)
    print("CR360 Test Suite - Running All 20 Queries")
    print("="*80 + "\n")

    total_queries = 0
    successful_queries = 0
    ambiguous_resolved = 0
    failed_queries = 0
    no_data_queries = 0

    all_results = []

    for category, queries in QUERIES.items():
        print(f"\n{'#'*80}")
        print(f"# {category}")
        print(f"{'#'*80}\n")

        for query_data in queries:
            query_id = query_data["id"]
            query = query_data["query"]
            expected = query_data["expected"]
            predefined_clarifications = query_data.get("clarifications", {})

            total_queries += 1

            print(f"Query {query_id}: {query}")
            print(f"Expected: {expected}")

            try:
                # Send initial query
                response = send_query(query)

                # Handle ambiguous queries
                if response.get("is_ambiguous"):
                    questions = response.get("questions", [])

                    if questions and predefined_clarifications:
                        # Handle with clarifications
                        response = handle_ambiguous_query(query, questions, predefined_clarifications)
                        ambiguous_resolved += 1
                    else:
                        print(f"  ⚠️  Ambiguous but no clarifications provided")

                # Check final result
                if response.get("success"):
                    row_count = response.get("result", {}).get("row_count", 0)

                    if row_count == 0:
                        no_data_queries += 1
                        print(f"  ✅ Success (0 rows - expected for edge cases)")
                    else:
                        successful_queries += 1
                        print(f"  ✅ Success ({row_count} rows)")
                else:
                    if not response.get("is_ambiguous"):
                        failed_queries += 1
                        print(f"  ❌ Failed: {response.get('error', 'Unknown error')}")

                # Format and store result
                result_text = format_result(response, query_id, query)
                all_results.append(result_text)

            except Exception as e:
                failed_queries += 1
                print(f"  ❌ Exception: {str(e)}")
                all_results.append(f"\nQuery {query_id}: {query}\n❌ EXCEPTION: {str(e)}\n")

            # Small delay between queries
            time.sleep(0.5)

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Queries:           {total_queries}")
    print(f"Successful:              {successful_queries}")
    print(f"Ambiguous (Resolved):    {ambiguous_resolved}")
    print(f"No Data (Expected):      {no_data_queries}")
    print(f"Failed:                  {failed_queries}")
    print(f"Pass Rate:               {((successful_queries + ambiguous_resolved + no_data_queries) / total_queries * 100):.1f}%")
    print("="*80 + "\n")

    # Write detailed results to file
    with open("test_results.txt", "w") as f:
        f.write("CR360 Test Results\n")
        f.write("="*80 + "\n\n")
        for result in all_results:
            f.write(result)

        f.write("\n\nTEST SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Total Queries:           {total_queries}\n")
        f.write(f"Successful:              {successful_queries}\n")
        f.write(f"Ambiguous (Resolved):    {ambiguous_resolved}\n")
        f.write(f"No Data (Expected):      {no_data_queries}\n")
        f.write(f"Failed:                  {failed_queries}\n")
        f.write(f"Pass Rate:               {((successful_queries + ambiguous_resolved + no_data_queries) / total_queries * 100):.1f}%\n")

    print("✅ Detailed results written to: test_results.txt")


if __name__ == "__main__":
    run_all_tests()
