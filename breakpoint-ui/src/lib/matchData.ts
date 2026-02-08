/* ── types ─────────────────────────────────────────────────────── */
export interface Landing { x: number; y: number; zone: string; }
export interface Shot { shot_id: number; player: "self" | "opponent"; hand: string; landing: Landing; }
export interface Rally { rally_id: number; shots: number[]; winner: "self" | "opponent"; length: number; }
export interface Court { corners: number[][]; net_y: number; width_px: number; height_px: number; }
export interface Coaching {
  headline: string; advice: string; mentalCue: string; finding: string;
  evidence: string; strategy: string; mentalIssue: string; confidence: number;
}
export interface Match {
  id: string; label: string; time: string; date: string; duration: string;
  shots_count: number; rallies_count: number;
  footworkDrop: number; aggression: number; forehand: number; backhand: number;
  avgRally: number; avgArmSpeed: number; avgFootSpeed: number; style: string;
  coaching: Coaching;
  pressureMoment: string; expectedImpact: string[];
  court: Court; shots: Shot[]; rallies: Rally[];
}

/* ── match data ────────────────────────────────────────────────── */
export const MATCHES: Match[] = [
  {
    id: "224148", label: "Match 1", time: "10:41 PM", date: "Feb 7", duration: "1:31",
    shots_count: 22, rallies_count: 17, footworkDrop: 25, aggression: 0.27,
    forehand: 36.4, backhand: 22.7, avgRally: 1.19, avgArmSpeed: 3.79, avgFootSpeed: 5.04,
    style: "passive",
    coaching: {
      headline: "You're giving up control by playing passively. Time to attack.",
      advice: "Step in and drive after pushing.",
      mentalCue: "Breathe, step, drive.",
      finding: "You primarily pushed the ball, with a low aggression index.",
      evidence: "Aggression index is 0.27. Forehand 36.4%, backhand 22.7%.",
      strategy: "After your push, immediately step forward and prepare a forehand drive.",
      mentalIssue: "Hesitation after pushing leads to passive play.",
      confidence: 0.85,
    },
    pressureMoment: "After pushes \u2192 hesitation \u2192 footwork slows 25%",
    expectedImpact: ["earlier point control", "fewer long rallies"],
    court: { corners: [[450, 252], [792, 252], [785, 478], [445, 478]], net_y: 365, width_px: 347, height_px: 226 },
    shots: [
      { shot_id: 1, player: "opponent", hand: "backhand", landing: { x: 473, y: 255, zone: "far_left" } },
      { shot_id: 2, player: "self", hand: "unknown", landing: { x: 583, y: 223, zone: "far_center" } },
      { shot_id: 3, player: "opponent", hand: "forehand", landing: { x: 724, y: 223, zone: "far_right" } },
      { shot_id: 4, player: "self", hand: "unknown", landing: { x: 617, y: 230, zone: "far_center" } },
      { shot_id: 5, player: "opponent", hand: "forehand", landing: { x: 471, y: 261, zone: "far_left" } },
      { shot_id: 6, player: "self", hand: "backhand", landing: { x: 713, y: 218, zone: "far_right" } },
      { shot_id: 7, player: "opponent", hand: "forehand", landing: { x: 642, y: 223, zone: "far_center" } },
      { shot_id: 8, player: "self", hand: "unknown", landing: { x: 780, y: 257, zone: "far_right" } },
      { shot_id: 9, player: "opponent", hand: "forehand", landing: { x: 432, y: 247, zone: "far_left" } },
      { shot_id: 10, player: "self", hand: "unknown", landing: { x: 618, y: 277, zone: "far_center" } },
      { shot_id: 11, player: "opponent", hand: "forehand", landing: { x: 715, y: 227, zone: "far_right" } },
      { shot_id: 12, player: "self", hand: "unknown", landing: { x: 686, y: 220, zone: "far_right" } },
      { shot_id: 13, player: "opponent", hand: "forehand", landing: { x: 642, y: 234, zone: "far_center" } },
      { shot_id: 14, player: "self", hand: "unknown", landing: { x: 560, y: 232, zone: "far_left" } },
      { shot_id: 15, player: "opponent", hand: "backhand", landing: { x: 440, y: 269, zone: "far_left" } },
      { shot_id: 16, player: "self", hand: "unknown", landing: { x: 624, y: 238, zone: "far_center" } },
      { shot_id: 17, player: "opponent", hand: "neutral", landing: { x: 716, y: 219, zone: "far_right" } },
      { shot_id: 18, player: "self", hand: "backhand", landing: { x: 445, y: 272, zone: "far_left" } },
      { shot_id: 19, player: "opponent", hand: "forehand", landing: { x: 634, y: 243, zone: "far_center" } },
      { shot_id: 20, player: "self", hand: "backhand", landing: { x: 543, y: 267, zone: "far_left" } },
      { shot_id: 21, player: "opponent", hand: "forehand", landing: { x: 739, y: 227, zone: "far_right" } },
      { shot_id: 22, player: "self", hand: "unknown", landing: { x: 800, y: 281, zone: "far_right" } },
    ],
    rallies: [
      { rally_id: 1, shots: [1], winner: "self", length: 1 },
      { rally_id: 2, shots: [2, 3, 4], winner: "opponent", length: 3 },
      { rally_id: 3, shots: [5, 6], winner: "opponent", length: 2 },
      { rally_id: 4, shots: [7], winner: "self", length: 1 },
      { rally_id: 5, shots: [8], winner: "opponent", length: 1 },
      { rally_id: 6, shots: [9], winner: "self", length: 1 },
      { rally_id: 7, shots: [10], winner: "opponent", length: 1 },
      { rally_id: 8, shots: [11], winner: "self", length: 1 },
      { rally_id: 9, shots: [12, 13, 14], winner: "opponent", length: 3 },
      { rally_id: 10, shots: [15], winner: "self", length: 1 },
      { rally_id: 11, shots: [16], winner: "opponent", length: 1 },
      { rally_id: 12, shots: [17], winner: "self", length: 1 },
      { rally_id: 13, shots: [18], winner: "opponent", length: 1 },
      { rally_id: 14, shots: [19], winner: "self", length: 1 },
      { rally_id: 15, shots: [20], winner: "opponent", length: 1 },
      { rally_id: 16, shots: [21], winner: "self", length: 1 },
      { rally_id: 17, shots: [22], winner: "opponent", length: 1 },
    ],
  },
  {
    id: "153355", label: "Match 2", time: "3:33 PM", date: "Feb 7", duration: "0:26",
    shots_count: 10, rallies_count: 4, footworkDrop: 29, aggression: 0.36,
    forehand: 30.0, backhand: 0, avgRally: 1.04, avgArmSpeed: 5.69, avgFootSpeed: 2.67,
    style: "passive",
    coaching: {
      headline: "Predictable patterns give opponents easy reads. Mix it up.",
      advice: "Mix up your push placement and prepare to attack.",
      mentalCue: "Breathe, shift, attack!",
      finding: "You primarily pushed the ball to the opponent's left side.",
      evidence: "7 out of 10 shots landed in the near_left zone.",
      strategy: "Vary your push placement to include the opponent's right side.",
      mentalIssue: "Hesitation after pushing, leading to a passive stance.",
      confidence: 0.80,
    },
    pressureMoment: "Predictable placement \u2192 opponent anticipates \u2192 lost initiative",
    expectedImpact: ["more unpredictable play", "better court control"],
    court: { corners: [[508, 262], [786, 262], [786, 460], [508, 460]], net_y: 361, width_px: 278, height_px: 198 },
    shots: [
      { shot_id: 1, player: "opponent", hand: "forehand", landing: { x: 771, y: 408, zone: "near_right" } },
      { shot_id: 2, player: "self", hand: "unknown", landing: { x: 582, y: 236, zone: "far_left" } },
      { shot_id: 3, player: "opponent", hand: "unknown", landing: { x: 548, y: 418, zone: "near_left" } },
      { shot_id: 4, player: "self", hand: "forehand", landing: { x: 539, y: 424, zone: "near_left" } },
      { shot_id: 5, player: "opponent", hand: "unknown", landing: { x: 555, y: 428, zone: "near_left" } },
      { shot_id: 6, player: "self", hand: "unknown", landing: { x: 497, y: 406, zone: "near_left" } },
      { shot_id: 7, player: "opponent", hand: "forehand", landing: { x: 503, y: 404, zone: "near_left" } },
      { shot_id: 8, player: "self", hand: "unknown", landing: { x: 691, y: 390, zone: "near_center" } },
      { shot_id: 9, player: "opponent", hand: "neutral", landing: { x: 493, y: 415, zone: "near_left" } },
      { shot_id: 10, player: "self", hand: "unknown", landing: { x: 522, y: 403, zone: "near_left" } },
    ],
    rallies: [
      { rally_id: 1, shots: [1, 2], winner: "opponent", length: 2 },
      { rally_id: 2, shots: [3, 4], winner: "opponent", length: 2 },
      { rally_id: 3, shots: [5, 6, 7, 8], winner: "opponent", length: 4 },
      { rally_id: 4, shots: [9, 10], winner: "opponent", length: 2 },
    ],
  },
  {
    id: "192747", label: "Match 3", time: "7:27 PM", date: "Feb 7", duration: "0:16",
    shots_count: 6, rallies_count: 3, footworkDrop: 27, aggression: 0.41,
    forehand: 16.7, backhand: 0, avgRally: 0.96, avgArmSpeed: 8.99, avgFootSpeed: 4.87,
    style: "passive",
    coaching: {
      headline: "You're letting opponents dictate. Take control of rallies.",
      advice: "Prepare a forehand drive after every push.",
      mentalCue: "Breathe, step, drive.",
      finding: "Frequently pushing with limited forehand drives observed.",
      evidence: "16.7% forehand usage across 6 shots.",
      strategy: "After your push, step forward and prepare a forehand drive.",
      mentalIssue: "Hesitation after pushing leads to passive play.",
      confidence: 0.75,
    },
    pressureMoment: "Low aggression index \u2192 opponent controls pace \u2192 reactive play",
    expectedImpact: ["aggressive positioning", "faster point resolution"],
    court: { corners: [[508, 284], [764, 284], [764, 388], [508, 388]], net_y: 336, width_px: 256, height_px: 104 },
    shots: [
      { shot_id: 1, player: "opponent", hand: "unknown", landing: { x: 651, y: 271, zone: "far_center" } },
      { shot_id: 2, player: "self", hand: "unknown", landing: { x: 686, y: 337, zone: "near_right" } },
      { shot_id: 3, player: "opponent", hand: "forehand", landing: { x: 663, y: 268, zone: "far_center" } },
      { shot_id: 4, player: "self", hand: "unknown", landing: { x: 761, y: 287, zone: "far_right" } },
      { shot_id: 5, player: "opponent", hand: "neutral", landing: { x: 692, y: 291, zone: "far_right" } },
      { shot_id: 6, player: "self", hand: "unknown", landing: { x: 670, y: 326, zone: "far_center" } },
    ],
    rallies: [
      { rally_id: 1, shots: [1, 2], winner: "opponent", length: 2 },
      { rally_id: 2, shots: [3], winner: "self", length: 1 },
      { rally_id: 3, shots: [4, 5, 6], winner: "opponent", length: 3 },
    ],
  },
  {
    id: "134224", label: "Match 4", time: "1:42 PM", date: "Feb 7", duration: "0:16",
    shots_count: 6, rallies_count: 3, footworkDrop: 35, aggression: 0.39,
    forehand: 66.7, backhand: 0, avgRally: 0.89, avgArmSpeed: 7.17, avgFootSpeed: 5.7,
    style: "passive",
    coaching: {
      headline: "Zero shot variation makes you predictable. Add drives.",
      advice: "Step in and drive after your push.",
      mentalCue: "Push, Breathe, Step, Drive",
      finding: "100% of your shots were pushes.",
      evidence: "All shots recorded were pushes. Forehand 66.7%.",
      strategy: "After your push, step forward and prepare a forehand drive.",
      mentalIssue: "Hesitation after pushing, leading to a passive stance.",
      confidence: 0.75,
    },
    pressureMoment: "All pushes \u2192 opponent expects pattern \u2192 easy counters",
    expectedImpact: ["unpredictable offense", "opponent uncertainty"],
    court: { corners: [[513, 280], [766, 280], [766, 390], [513, 390]], net_y: 308, width_px: 253, height_px: 110 },
    shots: [
      { shot_id: 1, player: "opponent", hand: "unknown", landing: { x: 548, y: 359, zone: "near_left" } },
      { shot_id: 2, player: "self", hand: "forehand", landing: { x: 641, y: 359, zone: "near_center" } },
      { shot_id: 3, player: "opponent", hand: "forehand", landing: { x: 500, y: 341, zone: "near_left" } },
      { shot_id: 4, player: "self", hand: "forehand", landing: { x: 584, y: 321, zone: "far_left" } },
      { shot_id: 5, player: "opponent", hand: "neutral", landing: { x: 522, y: 317, zone: "far_left" } },
      { shot_id: 6, player: "self", hand: "forehand", landing: { x: 645, y: 319, zone: "far_center" } },
    ],
    rallies: [
      { rally_id: 1, shots: [1, 2, 3], winner: "self", length: 3 },
      { rally_id: 2, shots: [4, 5], winner: "self", length: 2 },
      { rally_id: 3, shots: [6], winner: "opponent", length: 1 },
    ],
  },
];

