'use client';
import { useState } from 'react';

export default function TicketForm() {
  const [email, setEmail] = useState('');
  const [issue, setIssue] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!email || !issue) return;

    setSubmitting(true);
    setMessage('');

    try {
      const res = await fetch('https://7e276e7a8a76.ngrok-free.app/create-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, issue_description: issue }),
      });

      const data = await res.json();
      setMessage(data.message || 'Ticket submitted!');
      setEmail('');
      setIssue('');
    } catch (err) {
      setMessage('❌ Failed to submit ticket');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-8 bg-gray-100 p-6 rounded-lg shadow">
      <h2 className="text-lg font-bold mb-4">🛠️ Raise a Support Ticket</h2>

      <input
        type="email"
        placeholder="Your Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full mb-3 p-2 border rounded"
      />

      <textarea
        rows={4}
        placeholder="Describe your issue..."
        value={issue}
        onChange={(e) => setIssue(e.target.value)}
        className="w-full mb-3 p-2 border rounded"
      />

      <button
        onClick={handleSubmit}
        className="bg-green-600 text-white px-4 py-2 rounded"
        disabled={submitting}
      >
        {submitting ? 'Submitting...' : 'Submit Ticket'}
      </button>

      {message && <p className="mt-4 text-sm text-blue-700">{message}</p>}
    </div>
  );
}
