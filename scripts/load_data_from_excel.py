#!/usr/bin/env python3
"""
Data Loading Script for CR360 Schema Migration
Loads account-level data from Excel into PostgreSQL (Supabase)

Usage:
    python scripts/load_data_from_excel.py

Requirements:
    - pandas
    - psycopg2-binary
    - openpyxl (for Excel reading)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
from app.config import settings
import psycopg2
from psycopg2.extras import execute_values

# Configuration
EXCEL_FILE = 'CR360__Synthetic Data.xlsx'
ACCOUNTS_SHEET = 'Accounts Data'
METRICS_SHEET = 'computed metrics'

def get_db_connection():
    """Create direct PostgreSQL connection"""
    # Parse DATABASE_URL
    db_url = settings.DATABASE_URL

    # Extract components from connection string
    # Format: postgresql://user:pass@host:port/dbname
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
    if not match:
        raise ValueError("Invalid DATABASE_URL format")

    user, password, host, port, dbname = match.groups()

    conn = psycopg2.connect(
        host=host,
        port=int(port),
        dbname=dbname,
        user=user,
        password=password
    )
    return conn

def clean_dataframe(df):
    """Clean Excel dataframe - remove metadata rows"""
    # Remove rows where row_type starts with _ (metadata rows)
    df = df[~df['row_type'].astype(str).str.startswith('_')].copy()

    # Drop row_type column
    df = df.drop(columns=['row_type'])

    # Replace NaN with None for SQL NULL
    df = df.where(pd.notna(df), None)

    return df

def convert_date_columns(df, date_cols):
    """Convert date columns to proper datetime format"""
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def load_accounts_data(conn):
    """Load accounts data from Excel into accounts table"""
    print(f"\n{'='*80}")
    print("LOADING ACCOUNTS DATA")
    print(f"{'='*80}")

    # Read Excel file
    print(f"Reading {EXCEL_FILE} - Sheet: {ACCOUNTS_SHEET}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=ACCOUNTS_SHEET, header=0, skiprows=[1, 2])
    print(f"  Rows read: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    # Clean data
    print("\nCleaning data...")
    df = clean_dataframe(df)
    print(f"  Rows after cleaning: {len(df)}")

    # Convert date columns
    date_cols = ['as_of_date', 'origination_date', 'funded_date', 'last_payment_date']
    df = convert_date_columns(df, date_cols)

    # Show sample
    print(f"\nSample data (first 2 rows):")
    print(df[['account_id', 'product_code', 'region_code', 'as_of_date', 'adjusted_eop_balance']].head(2))

    # Prepare data for insertion
    print(f"\nPreparing data for insertion...")
    columns = df.columns.tolist()

    # Create INSERT statement (composite PK: account_id + as_of_date)
    insert_sql = f"""
        INSERT INTO accounts ({', '.join(columns)})
        VALUES %s
        ON CONFLICT (account_id, as_of_date) DO UPDATE SET
            adjusted_eop_balance = EXCLUDED.adjusted_eop_balance,
            days_past_due = EXCLUDED.days_past_due,
            account_status = EXCLUDED.account_status
    """

    # Convert to list of tuples
    data_tuples = [tuple(row) for row in df.values]

    # Execute batch insert
    print(f"Inserting {len(data_tuples)} rows into accounts table...")
    cursor = conn.cursor()
    try:
        execute_values(cursor, insert_sql, data_tuples, page_size=100)
        conn.commit()
        print(f"✅ Successfully inserted {len(data_tuples)} accounts")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting data: {e}")
        raise
    finally:
        cursor.close()

    # Verify insertion
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM accounts")
    count = cursor.fetchone()[0]
    cursor.close()
    print(f"\nVerification: {count} total rows in accounts table")

    return count

def load_computed_metrics(conn):
    """Load computed metrics from Excel into computed_metrics table"""
    print(f"\n{'='*80}")
    print("LOADING COMPUTED METRICS DATA")
    print(f"{'='*80}")

    try:
        # Read Excel file
        print(f"Reading {EXCEL_FILE} - Sheet: {METRICS_SHEET}")
        df = pd.read_excel(EXCEL_FILE, sheet_name=METRICS_SHEET, header=0, skiprows=[1, 2])
        print(f"  Rows read: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Clean data
        print("\nCleaning data...")
        df = clean_dataframe(df)
        print(f"  Rows after cleaning: {len(df)}")

        # Convert as_of_date
        df = convert_date_columns(df, ['as_of_date'])

        # Show sample
        print(f"\nSample data (first 2 rows):")
        cols_to_show = ['as_of_date', 'total_outstanding_balance', 'total_accounts', 'delinquency_rate_30_plus']
        available_cols = [c for c in cols_to_show if c in df.columns]
        if available_cols:
            print(df[available_cols].head(2))

        # Prepare data for insertion
        print(f"\nPreparing data for insertion...")
        columns = df.columns.tolist()

        # Create INSERT statement with conflict handling
        insert_sql = f"""
            INSERT INTO computed_metrics ({', '.join(columns)})
            VALUES %s
            ON CONFLICT (as_of_date) DO UPDATE SET
                total_outstanding_balance = EXCLUDED.total_outstanding_balance,
                total_accounts = EXCLUDED.total_accounts,
                num_active_accounts = EXCLUDED.num_active_accounts
        """

        # Convert to list of tuples
        data_tuples = [tuple(row) for row in df.values]

        # Execute batch insert
        print(f"Inserting {len(data_tuples)} rows into computed_metrics table...")
        cursor = conn.cursor()
        try:
            execute_values(cursor, insert_sql, data_tuples, page_size=10)
            conn.commit()
            print(f"✅ Successfully inserted {len(data_tuples)} metric records")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error inserting data: {e}")
            print(f"   Skipping computed_metrics (may need manual adjustment)")
            return 0
        finally:
            cursor.close()

        # Verify insertion
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM computed_metrics")
        count = cursor.fetchone()[0]
        cursor.close()
        print(f"\nVerification: {count} total rows in computed_metrics table")

        return count

    except Exception as e:
        print(f"⚠️  Warning: Could not load computed_metrics: {e}")
        print("   This is optional - accounts table is the primary data source")
        return 0

def verify_data_quality(conn):
    """Run basic data quality checks"""
    print(f"\n{'='*80}")
    print("DATA QUALITY CHECKS")
    print(f"{'='*80}")

    cursor = conn.cursor()

    # Check 1: Total accounts by product
    print("\n1. Accounts by Product:")
    cursor.execute("""
        SELECT product_code, COUNT(*) as count
        FROM accounts
        GROUP BY product_code
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Check 2: Accounts by region
    print("\n2. Accounts by Region:")
    cursor.execute("""
        SELECT region_code, COUNT(*) as count
        FROM accounts
        GROUP BY region_code
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Check 3: Accounts by as_of_date
    print("\n3. Accounts by Date:")
    cursor.execute("""
        SELECT as_of_date, COUNT(*) as count
        FROM accounts
        GROUP BY as_of_date
        ORDER BY as_of_date
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Check 4: Total balance by product
    print("\n4. Total Balance by Product (in billions):")
    cursor.execute("""
        SELECT
            product_code,
            ROUND(SUM(adjusted_eop_balance)::numeric / 1e9, 2) as total_balance_b
        FROM accounts
        WHERE as_of_date = (SELECT MAX(as_of_date) FROM accounts)
        GROUP BY product_code
        ORDER BY total_balance_b DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: ${row[1]}B")

    cursor.close()

def main():
    """Main execution function"""
    print(f"\n{'#'*80}")
    print("CR360 DATA LOADING SCRIPT")
    print(f"{'#'*80}")
    print(f"Started at: {datetime.now()}")

    # Check if Excel file exists
    if not os.path.exists(EXCEL_FILE):
        print(f"\n❌ ERROR: Excel file not found: {EXCEL_FILE}")
        print("   Please ensure the file is in the current directory")
        return 1

    try:
        # Connect to database
        print("\nConnecting to database...")
        conn = get_db_connection()
        print("✅ Connected successfully")

        # Load accounts data
        accounts_count = load_accounts_data(conn)

        # Load computed metrics (optional)
        metrics_count = load_computed_metrics(conn)

        # Verify data quality
        verify_data_quality(conn)

        # Close connection
        conn.close()

        # Summary
        print(f"\n{'='*80}")
        print("MIGRATION SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Accounts loaded: {accounts_count}")
        print(f"✅ Computed metrics loaded: {metrics_count}")
        print(f"\nCompleted at: {datetime.now()}")
        print(f"{'#'*80}\n")

        return 0

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