/* ── data-driven match insights ───────────────────────────────── */
export function analyzeMatch(m: Match) {
  const selfShots = m.shots.filter(s => s.player === "self");
  const oppShots = m.shots.filter(s => s.player === "opponent");
  const selfZones: Record<string, number> = {};
  const oppZones: Record<string, number> = {};
  selfShots.forEach(s => { selfZones[s.landing.zone] = (selfZones[s.landing.zone] || 0) + 1; });
  oppShots.forEach(s => { oppZones[s.landing.zone] = (oppZones[s.landing.zone] || 0) + 1; });

  const ralliesWon = m.rallies.filter(r => r.winner === "self").length;
  const ralliesLost = m.rallies.filter(r => r.winner === "opponent").length;
  const winPct = m.rallies_count > 0 ? Math.round((ralliesWon / m.rallies_count) * 100) : 0;

  const topSelfZone = Object.entries(selfZones).sort((a, b) => b[1] - a[1])[0];
  const topOppZone = Object.entries(oppZones).sort((a, b) => b[1] - a[1])[0];

  const allZones = ["far_left", "far_center", "far_right", "near_left", "near_center", "near_right"];
  const selfBlindSpots = allZones.filter(z => !selfZones[z]);
  const oppBlindSpots = allZones.filter(z => !oppZones[z]);

  const selfFar = selfShots.filter(s => s.landing.zone.startsWith("far_")).length;
  const selfNear = selfShots.filter(s => s.landing.zone.startsWith("near_")).length;

  const shortRallies = m.rallies.filter(r => r.length <= 1);
  const longRallies = m.rallies.filter(r => r.length >= 2);
  const shortWinPct = shortRallies.length > 0 ? Math.round(shortRallies.filter(r => r.winner === "self").length / shortRallies.length * 100) : 0;
  const longWinPct = longRallies.length > 0 ? Math.round(longRallies.filter(r => r.winner === "self").length / longRallies.length * 100) : 0;

  const forehandCount = selfShots.filter(s => s.hand === "forehand").length;
  const backhandCount = selfShots.filter(s => s.hand === "backhand").length;

  return {
    selfShots, oppShots, selfZones, oppZones, ralliesWon, ralliesLost, winPct,
    topSelfZone, topOppZone, selfBlindSpots, oppBlindSpots,
    selfFar, selfNear, shortWinPct, longWinPct, shortRallies, longRallies,
    forehandCount, backhandCount,
  };
}

