# CR360 Test Queries

Comprehensive test suite covering all query types, edge cases, and expected behaviors.

---

## Category 1: Portfolio-Level Aggregates
*Should use `computed_metrics` table for efficiency*

### Query 1
**Input:** "What is the total outstanding balance for the latest quarter?"

**Expected:**
- ✅ Success
- 1 row
- Uses `computed_metrics` table
- Returns single aggregate value

---

### Query 2
**Input:** "Show me the total outstanding balance for Q4 2024"

**Expected:**
- ✅ Success
- 1 row
- Specific value for Q4 2024
- Uses `computed_metrics` table

---

### Query 3
**Input:** "What is the 30+ day delinquency rate for Q4 2024?"

**Expected:**
- ✅ Success
- 1 row
- Returns percentage value
- Uses `computed_metrics` table

---

### Query 4
**Input:** "What is the ECL coverage ratio for the latest quarter?"

**Expected:**
- ✅ Success
- 1 row
- Returns ratio from `computed_metrics`
- Latest quarter = Q4 2025

---

## Category 2: Breakdowns by Dimension
*Should use `accounts` table for dimensional analysis*

### Query 5
**Input:** "Show me outstanding balance by product for Q4 2024"

**Expected:**
- ✅ Success
- 5 rows (MTG, AUTO, CC, PL, HELOC)
- Uses `accounts` table
- Groups by `product_type`

---

### Query 6
**Input:** "What is the outstanding balance by region for the latest quarter?"

**Expected:**
- ✅ Success
- 5 rows (Northeast, Southeast, Midwest, Southwest, West)
- Uses `accounts` table
- Groups by `region`

---

### Query 7
**Input:** "Show me delinquency rates by customer segment for Q4 2024"

**Expected:**
- ✅ Success
- Multiple rows (Prime, Near-Prime, Subprime)
- Uses `accounts` table
- Groups by `customer_segment`
- Calculates delinquency rate per segment

---

### Query 8
**Input:** "Compare outstanding balance across products and regions for Q4 2024"

**Expected:**
- ✅ Success
- Multiple rows (5 products × 5 regions = up to 25 rows)
- Uses `accounts` table
- Groups by both `product_type` AND `region`

---

## Category 3: Ambiguous Queries
*Should trigger interactive clarification questions*

### Query 9
**Input:** "What is the total outstanding balance?"

**Expected:**
- ⚠️ Ambiguous
- Missing: Time period
- Interactive question: "Which quarter do you want to see?"
- Options: Q1 2024, Q2 2024, Q3 2024, Q4 2024, Q1 2025, Q2 2025, Q3 2025, Q4 2025

---

### Query 10
**Input:** "Show me delinquency rates"

**Expected:**
- ⚠️ Ambiguous
- Missing: Time period, possibly dimension
- Interactive questions:
  1. "Which quarter?" → Q1-Q4 2024, Q1-Q4 2025
  2. "For the entire portfolio or by dimension?" → Total / By Product / By Region / By Segment

---

### Query 11
**Input:** "What is the ECL?"

**Expected:**
- ⚠️ Ambiguous
- Missing: Time period, unclear metric variant
- Interactive questions:
  1. "Which ECL metric?" → Total ECL / ECL Coverage Ratio / ECL by Stage
  2. "Which quarter?" → Q1-Q4 2024, Q1-Q4 2025

---

### Query 12
**Input:** "Show me the data"

**Expected:**
- ⚠️ Extremely ambiguous
- Missing: Everything (metric, time period, dimension)
- Interactive questions:
  1. "Which metric?" → Outstanding Balance / Delinquency Rate / Charge-off / Account Count
  2. "Which quarter?" → Q1-Q4 2024, Q1-Q4 2025
  3. "View by?" → Total / By Product / By Region / By Segment

---

## Category 4: Time-Based Queries
*Should handle temporal analysis and comparisons*

### Query 13
**Input:** "Show me all available quarters in the data"

**Expected:**
- ✅ Success
- 8 rows (Q1 2024, Q2 2024, Q3 2024, Q4 2024, Q1 2025, Q2 2025, Q3 2025, Q4 2025)
- Uses `DISTINCT as_of_date` from either table
- Returns list of quarters

