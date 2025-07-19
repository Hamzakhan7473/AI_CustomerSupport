'use client'

export default function VapiPage() {
  const publicKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY!;
  const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID!;

  return (
    <iframe
      src={`/vapi.html?publicKey=${publicKey}&assistantId=${assistantId}`}
      style={{ width: '100%', height: '100vh', border: 'none' }}
    />
  );
}