/* ── cross-match data ─────────────────────────────────────────── */
export const totalShots = MATCHES.reduce((s, m) => s + m.shots_count, 0);
export const totalRallies = MATCHES.reduce((s, m) => s + m.rallies_count, 0);
export const selfWins = MATCHES.reduce((s, m) => s + m.rallies.filter(r => r.winner === "self").length, 0);
export const winRate = Math.round((selfWins / totalRallies) * 100);
export const avgAggression = +(MATCHES.reduce((s, m) => s + m.aggression, 0) / MATCHES.length).toFixed(2);
export const avgFootworkDrop = +(MATCHES.reduce((s, m) => s + m.footworkDrop, 0) / MATCHES.length).toFixed(0);

/* ── drills ────────────────────────────────────────────────────── */
export const DRILLS = [
  {
    title: "Push-to-Drive Transition",
    desc: "Partner pushes to your forehand. Return push, then immediately step in and drive the next ball. Focus on eliminating the hesitation gap.",
    focus: "Eliminates post-push hesitation", reps: "3 x 10 rallies", metric: "Aggression Index",
  },
  {
    title: "Placement Variation",
    desc: "Push to all 6 zones systematically. Alternate left-center-right. Your data shows heavy clustering \u2014 opponents read you easily.",
    focus: "Breaks predictable patterns", reps: "2 x 12 pushes", metric: "Zone Coverage",
  },
  {
    title: "Footwork Recovery Loop",
    desc: "After each shot, split-step back to ready position. Maintain foot speed throughout the rally. Your footwork drops 25-35% under pressure.",
    focus: "Stops footwork degradation", reps: "5 min continuous", metric: "Footwork Drop %",
  },
];
