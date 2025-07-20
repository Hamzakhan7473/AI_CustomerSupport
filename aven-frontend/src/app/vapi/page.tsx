'use client';

export default function VapiPage() {
  const publicKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY;
  const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID;

  // 🛡️ Prevent SSR rendering errors
  if (typeof window === 'undefined') return null;

  // 🚨 Missing ENV check
  if (!publicKey || !assistantId) {
    return (
      <div className="text-center mt-10 text-red-600">
        ❌ Missing Vapi credentials. Please check your environment variables.
      </div>
    );
  }

  const iframeSrc = `/vapi.html?publicKey=${publicKey}&assistantId=${assistantId}`;

  return (
    <iframe
      key={iframeSrc} // 🔁 reloads if env changes
      src={iframeSrc}
      title="Vapi Voice Assistant"
      allow="microphone"
      loading="lazy"
      style={{
        width: '100%',
        height: '100vh',
        border: 'none',
        backgroundColor: '#fff',
      }}
    />
  );
}
