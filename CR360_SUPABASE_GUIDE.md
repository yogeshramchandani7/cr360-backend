# CR360 Credit Risk Analytics - Setup Guide

## Quick Start with Supabase (Recommended for MVP)

Supabase provides a free PostgreSQL database with a nice API layer - perfect for prototyping.

### Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click "New Project"
4. Choose organization, name it `cr360-prototype`
5. Set a database password (save this!)
6. Select region closest to you
7. Wait ~2 minutes for provisioning

### Step 2: Load the Schema & Data

1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy the entire contents of `cr360_supabase_setup.sql`
4. Paste into the editor
5. Click "Run" (takes ~10 seconds)
6. You should see "Success" messages

### Step 3: Verify Data

Run this test query in SQL Editor:

```sql
SELECT 
    r.region_name,
    ROUND(SUM(a.total_outstanding)::numeric / 1e9, 1) AS outstanding_B,
    ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2) AS dpd_pct
FROM agg_monthly_summary a
JOIN dim_region r ON a.region_skey = r.region_skey
WHERE a.as_of_date_skey = 20251231
GROUP BY r.region_name
ORDER BY dpd_pct DESC;
```

Expected output:
```
region_name  | outstanding_B | dpd_pct
-------------|---------------|--------
Southeast    | 69.1          | 3.24
Northeast    | 48.4          | 1.99
Midwest      | 42.3          | 2.51
West         | 47.0          | 2.09
Canada       | 28.2          | 1.85
```

### Step 4: Get Connection Details

1. Go to **Settings** > **API**
2. Copy:
   - **Project URL**: `https://xxxx.supabase.co`
   - **anon public key**: `eyJhbGc...`

For direct PostgreSQL access:
1. Go to **Settings** > **Database**
2. Copy the **Connection string** (URI format)

### Step 5: Connect from Python

```bash
pip install supabase psycopg2-binary
```

```python
# Option 1: Supabase Client (simple queries)
from supabase import create_client

supabase = create_client(
    "https://xxxx.supabase.co",
    "eyJhbGc..."
)

# Query data
result = supabase.table('agg_monthly_summary').select('*').limit(10).execute()
print(result.data)

# Option 2: Direct PostgreSQL (full SQL support)
import psycopg2

conn = psycopg2.connect("postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres")
cursor = conn.cursor()
cursor.execute("SELECT * FROM dim_region")
print(cursor.fetchall())
```

---

## Files Included

| File | Description |
|------|-------------|
| `cr360_supabase_setup.sql` | PostgreSQL DDL + synthetic data (run this first!) |
| `cr360_supabase.py` | Python integration module with helper queries |
| `cr360_credit_risk_context.yaml` | LLM context file (~20K tokens) |
| `cr360_bp_code_catalog.yaml` | Complete BP code reference (738 codes) |
| `cr360_prototype.db` | SQLite version for offline testing |

---

## Built-In Demo Patterns

The synthetic data includes realistic stress patterns:

| Pattern | Description | Demo Query |
|---------|-------------|------------|
| **Southeast Stress** | Highest volume, worst delinquency | "Compare delinquency by region" |
| **Subprime Deterioration** | DPD rising from 5% → 8%+ | "Show segment trend" |
| **Auto NCO Spike** | Elevated charge-offs | "Which product has highest losses?" |
| **Credit Card Utilization** | 58% in stressed segments | "Any early warning signs?" |
| **Canada Outperforms** | Best credit quality | "Which region is safest?" |

### Sample Investigation Flow

```
User: "What's our total exposure?"
→ $235B across 5 regions, 3 segments

User: "Show delinquency by region"
→ Southeast at 3.24% - highest (alert!)

User: "Why is Southeast so high?"  
→ Subprime segment at 8.06% DPD
→ Auto product showing 18.8% PD
→ Credit card utilization at 58%

User: "Show me the trend"
→ Q1-2024: 5.1% → Q4-2024: 6.3% → Q4-2025: 8.1%
→ Deteriorating for 6 quarters

User: "What's the root cause?"
→ Used car value depreciation + subprime concentration
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CR360 Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Query                                                  │
│      │                                                       │
│      ▼                                                       │
│  ┌─────────────────┐    ┌──────────────────────┐            │
│  │   Gemini 2.5    │◄───│ cr360_context.yaml   │            │
│  │   Flash LLM     │    │ (schema + metrics)   │            │
│  └────────┬────────┘    └──────────────────────┘            │
│           │                                                  │
│           │ Generated SQL                                    │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │    Supabase     │  ← PostgreSQL + REST API               │
│  │   (Free Tier)   │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           │ Query Results                                    │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │  Visualization  │  ← Charts + Tables                     │
│  │   + Response    │                                        │
│  └─────────────────┘                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Cost Comparison

| Option | Setup | Cost | Best For |
|--------|-------|------|----------|
| **Supabase Free** | 5 min | $0 | MVP/Prototype ✓ |
| SQLite | 1 min | $0 | Local testing |
| Supabase Pro | 5 min | $25/mo | Production |
| Snowflake | 30 min | ~$50/mo+ | Enterprise |

**Recommendation**: Start with Supabase Free tier. It includes:
- 500 MB database storage
- 2 GB bandwidth/month  
- Unlimited API requests
- Enough for MVP and demos

---

## Next Steps

1. ✅ Set up Supabase (15 min)
2. 🔲 Load context YAML into Gemini prompt
3. 🔲 Build FastAPI endpoint for query execution
4. 🔲 Add visualization layer (Plotly/Recharts)
5. 🔲 Create demo script with sample questions

---

## Environment Variables

```bash
# .env file
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres

# Gemini API (for LLM)
GOOGLE_API_KEY=your_gemini_key
```

---

## Troubleshooting

**"relation does not exist" error**
- Make sure you ran the full `cr360_supabase_setup.sql` script

**Connection timeout**
- Check if your IP is allowed in Supabase Network settings
- Try the direct PostgreSQL connection instead of REST API

**Empty results**
- Verify data loaded: `SELECT COUNT(*) FROM agg_monthly_summary`
- Should return ~70+ rows

---

*CR360 Prototype - December 2025*
