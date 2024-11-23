import axios from 'axios';
import { TranscriptionResponse, APIError } from '../types';

const API_URL = 'http://localhost:8000';

export async function transcribeAudio(file: File): Promise<TranscriptionResponse> {
  try {
    const formData = new FormData();
    formData.append('audio', file);

    const response = await axios.post<TranscriptionResponse>(
      `${API_URL}/transcribe`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const apiError: APIError = {
        message: error.response?.data?.detail || 'Error transcribing audio',
        status: error.response?.status
      };
      throw apiError;
    }
    throw { message: 'An unexpected error occurred' };
  }
}