'use client';

import { useEffect, useRef, useState } from 'react';
import Vapi from '@vapi-ai/web';

const PUBLIC_KEY = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY!;
const ASSISTANT_ID = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID!;

type VapiStatus = 'loading' | 'active' | 'speaking' | 'error';

export default function VoiceAssistant() {
  const vapiRef = useRef<InstanceType<typeof Vapi> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [status, setStatus] = useState<VapiStatus>('loading');
  const [userSpeech, setUserSpeech] = useState('');
  const [assistantReply, setAssistantReply] = useState('');

  useEffect(() => {
    const setup = async () => {
      try {
        if (!PUBLIC_KEY || !ASSISTANT_ID) {
          throw new Error('❌ Missing Vapi credentials');
        }

        const vapi = new Vapi(PUBLIC_KEY);
        vapiRef.current = vapi;

        // Vapi events
        vapi.on('message', (msg: any) => {
          if (msg?.role === 'user') {
            setUserSpeech(msg.content || '');
          } else if (msg?.role === 'assistant') {
            setAssistantReply(msg.content || '');
            setStatus('active');
          }
        });

        vapi.on('error', (err: any) => {
          console.error('❌ Vapi Error:', err);
          setStatus('error');
        });

        (vapi as any).on('call-started', () => {
          console.log('📞 Call started');
          setUserSpeech('');
          setAssistantReply('');
          setStatus('speaking');
        });

        (vapi as any).on('call-ended', () => {
          console.log('📴 Call ended');
          setStatus('active');
        });

        await vapi.start(ASSISTANT_ID);
        console.log('✅ Vapi Gemini Assistant Ready');
        setStatus('active');
      } catch (err) {
        console.error('❌ Vapi setup failed:', err);
        setStatus('error');
      }
    };

    setup();

    return () => {
      if (vapiRef.current) {
        console.log('🧹 Cleaning up Vapi');
        (vapiRef.current as any).stop?.();
        vapiRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [userSpeech, assistantReply]);

  return (
    <div className="bg-white rounded-xl shadow p-6 w-full max-w-2xl mx-auto text-center">
      <h2 className="text-lg font-semibold mb-4">🎤 Aven Voice Assistant</h2>

      <div className="space-y-2 text-left">
        {userSpeech && (
          <div className="bg-blue-100 text-blue-900 p-3 rounded-xl shadow-sm">
            <p className="text-sm">👤 <strong>User:</strong> {userSpeech}</p>
          </div>
        )}
        {status === 'speaking' && (
          <p className="text-gray-400 text-sm animate-pulse">🎙️ Listening...</p>
        )}
        {assistantReply && (
          <div className="bg-gray-100 text-gray-800 p-3 rounded-xl shadow-sm">
            <p className="text-sm">🤖 <strong>Aven:</strong> {assistantReply}</p>
          </div>
        )}
      </div>

      <div ref={messagesEndRef} />

      <div className="mt-6 text-sm text-gray-500">
        {status === 'loading'
          ? '⏳ Connecting to Vapi...'
          : status === 'active'
          ? '✅ Ready to assist you'
          : status === 'speaking'
          ? '🎧 Active conversation...'
          : '❌ Error connecting to assistant'}
      </div>
    </div>
  );
}
