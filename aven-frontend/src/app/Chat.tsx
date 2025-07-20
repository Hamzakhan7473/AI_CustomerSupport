'use client';

import React, { useRef, useState, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { ChatMessage as Message } from './types';
import { sendMessageToBackend } from './api';

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage: Message = {
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const answer = await sendMessageToBackend(trimmed);
      const botMessage: Message = {
        role: 'assistant',
        content: answer,
        timestamp: new Date().toISOString(),
        suggestions: ['Raise a ticket', 'Talk to support'],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Failed to reach server.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      handleSend();
    }
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4 flex flex-col min-h-screen">
      <div className="flex-1 space-y-4 mb-4 overflow-y-auto">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
        {loading && (
          <p className="text-sm text-gray-500 animate-pulse ml-2">Aven AI is typing...</p>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2 mt-2 sticky bottom-4 bg-white">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          placeholder="Ask Aven AI anything..."
          className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none"
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-50 hover:bg-blue-700 transition"
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
