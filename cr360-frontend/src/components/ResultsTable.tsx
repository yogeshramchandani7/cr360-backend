/**
 * ResultsTable Component
 * Displays query results in a clean, responsive table format
 */

import { logger } from '../utils/logger';

interface ResultsTableProps {
  data: Record<string, any>[];
  explanation?: string;
  sql?: string;
}

export function ResultsTable({ data, explanation, sql }: ResultsTableProps) {
  logger.debug('Rendering ResultsTable', {
    component: 'ResultsTable',
    rowCount: data.length,
    hasExplanation: !!explanation,
    hasSql: !!sql,
  });

  if (!data || data.length === 0) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        textAlign: 'center',
        color: '#6b7280'
      }}>
        <p style={{margin: 0, fontSize: '14px'}}>
          No data found for this query. The database contains data for Q1 2024 through Q4 2025.
        </p>
      </div>
    );
  }

  const columns = Object.keys(data[0]);

  // Format cell values for display
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) {
      return '-';
    }
    if (typeof value === 'number') {
      // Format numbers with commas and 2 decimal places if needed
      return value % 1 === 0
        ? value.toLocaleString()
        : value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    return String(value);
  };

  // Format column headers (convert snake_case to Title Case)
  const formatHeader = (column: string): string => {
    return column
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
      {/* Explanation */}
      {explanation && (
        <div style={{
          backgroundColor: '#eff6ff',
          border: '1px solid #bfdbfe',
          borderRadius: '8px',
          padding: '16px'
        }}>
          <h3 style={{
            fontWeight: '600',
            color: '#1e3a8a',
            marginTop: 0,
            marginBottom: '8px',
            fontSize: '14px'
          }}>
            Explanation
          </h3>
          <p style={{
            color: '#1e40af',
            fontSize: '13px',
            lineHeight: '1.6',
            margin: 0
          }}>
            {explanation}
          </p>
        </div>
      )}

      {/* SQL Query (collapsible) */}
      {sql && (
        <details style={{
          backgroundColor: '#f9fafb',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '16px'
        }}>
          <summary style={{
            fontWeight: '600',
            color: '#374151',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            View SQL Query
          </summary>
          <pre style={{
            marginTop: '12px',
            fontSize: '12px',
            backgroundColor: '#1f2937',
            color: '#10b981',
            padding: '12px',
            borderRadius: '6px',
            overflowX: 'auto',
            marginBottom: 0
          }}>
            {sql}
          </pre>
        </details>
      )}

      {/* Results Table */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        overflow: 'hidden'
      }}>
        <div style={{overflowX: 'auto'}}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse'
          }}>
            <thead style={{backgroundColor: '#f9fafb'}}>
              <tr>
                {columns.map((column) => (
                  <th
                    key={column}
                    style={{
                      padding: '12px 24px',
                      textAlign: 'left',
                      fontSize: '11px',
                      fontWeight: '500',
                      color: '#6b7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      borderBottom: '1px solid #e5e7eb'
                    }}
                  >
                    {formatHeader(column)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  style={{
                    backgroundColor: 'white',
                    borderBottom: rowIndex < data.length - 1 ? '1px solid #e5e7eb' : 'none'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9fafb';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                  }}
                >
                  {columns.map((column) => (
                    <td
                      key={`${rowIndex}-${column}`}
                      style={{
                        padding: '16px 24px',
                        fontSize: '14px',
                        color: '#111827',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      {formatValue(row[column])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Row count footer */}
        <div style={{
          backgroundColor: '#f9fafb',
          padding: '12px 24px',
          fontSize: '13px',
          color: '#6b7280',
          borderTop: '1px solid #e5e7eb'
        }}>
          Showing {data.length} {data.length === 1 ? 'row' : 'rows'}
        </div>
      </div>
    </div>
  );
}
