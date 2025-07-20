'use client';
import { useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export default function TicketForm() {
  const [email, setEmail] = useState('');
  const [issue, setIssue] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!email || !issue) {
      setMessage('❗ Please fill in all fields.');
      return;
    }

    setSubmitting(true);
    setMessage('');

    try {
      const res = await fetch(`${API_BASE_URL}/create-ticket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, issue_description: issue }),
      });

      const data = await res.json();
      setMessage(data.message || '✅ Ticket submitted successfully!');
      setEmail('');
      setIssue('');
    } catch (err) {
      console.error('❌ Ticket submission failed:', err);
      setMessage('❌ Failed to submit ticket. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-8 bg-white p-6 rounded-xl shadow border">
      <h2 className="text-xl font-semibold mb-4">🛠️ Raise a Support Ticket</h2>

      <label className="block mb-2 text-sm font-medium">Email</label>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full mb-4 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
        placeholder="you@example.com"
        required
      />

      <label className="block mb-2 text-sm font-medium">Issue Description</label>
      <textarea
        rows={4}
        value={issue}
        onChange={(e) => setIssue(e.target.value)}
        className="w-full mb-4 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
        placeholder="Describe your issue clearly"
        required
      />

      <button
        onClick={handleSubmit}
        className={`bg-green-600 text-white px-4 py-2 rounded font-medium hover:bg-green-700 transition ${
          submitting ? 'opacity-70 cursor-not-allowed' : ''
        }`}
        disabled={submitting}
      >
        {submitting ? 'Submitting...' : 'Submit Ticket'}
      </button>

      {message && <p className="mt-4 text-sm text-blue-700">{message}</p>}
    </div>
  );
}
