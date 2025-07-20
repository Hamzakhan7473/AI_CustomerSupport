'use client';

import { useEffect, useRef, useState } from 'react';
import ChatMessage from './ChatMessage';
import { ChatMessage as Message } from './types';
import VoiceAssistant from './VoiceAssistant';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export default function ChatPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'voice' | 'ticket'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

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
    setTyping(true);

    try {
      const res = await fetch(`${BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed }),
      });

      if (!res.ok) throw new Error('Server error');

      const data = await res.json();
      const botMessage: Message = {
        role: 'assistant',
        content: data.answer || '🤖 No answer found.',
        timestamp: new Date().toISOString(),
        suggestions: ['Raise a ticket', 'Talk to human'],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('❌ Error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Aven AI is temporarily unavailable.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
      setTyping(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) handleSend();
  };

  return (
    <div className="flex flex-col h-screen bg-white text-black p-4 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-xl font-semibold">Aven</h1>
          <p className="text-xs text-gray-500 mt-1">Encrypted · 24/7 AI Support</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mt-4 mb-3">
        {['chat', 'voice', 'ticket'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as 'chat' | 'voice' | 'ticket')}
            className={`capitalize px-4 py-1 rounded-full text-sm font-medium transition border ${
              activeTab === tab ? 'bg-black text-white' : 'bg-white text-black border-gray-300'
            }`}
          >
            {tab === 'chat' ? 'Chat' : tab === 'voice' ? 'Voice AI' : 'Support Ticket'}
          </button>
        ))}
      </div>

      {/* Chat View */}
      {activeTab === 'chat' && (
        <>
          <div className="flex-1 overflow-y-auto space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`max-w-xl px-4 py-3 rounded-2xl shadow ${
                  msg.role === 'user' ? 'ml-auto bg-[#f3f3f3]' : 'mr-auto bg-[#fafafa]'
                }`}
              >
                <p className="text-sm">{msg.content}</p>
                <div className="text-xs text-gray-400 mt-1 text-right">
                  {new Date(msg.timestamp || '').toLocaleTimeString()}
                </div>
                {Array.isArray(msg.suggestions) && msg.suggestions.length > 0 && (
                  <div className="mt-2 flex gap-2 flex-wrap">
                    {msg.suggestions.map((s, idx) => (
                      <button
                        key={idx}
                        className="bg-black text-white text-xs px-3 py-1 rounded-full hover:opacity-80"
                        onClick={() => setInput(s)}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {typing && (
              <div className="text-sm text-gray-400">
                Aven AI is typing<span className="animate-pulse">...</span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="mt-4 flex gap-2">
            <input
              type="text"
              placeholder="Ask Aven anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              className="flex-1 rounded-full px-4 py-2 bg-[#f3f3f3] border border-gray-300 focus:outline-none"
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="bg-black text-white font-medium px-5 py-2 rounded-full shadow hover:opacity-90"
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
        </>
      )}

      {/* Voice View */}
      {activeTab === 'voice' && (
        <div className="flex-1 flex items-center justify-center">
          <VoiceAssistant />
        </div>
      )}

      {/* Ticket View */}
      {activeTab === 'ticket' && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.currentTarget);
            fetch(`${BASE_URL}/create-ticket`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                email: formData.get('email'),
                issue_description: formData.get('issue'),
              }),
            })
              .then((res) => res.json())
              .then((data) => alert(data.message))
              .catch(() => alert('❌ Failed to submit ticket'));
          }}
          className="space-y-4 mt-4 max-w-md mx-auto"
        >
          <input
            type="email"
            name="email"
            placeholder="Your email"
            required
            className="w-full border border-gray-300 bg-[#fafafa] text-black rounded-xl px-4 py-2"
          />
          <textarea
            name="issue"
            rows={4}
            placeholder="Describe your issue..."
            required
            className="w-full border border-gray-300 bg-[#fafafa] text-black rounded-xl px-4 py-2"
          />
          <button
            type="submit"
            className="bg-black hover:bg-gray-900 text-white font-semibold w-full py-2 rounded-xl"
          >
            Submit Ticket
          </button>
        </form>
      )}
    </div>
  );
}
