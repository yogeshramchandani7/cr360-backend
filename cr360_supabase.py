"""
CR360 Supabase Integration
==========================

This module provides the database connection layer for CR360,
connecting to Supabase (PostgreSQL) for credit risk data queries.

Setup:
------
1. Create a Supabase project at https://supabase.com
2. Run cr360_supabase_setup.sql in the SQL Editor
3. Copy your project URL and anon key from Settings > API
4. Set environment variables or update config below

Usage:
------
    from cr360_supabase import CR360Database
    
    db = CR360Database()
    
    # Execute a query
    result = db.execute_query("SELECT * FROM dim_region")
    
    # Or use the Supabase client directly
    data = db.client.table('agg_monthly_summary').select('*').execute()
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SupabaseConfig:
    """Supabase connection configuration"""
    url: str = os.getenv('SUPABASE_URL', 'YOUR_SUPABASE_URL')
    key: str = os.getenv('SUPABASE_KEY', 'YOUR_SUPABASE_ANON_KEY')
    
    # Alternative: Direct PostgreSQL connection
    # Get from Supabase Dashboard > Settings > Database > Connection string
    postgres_url: str = os.getenv('DATABASE_URL', '')


# =============================================================================
# DATABASE CLIENT
# =============================================================================

class CR360Database:
    """
    CR360 Database interface for Supabase
    
    Supports both:
    1. Supabase Python client (simpler, good for basic queries)
    2. Direct PostgreSQL via psycopg2 (full SQL support)
    """
    
    def __init__(self, config: Optional[SupabaseConfig] = None):
        self.config = config or SupabaseConfig()
        self._supabase_client = None
        self._pg_connection = None
    
    # -------------------------------------------------------------------------
    # Supabase Client (REST API)
    # -------------------------------------------------------------------------
    
    @property
    def client(self):
        """Get Supabase client (lazy initialization)"""
        if self._supabase_client is None:
            try:
                from supabase import create_client
                self._supabase_client = create_client(
                    self.config.url, 
                    self.config.key
                )
            except ImportError:
                raise ImportError("Install supabase: pip install supabase")
        return self._supabase_client
    
    def query_table(self, table: str, columns: str = '*', 
                    filters: Dict[str, Any] = None, 
                    limit: int = 1000) -> List[Dict]:
        """
        Query a table using Supabase client
        
        Args:
            table: Table name (e.g., 'agg_monthly_summary')
            columns: Column selection (default '*')
            filters: Dict of column->value filters
            limit: Max rows to return
            
        Returns:
            List of dictionaries
        """
        query = self.client.table(table).select(columns)
        
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        
        result = query.limit(limit).execute()
        return result.data
    
    # -------------------------------------------------------------------------
    # Direct PostgreSQL (Full SQL Support)
    # -------------------------------------------------------------------------
    
    @property
    def pg_connection(self):
        """Get PostgreSQL connection (lazy initialization)"""
        if self._pg_connection is None:
            try:
                import psycopg2
                self._pg_connection = psycopg2.connect(self.config.postgres_url)
            except ImportError:
                raise ImportError("Install psycopg2: pip install psycopg2-binary")
        return self._pg_connection
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict]:
        """
        Execute raw SQL query
        
        Args:
            sql: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            List of dictionaries with column names as keys
        """
        cursor = self.pg_connection.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()
    
    def close(self):
        """Close database connections"""
        if self._pg_connection:
            self._pg_connection.close()
            self._pg_connection = None


# =============================================================================
# CONVENIENCE FUNCTIONS FOR CR360 QUERIES
# =============================================================================

class CR360Queries:
    """
    Pre-built queries for common CR360 analytics
    """
    
    def __init__(self, db: CR360Database):
        self.db = db
    
    def get_portfolio_summary(self, quarter: str = 'Q4-2025') -> Dict:
        """Get high-level portfolio summary"""
        sql = """
        SELECT 
            ROUND(SUM(total_outstanding)::numeric / 1e9, 2) AS portfolio_billions,
            SUM(account_count) AS total_accounts,
            ROUND((SUM(dpd_30_balance) / NULLIF(SUM(total_outstanding), 0) * 100)::numeric, 2) AS delinquency_rate_pct,
            ROUND((SUM(net_charge_off_qtd) * 4 / NULLIF(SUM(total_outstanding), 0) * 100)::numeric, 3) AS annualized_nco_pct
        FROM agg_monthly_summary a
        JOIN dim_date d ON a.as_of_date_skey = d.date_skey
        WHERE d.quarter_name = %s
        """
        result = self.db.execute_query(sql, (quarter,))
        return result[0] if result else {}
    
    def get_regional_comparison(self, quarter: str = 'Q4-2025') -> List[Dict]:
        """Get delinquency comparison by region"""
        sql = """
        SELECT 
            r.region_name,
            ROUND(SUM(a.total_outstanding)::numeric / 1e9, 2) AS outstanding_billions,
            ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2) AS dpd_30_pct,
            ROUND((SUM(a.net_charge_off_qtd) * 4 / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 3) AS annualized_nco_pct
        FROM agg_monthly_summary a
        JOIN dim_date d ON a.as_of_date_skey = d.date_skey
        JOIN dim_region r ON a.region_skey = r.region_skey
        WHERE d.quarter_name = %s
        GROUP BY r.region_name
        ORDER BY dpd_30_pct DESC
        """
        return self.db.execute_query(sql, (quarter,))
    
    def get_segment_analysis(self, region: str = None, quarter: str = 'Q4-2025') -> List[Dict]:
        """Get segment-level analysis, optionally filtered by region"""
        sql = """
        SELECT 
            s.retail_classification AS segment,
            r.region_name,
            ROUND(SUM(a.total_outstanding)::numeric / 1e9, 2) AS outstanding_billions,
            ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2) AS dpd_30_pct,
            ROUND((SUM(a.avg_credit_score * a.total_outstanding) / NULLIF(SUM(a.total_outstanding), 0))::numeric, 0) AS avg_score
        FROM agg_monthly_summary a
        JOIN dim_date d ON a.as_of_date_skey = d.date_skey
        JOIN dim_segment s ON a.segment_skey = s.segment_skey
        JOIN dim_region r ON a.region_skey = r.region_skey
        WHERE d.quarter_name = %s
        """
        params = [quarter]
        
        if region:
            sql += " AND r.region_name = %s"
            params.append(region)
        
        sql += """
        GROUP BY s.retail_classification, r.region_name
        ORDER BY dpd_30_pct DESC
        """
        return self.db.execute_query(sql, tuple(params))
    
    def get_product_performance(self, quarter: str = 'Q4-2025') -> List[Dict]:
        """Get performance by product type"""
        sql = """
        SELECT 
            p.product_type,
            ROUND(SUM(a.total_outstanding)::numeric / 1e9, 2) AS outstanding_billions,
            ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2) AS dpd_30_pct,
            ROUND((SUM(a.net_charge_off_qtd) * 4 / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 3) AS annualized_nco_pct,
            ROUND((SUM(a.avg_credit_score * a.total_outstanding) / NULLIF(SUM(a.total_outstanding), 0))::numeric, 0) AS avg_score
        FROM agg_monthly_summary a
        JOIN dim_date d ON a.as_of_date_skey = d.date_skey
        JOIN dim_product p ON a.product_skey = p.product_skey
        WHERE d.quarter_name = %s
        GROUP BY p.product_type
        ORDER BY outstanding_billions DESC
        """
        return self.db.execute_query(sql, (quarter,))
    
    def get_trend(self, metric: str = 'dpd_30', 
                  dimension: str = 'segment',
                  dimension_value: str = None) -> List[Dict]:
        """
        Get trend over time for a metric
        
        Args:
            metric: 'dpd_30', 'nco', 'score', 'originations'
            dimension: 'region', 'segment', 'product'
            dimension_value: Filter to specific value (e.g., 'Southeast')
        """
        metric_sql = {
            'dpd_30': "ROUND((SUM(a.dpd_30_balance) / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 2)",
            'nco': "ROUND((SUM(a.net_charge_off_qtd) * 4 / NULLIF(SUM(a.total_outstanding), 0) * 100)::numeric, 3)",
            'score': "ROUND((SUM(a.avg_credit_score * a.total_outstanding) / NULLIF(SUM(a.total_outstanding), 0))::numeric, 0)",
            'originations': "ROUND(SUM(a.origination_volume)::numeric / 1e9, 2)"
        }
        
        dimension_config = {
            'region': ('r.region_name', 'dim_region r ON a.region_skey = r.region_skey'),
            'segment': ('s.retail_classification', 'dim_segment s ON a.segment_skey = s.segment_skey'),
            'product': ('p.product_type', 'dim_product p ON a.product_skey = p.product_skey')
        }
        
        dim_col, dim_join = dimension_config.get(dimension, dimension_config['region'])
        
        sql = f"""
        SELECT 
            d.quarter_name,
            {dim_col} AS {dimension},
            {metric_sql.get(metric, metric_sql['dpd_30'])} AS {metric}
        FROM agg_monthly_summary a
        JOIN dim_date d ON a.as_of_date_skey = d.date_skey
        JOIN {dim_join}
        """
        
        params = []
        if dimension_value:
            sql += f" WHERE {dim_col} = %s"
            params.append(dimension_value)
        
        sql += f"""
        GROUP BY d.quarter_name, d.date_skey, {dim_col}
        ORDER BY d.date_skey, {dim_col}
        """
        
        return self.db.execute_query(sql, tuple(params) if params else None)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def demo():
    """Demonstrate CR360 database queries"""
    
    print("=" * 60)
    print("CR360 Supabase Integration Demo")
    print("=" * 60)
    
    # Initialize
    db = CR360Database()
    queries = CR360Queries(db)
    
    # Portfolio summary
    print("\n1. Portfolio Summary (Q4-2025):")
    summary = queries.get_portfolio_summary('Q4-2025')
    print(f"   Total: ${summary.get('portfolio_billions', 'N/A')}B")
    print(f"   Accounts: {summary.get('total_accounts', 'N/A'):,}")
    print(f"   Delinquency: {summary.get('delinquency_rate_pct', 'N/A')}%")
    print(f"   NCO Rate: {summary.get('annualized_nco_pct', 'N/A')}%")
    
    # Regional comparison
    print("\n2. Regional Comparison:")
    regions = queries.get_regional_comparison('Q4-2025')
    for r in regions:
        print(f"   {r['region_name']}: ${r['outstanding_billions']}B | DPD: {r['dpd_30_pct']}%")
    
    # Segment stress
    print("\n3. Southeast Segment Analysis:")
    segments = queries.get_segment_analysis(region='Southeast', quarter='Q4-2025')
    for s in segments:
        print(f"   {s['segment']}: ${s['outstanding_billions']}B | DPD: {s['dpd_30_pct']}% | Score: {s['avg_score']}")
    
    # Trend
    print("\n4. Subprime Delinquency Trend:")
    trend = queries.get_trend(metric='dpd_30', dimension='segment', dimension_value='Subprime')
    for t in trend:
        print(f"   {t['quarter_name']}: {t['dpd_30']}%")
    
    # Cleanup
    db.close()
    print("\n" + "=" * 60)


if __name__ == '__main__':
    demo()
