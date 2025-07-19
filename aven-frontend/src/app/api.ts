// src/app/api.ts
export async function sendMessageToBackend(userMessage: string): Promise<string> {
  const res = await fetch('https://7e276e7a8a76.ngrok-free.app/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: userMessage }),
  });

  if (!res.ok) {
    throw new Error('Failed to fetch from backend');
  }

  const data = await res.json();
  return data.answer;
}
