export interface TranscriptionResponse {
  transcription: string;
}

export interface APIError {
  message: string;
  status?: number;
}