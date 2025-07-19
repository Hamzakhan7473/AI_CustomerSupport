'use client';
import { useEffect, useState } from 'react';

export default function VoiceAssistant() {
  const [showIframe, setShowIframe] = useState(false);

  const handleStartCall = () => {
    setShowIframe(true);
  };

  return (
    <div className="my-4 text-center">
      {!showIframe ? (
        <button
          onClick={handleStartCall}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg shadow"
        >
          🎙️ Talk to Aven AI
        </button>
      ) : (
        <iframe
          src={`https://your-ngrok-url.ngrok-free.app/vapi.html?publicKey=YOUR_PUBLIC_KEY&assistantId=YOUR_ASSISTANT_ID`}
          title="Vapi Assistant"
          width="100%"
          height="400"
          className="rounded-xl border"
        />
      )}
    </div>
  );
}
