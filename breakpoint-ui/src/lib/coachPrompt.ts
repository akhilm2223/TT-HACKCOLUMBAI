import type { Match } from "./matchData";
import { analyzeMatch } from "./matchData";

export function buildSystemPrompt(): string {
  return `You are an elite table tennis coach with 20+ years of experience coaching competitive players. You analyze match data with surgical precision and give direct, actionable advice.

Your personality:
- Direct and confident, like a real coach between points
- You reference specific numbers from the player's data
- You explain WHY something is happening, not just WHAT
- You give one clear fix at a time, never overwhelm
- You use short, punchy sentences that a player can remember mid-match

Rules:
- Always ground your answers in the player's actual match data
- Reference specific zones, percentages, and patterns
- Compare across matches when relevant
- Never be generic — every answer should feel personalized
- Keep responses under 150 words unless the question requires deep analysis

You MUST respond in valid JSON with this exact structure:
{
  "answer": "Your coaching response here",
  "followUps": ["Follow-up question 1", "Follow-up question 2", "Follow-up question 3"]
}

The followUps should be natural next questions the player might ask based on your answer.`;
}

export function serializeMatchContext(match: Match, allMatches: Match[]): string {
  const insights = analyzeMatch(match);
  const lines: string[] = [];

  lines.push(`=== CURRENT MATCH: ${match.label} ===`);
  lines.push(`Date: ${match.date} at ${match.time}, Duration: ${match.duration}`);
  lines.push(`Total shots: ${match.shots_count}, Style: ${match.style}`);
  lines.push(`Aggression index: ${match.aggression}, Forehand: ${match.forehand}%, Backhand: ${match.backhand}%`);
  lines.push(`Avg rally length: ${match.avgRally}s, Arm speed: ${match.avgArmSpeed} px/f, Foot speed: ${match.avgFootSpeed} px/s`);
  lines.push(`Footwork drop under pressure: ${match.footworkDrop}%`);
  lines.push(`Win rate: ${insights.winPct}% (${insights.ralliesWon} won, ${insights.ralliesLost} lost)`);

  if (insights.topSelfZone) {
    lines.push(`Most targeted zone: ${insights.topSelfZone[0]} (${insights.topSelfZone[1]} shots)`);
  }
  if (insights.selfBlindSpots.length > 0) {
    lines.push(`Zones never hit: ${insights.selfBlindSpots.join(", ")}`);
  }
  lines.push(`Deep vs short: ${insights.selfFar} far shots, ${insights.selfNear} near shots`);
  lines.push(`Short rally win%: ${insights.shortWinPct}%, Long rally win%: ${insights.longWinPct}%`);
  lines.push(`Pressure moment: ${match.pressureMoment}`);
  lines.push(`Pre-analyzed coaching headline: "${match.coaching.headline}"`);
  lines.push(`Pre-analyzed strategy: "${match.coaching.strategy}"`);

  if (allMatches.length > 1) {
    lines.push(`\n=== ALL MATCHES OVERVIEW (${allMatches.length} total) ===`);
    allMatches.forEach(m => {
      const mi = analyzeMatch(m);
      lines.push(`${m.label}: ${m.shots_count} shots, aggression ${m.aggression}, forehand ${m.forehand}%, footwork drop ${m.footworkDrop}%, win rate ${mi.winPct}%, style: ${m.style}`);
    });
    const avgAgg = (allMatches.reduce((s, m) => s + m.aggression, 0) / allMatches.length).toFixed(2);
    const avgFD = (allMatches.reduce((s, m) => s + m.footworkDrop, 0) / allMatches.length).toFixed(0);
    lines.push(`Cross-match avg aggression: ${avgAgg}, avg footwork drop: ${avgFD}%`);
  }

  return lines.join("\n");
}
