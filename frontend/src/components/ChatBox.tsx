"use client";

import { useState, useRef, useEffect } from "react";
import { SendHorizonal } from "lucide-react";

interface Message {
  role: "user" | "ai";
  content: string;
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "Thanks for reaching out. How can I help you?" },
      ]);
    }, 1500);
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col h-[500px] w-full max-w-md rounded-2xl bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-800 shadow-sm">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
              msg.role === "user"
                ? "bg-black text-white ml-auto rounded-br-none"
                : "bg-gray-100 dark:bg-zinc-800 text-black dark:text-white rounded-bl-none"
            }`}
          >
            {msg.content}
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-1 items-center px-4 py-3 bg-gray-100 dark:bg-zinc-800 rounded-2xl w-fit text-black dark:text-white">
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0s]" />
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0.15s]" />
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0.3s]" />
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="border-t border-gray-200 dark:border-gray-800 px-4 py-3 flex items-center gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 text-sm px-4 py-2 rounded-full bg-gray-100 dark:bg-zinc-800 focus:outline-none"
        />
        <button
          onClick={sendMessage}
          className="p-2 bg-black text-white dark:bg-white dark:text-black rounded-full hover:opacity-90 transition"
        >
          <SendHorizonal size={18} />
        </button>
      </div>
    </div>
  );
}
