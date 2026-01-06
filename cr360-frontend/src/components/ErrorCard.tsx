/**
 * ErrorCard Component
 * Displays error messages in a user-friendly format
 */

import { logger } from '../utils/logger';

interface ErrorCardProps {
  errorType: string;
  message: string;
  details?: any;
}

export function ErrorCard({ errorType, message, details }: ErrorCardProps) {
  logger.error('Displaying error', null, {
    component: 'ErrorCard',
    errorType,
    message,
    details,
  });

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-lg font-semibold text-red-900">
            {errorType || 'Error'}
          </h3>
          <p className="mt-1 text-sm text-red-800">{message}</p>
          {details && (
            <details className="mt-3">
              <summary className="text-xs text-red-700 cursor-pointer hover:text-red-900">
                Show details
              </summary>
              <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(details, null, 2)}
              </pre>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
