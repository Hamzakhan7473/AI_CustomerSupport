export async function sendMessageToBackend(userMessage: string): Promise<string> {
  try {
    const response = await fetch('https://ce3a710ead90.ngrok-free.app/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: userMessage }),
    });

    const isJson = response.headers
      .get('content-type')
      ?.toLowerCase()
      .includes('application/json');

    if (!response.ok) {
      const errorData = isJson ? await response.json() : { detail: 'Non-JSON error from backend' };
      console.error('❌ Backend error:', errorData);
      throw new Error(errorData.detail || 'Unexpected error from backend');
    }

    const data = isJson ? await response.json() : { answer: '❌ Unexpected non-JSON response.' };
    return data.answer || '🤖 Aven AI has no answer right now.';

  } catch (error) {
    console.error('❌ Failed to send message:', error);
    return '❌ Could not reach Aven AI backend. Please try again.';
  }
}
