"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

export default function Header() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  return (
    <header className="w-full max-w-2xl px-4 py-3 flex items-center justify-between bg-white dark:bg-zinc-800 border-b dark:border-zinc-700 rounded-t-xl">
      <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">Aven AI</h1>

      {mounted && (
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-2 rounded-full bg-zinc-200 dark:bg-zinc-700"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      )}
    </header>
  );
}