---

### Query 14
**Input:** "What is the outstanding balance trend over all quarters?"

**Expected:**
- ✅ Success
- 8 rows (one per quarter)
- Uses `computed_metrics` table
- Returns time series data
- Sorted chronologically

---

### Query 15
**Input:** "Compare Q1 2024 vs Q4 2025 outstanding balance"

**Expected:**
- ✅ Success
- 2 rows OR 1 row with comparative values
- Uses `computed_metrics` table
- Shows values for both quarters
- May include delta/percentage change

---

## Category 5: Edge Cases - No Data
*Should handle gracefully when data doesn't exist*

### Query 16
**Input:** "What is the total outstanding balance for Q3 2023?"

**Expected:**
- ✅ Success (valid query structure)
- 0 rows (data doesn't exist for Q3 2023)
- Message: "No results found for the specified period"
- Data range: Q1 2024 - Q4 2025 only

---

### Query 17
**Input:** "Show me outstanding balance for December 2020"

**Expected:**
- ✅ Success (valid query structure)
- 0 rows (before data range)
- Message: "No results found for the specified period"
- May suggest available date range

---

## Category 6: Complex Metrics
*Should handle advanced calculations and multi-dimensional analysis*

### Query 18
**Input:** "What is the net charge-off rate for Q4 2024?"

**Expected:**
- ✅ Success
- 1 row
- Uses `computed_metrics` table
- Returns percentage
- Metric: `net_charge_off_rate`

---

### Query 19
**Input:** "Show me the number of accounts by ECL stage for the latest quarter"

**Expected:**
- ✅ Success
- 3 rows (Stage 1, Stage 2, Stage 3)
- Uses `accounts` table
- Groups by `ecl_stage`
- Returns COUNT of accounts per stage
- Latest quarter = Q4 2025

---

### Query 20
**Input:** "What is the average credit score for subprime customers in the Southeast region for Q4 2024?"

**Expected:**
- ✅ Success
- 1 row
- Uses `accounts` table
- Filters: `customer_segment = 'Subprime'` AND `region = 'Southeast'` AND `as_of_date = '2024-10-01'`
- Returns AVG(`credit_score`)
- Complex multi-filter query

---

## Summary of Expected Results

| Category | Total Queries | Success | Ambiguous | No Data |
|----------|---------------|---------|-----------|---------|
| Portfolio-Level Aggregates | 4 | 4 | 0 | 0 |
| Breakdowns by Dimension | 4 | 4 | 0 | 0 |
| Ambiguous Queries | 4 | 0 | 4 | 0 |
| Time-Based Queries | 3 | 3 | 0 | 0 |
| Edge Cases - No Data | 2 | 2 | 0 | 2* |
| Complex Metrics | 3 | 3 | 0 | 0 |
| **TOTAL** | **20** | **16** | **4** | **2*** |

\* Success with 0 rows returned

---

## Testing Checklist

- [ ] All 4 portfolio-level queries return correct aggregates
- [ ] All 4 breakdown queries group correctly by dimensions
- [ ] All 4 ambiguous queries trigger interactive clarification
- [ ] All 3 time-based queries handle temporal logic
- [ ] Both edge cases return gracefully with 0 rows
- [ ] All 3 complex metric queries calculate correctly

**Target Pass Rate:** 100% (20/20 queries handle correctly)
- Direct success: 16 queries
- Interactive clarification: 4 queries
- Graceful no-data handling: 2 queries (subset of success)

---

## Notes

1. **Ambiguous Query Flow:**
   - Backend detects ambiguity
   - Returns structured `questions` array
   - Frontend displays interactive buttons
   - User selects options
   - Frontend sends clarified query with original context
   - Backend processes without re-checking ambiguity

2. **Data Range:**
   - Available quarters: Q1 2024 through Q4 2025
   - Queries outside this range should return 0 rows gracefully

3. **Table Selection:**
   - `computed_metrics`: Portfolio-level aggregates (faster)
   - `accounts`: Dimensional breakdowns, filtered queries

4. **Visualization Hints:**
   - Single value → `table`
   - Time series → `line`
   - Breakdown by 1 dimension → `bar` or `horizontal_bar`
   - Breakdown by 2 dimensions → `table`
