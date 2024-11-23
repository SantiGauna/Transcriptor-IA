// import React from 'react';

interface TranscriptionResultProps {
  transcription: string;
}

export function TranscriptionResult({ transcription }: TranscriptionResultProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">
        Resultado de la transcripción
      </h2>
      <div className="bg-gray-50 rounded-lg p-6">
        <p className="text-gray-700 whitespace-pre-wrap">
          {transcription}
        </p>
      </div>
    </div>
  );
}