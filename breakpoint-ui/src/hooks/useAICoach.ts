import { useState, useCallback } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";
import type { Match } from "../lib/matchData";
import { MATCHES } from "../lib/matchData";
import { buildSystemPrompt, serializeMatchContext } from "../lib/coachPrompt";

export interface CoachMessage {
  role: "user" | "coach";
  text: string;
  followUps?: string[];
  timestamp: number;
}

const apiKey = import.meta.env.VITE_GEMINI_API_KEY || "";
if (!apiKey) console.warn("Missing VITE_GEMINI_API_KEY in environment variables");
const genAI = new GoogleGenerativeAI(apiKey);

export function useAICoach() {
  const [messages, setMessages] = useState<CoachMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askCoach = useCallback(async (question: string, match: Match) => {
    setError(null);
    const userMsg: CoachMessage = { role: "user", text: question, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
      const systemPrompt = buildSystemPrompt();
      const matchContext = serializeMatchContext(match, MATCHES);

      const prompt = `${systemPrompt}\n\n--- PLAYER DATA ---\n${matchContext}\n\n--- PLAYER QUESTION ---\n${question}`;

      const result = await model.generateContent(prompt);
      const raw = result.response.text();

      let answer = raw;
      let followUps: string[] = [];

      try {
        const jsonMatch = raw.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]) as { answer: string; followUps: string[] };
          answer = parsed.answer;
          followUps = parsed.followUps || [];
        }
      } catch {
        // Use raw text if JSON parsing fails
      }

      const coachMsg: CoachMessage = {
        role: "coach",
        text: answer,
        followUps: followUps.slice(0, 3),
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, coachMsg]);
    } catch (err) {
      console.error("Gemini API Error:", err);
      const msg = err instanceof Error ? err.message : "Failed to get coaching response";
      setError(msg);
      const errMsg: CoachMessage = {
        role: "coach",
        text: "I'm having trouble connecting right now. Try again in a moment.",
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, askCoach, clearChat };
}
