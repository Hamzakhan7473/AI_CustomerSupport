// src/components/TypingDots.tsx
export default function TypingDots() {
  return (
    <div className="flex space-x-1 items-end justify-start px-4 py-2 rounded-2xl bg-zinc-200 dark:bg-zinc-700 shadow-md max-w-max">
      <div className="animate-bounce w-2 h-2 bg-gray-500 dark:bg-gray-300 rounded-full" style={{ animationDelay: "0s" }} />
      <div className="animate-bounce w-2 h-2 bg-gray-500 dark:bg-gray-300 rounded-full" style={{ animationDelay: "0.2s" }} />
      <div className="animate-bounce w-2 h-2 bg-gray-500 dark:bg-gray-300 rounded-full" style={{ animationDelay: "0.4s" }} />
    </div>
  );
}
