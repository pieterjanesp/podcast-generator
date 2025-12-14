/**
 * Type definitions for podcast generation
 */

export interface GenerateRequest {
  topic: string;
  duration_minutes: number;
}

export interface GenerateResponse {
  topic: string;
  duration_minutes: number;
  script: string;
  word_count: number;
}
