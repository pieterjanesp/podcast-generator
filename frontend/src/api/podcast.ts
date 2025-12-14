/**
 * API client for podcast generation
 *
 * This module handles HTTP calls to the backend.
 * Keeping API calls separate from React components makes them:
 * - Easier to test
 * - Reusable across components
 * - Framework-agnostic
 */

import type { GenerateRequest, GenerateResponse } from '../types/podcast';

const API_BASE = 'http://localhost:8000';

/**
 * Generate a podcast script for the given topic
 *
 * @param request - Topic and duration configuration
 * @returns The generated script and metadata
 * @throws Error if the request fails
 */
export async function generatePodcast(
  request: GenerateRequest
): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
