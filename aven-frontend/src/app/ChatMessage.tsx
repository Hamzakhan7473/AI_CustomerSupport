'use client';

import { ChatMessage as Message } from './types';
import { useState } from 'react';

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user';
  const hasSuggestions = Array.isArray(message.suggestions) && message.suggestions.length > 0;

  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 1500);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-2 px-2`}>
      <div
        className={`rounded-2xl px-4 py-3 max-w-sm md:max-w-md shadow-sm whitespace-pre-wrap break-words ${
          isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-black'
        }`}
      >
        <p className="text-sm">{message.content}</p>

        {message.timestamp && (
          <p className={`text-xs mt-1 text-right ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        )}

        {hasSuggestions && (
          <div className="flex flex-wrap gap-2 mt-2">
            {message.suggestions!.map((sugg, idx) => (
              <button
                key={idx}
                aria-label={`Copy suggestion: ${sugg}`}
                title={copiedIndex === idx ? 'Copied!' : 'Click to copy'}
                className="bg-black text-white text-xs px-3 py-1 rounded-full hover:opacity-80 transition-all"
                onClick={() => handleCopy(sugg, idx)}
              >
                {copiedIndex === idx ? '✅ Copied' : sugg}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
