'use client';
import { ChatMessage as Message } from './types';


export default function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      <div
        className={`rounded-xl px-4 py-2 max-w-xs md:max-w-md ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-800'
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
