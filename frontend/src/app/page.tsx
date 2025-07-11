// src/app/page.tsx
"use client";

import ChatBox from "@/components/ChatBox";
import ChatHeader from "@/components/ChatHeader";
import DarkModeToggle from "@/components/DarkModeToggle";
import BackgroundGlow from "@/components/BackgroundGlow";

export default function Home() {
  return (
    <main className="relative min-h-screen w-full flex items-center justify-center bg-gray-100 dark:bg-[#0a0a0a] px-4">
      <BackgroundGlow />

      <div className="flex flex-col items-center gap-6 w-full max-w-xl">
        <div className="flex justify-between items-center w-full">
          <ChatHeader />
          <DarkModeToggle />
        </div>

        <ChatBox />
      </div>
    </main>
  );
}
