/**
 * LoadingSpinner Component
 * Simple loading indicator
 */

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="flex flex-col items-center space-y-3">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="text-sm text-gray-600">Processing your query...</p>
      </div>
    </div>
  );
}
