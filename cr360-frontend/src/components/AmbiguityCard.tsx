/**
 * AmbiguityCard Component
 * Displays interactive clarification questions and fallback suggestions
 */

import { useState } from 'react';
import { logger } from '../utils/logger';
import type { ClarificationQuestion, Clarification } from '../types/api';

interface AmbiguityCardProps {
  message: string;
  reasons: string[];
  suggestions: string[];
  questions: ClarificationQuestion[];
  originalQuery: string;
  onSuggestionClick?: (suggestion: string) => void;
  onClarificationSubmit?: (clarifications: Clarification[], originalQuery: string) => void;
}

export function AmbiguityCard({
  message,
  reasons,
  suggestions,
  questions,
  originalQuery,
  onSuggestionClick,
  onClarificationSubmit,
}: AmbiguityCardProps) {
  const [selections, setSelections] = useState<Record<string, string>>({});

  logger.debug('Rendering AmbiguityCard', {
    component: 'AmbiguityCard',
    reasonCount: reasons.length,
    suggestionCount: suggestions.length,
    questionCount: questions.length,
  });

  const handleOptionSelect = (questionId: string, option: string) => {
    setSelections(prev => ({
      ...prev,
      [questionId]: option
    }));
    logger.debug('Option selected', { questionId, option });
  };

  const handleSubmit = () => {
    const clarifications: Clarification[] = Object.entries(selections).map(
      ([question_id, selected_option]) => ({
        question_id,
        selected_option,
      })
    );

    logger.info('Submitting clarifications', {
      clarificationCount: clarifications.length,
      clarifications,
      originalQuery,
    });

    onClarificationSubmit?.(clarifications, originalQuery);
  };

  const allQuestionsAnswered = questions.length > 0 &&
    questions.every(q => selections[q.question_id]);

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-yellow-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-lg font-semibold text-yellow-900">
            Query Needs Clarification
          </h3>
          <p className="mt-1 text-sm text-yellow-800">{message}</p>
        </div>
      </div>

      {/* Reasons */}
      {reasons.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-yellow-900 mb-2">
            Why is this ambiguous?
          </h4>
          <ul className="list-disc list-inside space-y-1">
            {reasons.map((reason, index) => (
              <li key={index} className="text-sm text-yellow-800">
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Interactive Questions (NEW) */}
      {questions.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-yellow-900 mb-3">
            Please clarify:
          </h4>

          {questions.map((question) => (
            <div key={question.question_id} className="mb-4">
              <p className="text-sm font-medium text-yellow-900 mb-2">
                {question.question_text}
              </p>

              <div className="space-y-2">
                {question.options.map((option) => (
                  <button
                    key={option}
                    onClick={() => handleOptionSelect(question.question_id, option)}
                    className={`w-full text-left px-4 py-2.5 rounded-md text-sm transition-all ${
                      selections[question.question_id] === option
                        ? 'bg-blue-100 border-2 border-blue-500 text-blue-900 font-semibold'
                        : 'bg-white border border-yellow-300 text-yellow-900 hover:bg-yellow-100 hover:border-yellow-400'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          ))}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={!allQuestionsAnswered}
            className={`w-full px-4 py-3 rounded-md text-sm font-semibold transition-colors ${
              allQuestionsAnswered
                ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Submit Clarifications
          </button>
        </div>
      )}

      {/* Fallback Suggestions (shown when no structured questions available) */}
      {questions.length === 0 && suggestions.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-yellow-900 mb-2">
            Try asking:
          </h4>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => onSuggestionClick?.(suggestion)}
                className="w-full text-left px-4 py-2 bg-white border border-yellow-300 rounded-md text-sm text-yellow-900 hover:bg-yellow-100 hover:border-yellow-400 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
