// import React from 'react';
import { FileAudio, Headphones, Loader2 } from 'lucide-react';

interface FilePreviewProps {
  file: File;
  loading: boolean;
  onTranscribe: () => void;
}

export function FilePreview({ file, loading, onTranscribe }: FilePreviewProps) {
  return (
    <div className="mt-6">
      <div className="flex items-center gap-3 p-4 bg-purple-50 rounded-lg">
        <FileAudio className="text-purple-500" />
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-700">
            {file.name}
          </p>
          <p className="text-xs text-gray-500">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
        <button
          onClick={onTranscribe}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:bg-purple-300 flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Transcribiendo...
            </>
          ) : (
            <>
              <Headphones className="w-4 h-4" />
              Transcribe
            </>
          )}
        </button>
      </div>
    </div>
  );
}