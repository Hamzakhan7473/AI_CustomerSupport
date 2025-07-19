export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string; // ⏱️ Optional field for message time
  suggestions?: string[]; // 💡 Optional smart reply suggestions
}
