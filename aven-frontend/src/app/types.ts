export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  suggestions?: string[];
  type?: 'text' | 'voice' | 'error'; // for different types of assistant responses
  spokenText?: string;              // if Vapi/Gemini returns speech recognition text
}
