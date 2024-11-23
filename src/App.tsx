import React, { useState, useRef } from 'react';
import { FileUploader } from './components/FileUploader';
import { FilePreview } from './components/FilePreview';
import { TranscriptionResult } from './components/TranscriptionResult';
import { transcribeAudio } from './services/api';
import { APIError } from './types';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [transcription, setTranscription] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setTranscription('');
    setError('');
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile?.type.startsWith('audio/')) {
      handleFileSelect(droppedFile);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleTranscribe = async () => {
    if (!file) return;

    setLoading(true);
    setError('');

    try {
      const result = await transcribeAudio(file);
      setTranscription(result.transcription);
    } catch (err) {
      const apiError = err as APIError;
      setError(apiError.message);
      setTranscription('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            AI Audio Transcription
          </h1>
          <p className="text-gray-600">
          Sube tu archivo de audio y obtén una transcripción precisa impulsada por IA
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <FileUploader
            onFileSelect={handleFileSelect}
            fileInputRef={fileInputRef}
            handleDrop={handleDrop}
            handleDragOver={handleDragOver}
          />

          {file && (
            <FilePreview
              file={file}
              loading={loading}
              onTranscribe={handleTranscribe}
            />
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">
              {error}
            </div>
          )}
        </div>

        {transcription && <TranscriptionResult transcription={transcription} />}
      </div>
    </div>
  );
}

export default App;