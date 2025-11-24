"use client";
import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { motion } from "framer-motion";

// Helper function to apply underlines to text based on spans
function applyUnderlinesToText(text: string, spans: [number, number][]) {
  if (!spans || spans.length === 0) {
    return text;
  }

  // Sort spans by start position in descending order to avoid index issues
  const sortedSpans = [...spans].sort((a, b) => b[0] - a[0]);
  
  let result = text;
  
  for (const [start, end] of sortedSpans) {
    // Ensure the span is within the text bounds
    if (start >= 0 && end <= text.length && start < end) {
      const before = result.slice(0, start);
      const underlined = result.slice(start, end);
      const after = result.slice(end);
      result = before + `<u class="text-red-600 decoration-2">${underlined}</u>` + after;
    }
  }
  
  return result;
}

// StickmanVisualization Component
function StickmanVisualization({ handPositionData }: { handPositionData: string }) {
  // Parse the hand position data to extract percentages
  const parseHandPositionData = (data: string) => {
    try {
      // The data is a string representation of a dictionary
      // Look for 'boxes_percentages': {...}
      const boxesMatch = data.match(/'boxes_percentages':\s*{([^}]+)}/);
      if (!boxesMatch) return {};
      
      const boxesContent = boxesMatch[1];
      const percentages: Record<string, number> = {};
      
      // Extract each key-value pair
      const pairs = boxesContent.split(',');
      pairs.forEach(pair => {
        const match = pair.match(/'([^']+)':\s*([\d.]+)/);
        if (match) {
          percentages[match[1]] = parseFloat(match[2]);
        }
      });
      
      return percentages;
    } catch (error) {
      console.error('Error parsing hand position data:', error);
      return {};
    }
  };

  const percentages = parseHandPositionData(handPositionData);
  const formatPercentage = (value?: number) => `${(value ?? 0).toFixed(1)}%`;
  
  // Get alpha values (percentages as decimals, multiplied by 1.5, clamped between 0.1 and 0.8 for visibility)
  const getAlpha = (percentage: number) => {
    return Math.max(0.1, Math.min(0.9, (percentage * 1.6) / 100));
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative inline-block group">
        {/* Stickman base image */}
        <img 
          src="/stickman.png" 
          alt="Stickman" 
          className="w-64 h-64 object-contain block"
        />
        
        {/* Overlay divs for 8 regions - positioned to match image exactly */}
        {/* Upper row */}
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: 0,
            left: 0,
            width: '50%',
            height: '24%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.uul || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.uul)}
          </span>
        </div>
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: 0,
            right: 0,
            width: '50%',
            height: '24%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.uur || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.uur)}
          </span>
        </div>
        
        {/* Upper middle row */}
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: '24%',
            left: 0,
            width: '50%',
            height: '18%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ul || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.ul)}
          </span>
        </div>
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: '24%',
            right: 0,
            width: '50%',
            height: '18%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ur || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.ur)}
          </span>
        </div>
        
        {/* Lower middle row */}
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: '42%',
            left: 0,
            width: '50%',
            height: '15%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.dl || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.dl)}
          </span>
        </div>
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: '42%',
            right: 0,
            width: '50%',
            height: '15%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.dr || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.dr)}
          </span>
        </div>
        
        {/* Bottom row */}
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: '57%',
            left: 0,
            width: '50%',
            height: '43%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ddl || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.ddl)}
          </span>
        </div>
        <div 
          className="absolute flex items-center justify-center text-white text-xs font-semibold group"
          style={{
            top: '57%',
            right: 0,
            width: '50%',
            height: '43%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ddr || 0)})` 
          }}
        >
          <span className="px-2 py-1 rounded bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
            {formatPercentage(percentages.ddr)}
          </span>
        </div>
      </div>
      
      {/* 
      <div className="mt-4 text-xs text-gray-600">
        <div className="grid grid-cols-2 gap-2">
          <div>UUL: {(percentages.uul || 0).toFixed(1)}%</div>
          <div>UUR: {(percentages.uur || 0).toFixed(1)}%</div>
          <div>UL: {(percentages.ul || 0).toFixed(1)}%</div>
          <div>UR: {(percentages.ur || 0).toFixed(1)}%</div>
          <div>DL: {(percentages.dl || 0).toFixed(1)}%</div>
          <div>DR: {(percentages.dr || 0).toFixed(1)}%</div>
          <div>DDL: {(percentages.ddl || 0).toFixed(1)}%</div>
          <div>DDR: {(percentages.ddr || 0).toFixed(1)}%</div>
        </div>
      </div> */}
    </div>
  );
}

interface AnalysisResults {
  transcript: string;
  corrected_transcript: string;
  word_count: number;
  sentence_count: number;
  paragraph_count: number;
  letter_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores?: Record<string, number>;
  parts_of_speech: Record<string, number>;
  grammar_mistakes: [[number, number], string, string][];
  custom_tone_results: [number, string, string][];
  extra_tone_results: [number, string, string][];
  hand_position_results: string;
  gaze_x?: number[];
  gaze_y?: number[];
  gaze_angle_x?: number[];
  gaze_angle_y?: number[];
  hand_eye_activity_results?: any;
  aus_sum: number;
  blinks: number;
  active: number;
  passive: number;
  readability_score: string;
  cefr: string;
  ielts: string;
  floss_spans: [number, number][];
}

export default function ResultsDisplay({ results }: { results: AnalysisResults }) {
  const [userInfo, setUserInfo] = useState<{ name: string; age: number; organization: string; role: string } | null>(null);
  const [copyAlertVisible, setCopyAlertVisible] = useState(false);
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem('userInfo');
      if (stored) {
        setUserInfo(JSON.parse(stored));
      }
    } catch (e) {
      // ignore
    }
  }, []);
  // Prepare gaze arrays with fallback to older field names
  const gazeX: number[] = (results.gaze_x ?? results.gaze_angle_x ?? []) as number[];
  const gazeY: number[] = (results.gaze_y ?? results.gaze_angle_y ?? []) as number[];

  // Prepare raw-range-based plotting (supports negative and positive values)
  const gazePlotData = (() => {
    const length = Math.min(gazeX.length, gazeY.length);
    const xs = gazeX.slice(0, length).map((value) => Math.max(Math.min(value, 0.4), -0.4));
    const ys = gazeY.slice(0, length).map((value) => Math.max(Math.min(value, 0.4), -0.4));
    const MAX_ABS = 0.4;
    return {
      xs,
      ys,
      length,
      maxAbsX: MAX_ABS,
      maxAbsY: MAX_ABS,
      rangeX: MAX_ABS,
      rangeY: MAX_ABS,
    };
  })();

  const volumeRawData = (() => {
    const entries = Object.entries(results.volume_points ?? {});
    return entries.map(([time, volume], index) => {
      const numericTime = Number(time);
      const timeNumber = Number.isFinite(numericTime) ? numericTime : index;
      return {
        timeNumber,
        originalTime: timeNumber,
        Volume: volume,
      };
    });
  })();

  const volumeSpacing = (() => {
    if (volumeRawData.length < 2) {
      return 1;
    }
    const sortedTimes = [...volumeRawData.map((point) => point.timeNumber)].sort((a, b) => a - b);
    let minDiff = Infinity;
    for (let i = 1; i < sortedTimes.length; i += 1) {
      const diff = sortedTimes[i] - sortedTimes[i - 1];
      if (diff > 0) {
        minDiff = Math.min(minDiff, diff);
      }
    }
    if (!Number.isFinite(minDiff) || minDiff <= 0) {
      return 1;
    }
    return minDiff;
  })();

  const volumeBarOffset = volumeSpacing / 2;

  const volumeChartData = volumeRawData.map((point) => ({
    ...point,
    timePosition: point.timeNumber + volumeBarOffset,
  }));

  const volumeTicks = (() => {
    if (volumeRawData.length === 0) {
      return [];
    }
    const tickInterval = 20;
    const maxTime = volumeRawData.reduce((max, point) => Math.max(max, point.timeNumber), 0);
    const upperTick = Math.max(tickInterval, Math.ceil(maxTime / tickInterval) * tickInterval);
    const ticks: number[] = [];
    for (let t = 0; t <= upperTick; t += tickInterval) {
      ticks.push(t);
    }
    return ticks;
  })();

  const GazeScatterPlot = () => {
    const PADDING_LEFT = 10;
    const PADDING_RIGHT = 5;
    const PADDING_TOP = 6;
    const PADDING_BOTTOM = 12;
    const INNER_WIDTH = 100 - PADDING_LEFT - PADDING_RIGHT;
    const INNER_HEIGHT = 100 - PADDING_TOP - PADDING_BOTTOM;
    const HALF_WIDTH = INNER_WIDTH / 2;
    const HALF_HEIGHT = INNER_HEIGHT / 2;
    const rangeX = gazePlotData.rangeX || 1;
    const rangeY = gazePlotData.rangeY || 1;
    const centerX = PADDING_LEFT + HALF_WIDTH;
    const centerY = PADDING_TOP + HALF_HEIGHT;

    const mapX = (x: number) => centerX + (x / rangeX) * HALF_WIDTH;
    const mapY = (y: number) => centerY - (y / rangeY) * HALF_HEIGHT;

    const zeroX = centerX;
    const zeroY = centerY;

    return (
      <div className="w-full">
        <div className="text-sm text-gray-600 mb-2">
          <span>Samples: {gazePlotData.length}</span>
        </div>
        <svg viewBox="0 0 100 100" className="w-full h-64 bg-white rounded-md border border-yellow-200">
          {/* Frame */}
          <rect x={PADDING_LEFT} y={PADDING_TOP} width={INNER_WIDTH} height={INNER_HEIGHT} fill="#fff" stroke="#ddd" strokeWidth="0.5" />

          {/* Zero axes if within range */}
          <line x1={zeroX} y1={PADDING_TOP} x2={zeroX} y2={PADDING_TOP + INNER_HEIGHT} stroke="#bbb" strokeWidth="0.6" />
          <line x1={PADDING_LEFT} y1={zeroY} x2={PADDING_LEFT + INNER_WIDTH} y2={zeroY} stroke="#bbb" strokeWidth="0.6" />

          {/* Central focus circle */}
          <circle
            cx={centerX}
            cy={centerY}
            r={(0.075 / rangeX) * HALF_WIDTH}
            stroke="#f87171"
            strokeWidth="0.7"
            fill="none"
          />

          <circle
            cx={centerX}
            cy={centerY}
            r={(0.075 * 2 / rangeX) * HALF_WIDTH}
            stroke="#52a447"
            strokeWidth="0.7"
            fill="none"
          />
          {/* Points */}
          {gazePlotData.xs.map((x, idx) => (
            <circle key={idx} cx={mapX(x)} cy={mapY(gazePlotData.ys[idx])} r={1.5} fill="#eab308" fillOpacity="0.85" />
          ))}

          {/* Axis labels: min, 0, max on both axes */}
          {/* X axis labels */}
          <text x={PADDING_LEFT} y={PADDING_TOP + INNER_HEIGHT + 8} fontSize="3" fill="#666" textAnchor="start">
            {(-gazePlotData.maxAbsX).toFixed(1)}
          </text>
          <text x={zeroX} y={PADDING_TOP + INNER_HEIGHT + 8} fontSize="3" fill="#666" textAnchor="middle">0</text>
          <text x={PADDING_LEFT + INNER_WIDTH} y={PADDING_TOP + INNER_HEIGHT + 8} fontSize="3" fill="#666" textAnchor="end">
            {gazePlotData.maxAbsX.toFixed(1)}
          </text>

          {/* Y axis labels */}
          <text x={PADDING_LEFT - 2} y={PADDING_TOP + INNER_HEIGHT} fontSize="3" fill="#666" textAnchor="end">
            {(-gazePlotData.maxAbsY).toFixed(1)}
          </text>
          <text x={PADDING_LEFT - 2} y={zeroY + 1} fontSize="3" fill="#666" textAnchor="end">0</text>
          <text x={PADDING_LEFT - 2} y={PADDING_TOP + 3} fontSize="3" fill="#666" textAnchor="end">
            {gazePlotData.maxAbsY.toFixed(1)}
          </text>
        </svg>
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>Left (neg)</span>
          <span>Right (pos)</span>
        </div>
      </div>
    );
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      transition={{ duration: 0.8 }}
      className="space-y-6 reveal w-full"
    >
      {userInfo && (
        <div className="w-full text-center">
          <div className="p-2">
            <div className="flex flex-col items-center gap-1">
              <div className="text-[#80003a] font-display text-2xl font-semibold">
                {userInfo.name}
              </div>
              <div className="text-[#80003a] font-display text-xl font-semibold">
                Age: {userInfo.age}
              </div>
              <div className="text-[#80003a] font-display text-xl font-semibold">
                {userInfo.organization}
              </div>
              <div className="text-[#80003a] font-display text-xl font-semibold capitalize">
                {userInfo.role}
              </div>
            </div>
          </div>
        </div>
      )}
      <div className='flex items-center justify-center pt-2'>
        <h1 className='text-xl text-[#80003a]'>Verbal Communication</h1>
      </div>

      {/* Grid for various analysis metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Word Count */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="border-card border-yellow-500 bg-yellow-50 p-6 shadow-xl rounded-xl"
        >
          <h3 className="font-display text-lg text-yellow-700 mb-4">Linguistic Structures Counts</h3>
          <div className="space-y-3">
                <div>
                    <p className="text-sm font-medium text-yellow-600 mb-1">Letters</p>
                    <p className="text-2xl font-bold text-yellow-700">{results.letter_count}</p>
                </div>
                <div>
                    <p className="text-sm font-medium text-yellow-600 mb-1">Words</p>
                    <p className="text-2xl font-bold text-yellow-700">{results.word_count}</p>
                </div>
                <div>
                    <p className="text-sm font-medium text-yellow-600 mb-1">Sentences</p>
                    <p className="text-2xl font-bold text-yellow-700">{results.sentence_count}</p>
                </div>
                <div>
                    <p className="text-sm font-medium text-yellow-600 mb-1">Paragraphs</p>
                    <p className="text-2xl font-bold text-yellow-700">{results.paragraph_count}</p>
                </div>
            </div>
        </motion.div>

        {/* CEFR, IELTS & Readability */}
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="border-card border-teal-500 bg-teal-50 p-6 shadow-xl rounded-xl"
        >
            <h3 className="font-display text-lg text-teal-700 mb-4">Language Proficiency</h3>
            <div className="space-y-3">
                <div>
                    <p className="text-sm font-medium text-teal-600 mb-1">CEFR Level</p>
                    <p className="text-2xl font-bold text-teal-700">{results.cefr}</p>
                </div>
                <div>
                    <p className="text-sm font-medium text-teal-600 mb-1">IELTS Score</p>
                    <p className="text-2xl font-bold text-teal-700">{results.ielts}</p>
                </div>
                <div>
                    <p className="text-sm font-medium text-teal-600 mb-1">Readability Score</p>
                    <p className="text-2xl font-bold text-teal-700">{results.readability_score}</p>
                </div>
            </div>
        </motion.div>

        {/* Tone Analysis (Custom Tone Results) */}
        {/* {results.custom_tone_results && results.custom_tone_results.length > 0 && ( */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="border-card border-red-500 bg-red-50 p-6 shadow-xl rounded-xl"
          >
            <h3 className="font-display text-lg text-red-700 mb-2">Sentiment Analysis</h3>
            <ul className="space-y-2">
              {results.custom_tone_results.map(([score, label, emoji], idx) => (
                <li key={idx} className="flex items-center space-x-2">
                  <span className="text-2xl">{emoji}</span>
                  <span className="font-medium text-gray-800">{label}</span>
                  <span className="ml-auto font-semibold text-red-600">{(score * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
            
            {/* Extra Tone Results */}
            {results.extra_tone_results && results.extra_tone_results.length > 0 && (
              <div className="mt-4 pt-4 border-t border-red-300">
                <h4 className="font-display text-md text-red-600 mb-2">Other detected tones</h4>
                <ul className="space-y-2">
                  {results.extra_tone_results.map(([score, label, emoji], idx) => (
                    <li key={idx} className="flex items-center space-x-2">
                      <span className="font-bold text-gray-500 mr-2">{idx + 1}.</span>
                      <span className="text-2xl">{emoji}</span>
                      <span className="font-medium text-gray-800">{label}</span>
                      {/* <span className="ml-auto font-semibold text-red-600">{(score * 100).toFixed(1)}%</span> */}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        {/* )} */}

      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Parts of Speech Analysis Chart */}
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="md:col-span-2 border-card border-indigo-700 bg-indigo-50 p-6 shadow-xl rounded-xl"
        >
            <h3 className="font-display text-lg text-indigo-700 mb-4">Parts of Speech Distribution</h3>
            <div className="flex flex-col md:flex-row items-center justify-center">
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                        <Pie
                            data={Object.entries(results.parts_of_speech).map(([part, count]) => ({
                                name: part.replace('_', ' '), // Clean up name for display
                                value: count
                            }))}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                            labelLine={false}
                            label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                            animationBegin={0}
                            animationDuration={800}
                            animationEasing="ease-out"
                        >
                            {
                                Object.entries(results.parts_of_speech).map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={`hsl(${index * 60}, 70%, 50%)`} /> // Dynamic colors
                                ))
                            }
                        </Pie>
                        <Tooltip />
                        <Legend layout="vertical" align="right" verticalAlign="middle" />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
        {/* Parts of Speech Analysis Chart */}
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="md:col-span-1 border-card border-indigo-700 bg-indigo-50 p-6 shadow-xl rounded-xl"
        >
            <h3 className="font-display text-lg text-indigo-700 mb-4">Active & Passive Voice</h3>
            <div className="flex flex-col md:flex-row items-center justify-center">
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                        data={[
                            { name: 'Active', count: results.active },
                            { name: 'Passive', count: results.passive },
                        ]}
                        margin={{ top: 16, right: 16, left: 0, bottom: 16 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="count" name="Sentences">
                            <Cell key="cell-active" fill="#34d399" />
                            <Cell key="cell-passive" fill="#f87171" />
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
      </div>

      <div className='flex items-center justify-center pt-2'>
        <h1 className='text-xl text-[#80003a]'>Non-Verbal Communication</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* Rate of Speech Chart */}
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="border-card border-teal-500 bg-teal-50 p-6 shadow-xl rounded-xl"
        >
            <h3 className="font-display text-lg text-teal-700 mb-2">Rate of Speech (Words/Min)</h3>
            <ResponsiveContainer width="100%" height={200}>
                <LineChart data={results.rate_of_speech_points.map(([time, rate]) => ({
                    time: time.toFixed(1),
                    "Words/Min": (rate * 60).toFixed(1) // Convert to words per minute
                }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0f2f2" />
                    <XAxis dataKey="time" label={{ value: "Time (s)", position: "insideBottom", offset: -5 }} />
                    <YAxis label={{ value: "Words/Min", angle: -90, position: "insideLeft" }} />
                    <Tooltip
                        formatter={(value: any, name: string) => [`${value} ${name}`, `Time: ${name === "Words/Min" ? "" : name}s`]}
                        labelFormatter={(label: any) => `At ${label}s`}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="Words/Min" stroke="#009688" activeDot={{ r: 8 }} />
                </LineChart>
            </ResponsiveContainer>
        </motion.div>

        {/* Hand and Eye Activity Results */}
        {results.hand_eye_activity_results && (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="border-card border-red-500 bg-red-50 p-6 shadow-xl rounded-xl"
          >
            {/* <h3 className="font-display text-lg text-red-700 mb-2">Hand & Eye Activity</h3> */}
            <div className="space-y-3 text-sm">
              {/* Hand Activity */}
              {results.hand_eye_activity_results.hand_activity && (
                <div>
                  <h4 className="font-display text-lg text-red-700 mb-2">Gestures(Hand Activity):</h4>
                  {/* <h3 className="font-display text-lg text-teal-700 mb-2">Rate of Speech (Words/Min)</h3> */}
                  <div className="space-y-1 text-gray-700">
                    <p>Left Hand Avg: {results.hand_eye_activity_results.hand_activity.left_hand_avg_activity}%</p>
                    <p>Right Hand Avg: {results.hand_eye_activity_results.hand_activity.right_hand_avg_activity}%</p>
                    <p>Combined Avg: {results.hand_eye_activity_results.hand_activity.avg_combined_activity}%</p>
                    <p>Distance Changes: {results.hand_eye_activity_results.hand_activity.total_distance_changes}</p>
                    <p>Avg Distance Change/Frame: {results.hand_eye_activity_results.hand_activity.avg_distance_change_per_frame}</p>
                  </div>
                </div>
              )}
              
              {/* Eye Activity */}
              {results.hand_eye_activity_results.eye_activity && (
                <div>
                  <h4 className="font-display text-lg text-red-700 mb-2">Oculesics (Eyes Activity):</h4>
                  <div className="space-y-1 text-gray-700">
                    <p>Left Eyebrow Avg: {results.hand_eye_activity_results.eye_activity.left_eye_avg_activity}%</p>
                    <p>Right Eyebeow Avg: {results.hand_eye_activity_results.eye_activity.right_eye_avg_activity}%</p>
                    <p>Combined Eyebrows Avg: {results.hand_eye_activity_results.eye_activity.avg_combined_eye_activity}%</p>
                  </div>
                </div>
              )}
              
            </div>
          </motion.div>
        )}

        {/* Volume Analysis Chart */}
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="border-card border-orange-500 bg-orange-50 p-6 shadow-xl rounded-xl"
        >
            <h3 className="font-display text-lg text-orange-700 mb-2">Volume Levels Analysis</h3>
            <ResponsiveContainer width="100%" height={200}>
                <BarChart data={volumeChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffe0b2" />
                    <XAxis
                        dataKey="timePosition"
                        type="number"
                        domain={[
                          volumeTicks[0] ?? 0,
                          volumeTicks.length > 0
                            ? volumeTicks[volumeTicks.length - 1] + volumeBarOffset
                            : 'auto',
                        ]}
                        ticks={volumeTicks}
                        tickFormatter={(value: number) => `${value}s`}
                        label={{ value: "Time (s)", position: "insideBottom", offset: -5 }}
                        allowDecimals={false}
                    />
                    <YAxis label={{ value: "Volume (db)", angle: -90, position: "insideLeft" }} />
                    <Tooltip
                        labelFormatter={(label: number, payload: readonly { payload?: { originalTime?: number } }[]) => {
                          const originalTime = payload?.[0]?.payload?.originalTime ?? label - volumeBarOffset;
                          return `${Math.round(originalTime)}s`;
                        }}
                    />
                    <Legend />
                    <Bar dataKey="Volume" fill="#fb923c" />
                </BarChart>
            </ResponsiveContainer>
        </motion.div>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Hand Position Analysis */}
        {results.hand_position_results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="border-card border-gray-500 bg-gray-50 p-6 shadow-xl rounded-xl"
          >
            <h3 className="font-display text-xl text-gray-700 mb-4">Hand Position Analysis</h3>
            <StickmanVisualization handPositionData={results.hand_position_results} />
          </motion.div>
        )}
        {/* Gaze Analysis */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="border-card border-yellow-500 bg-yellow-50 p-6 shadow-xl rounded-xl"
        >
          <h3 className="font-display text-lg text-yellow-700 mb-3">Gaze Analysis</h3>
          {gazePlotData.length > 0 ? (
            <GazeScatterPlot />
          ) : (
            <p className="text-yellow-700">No gaze data available.</p>
          )}
        </motion.div>
      </div>


      <div className='flex items-center justify-center pt-2'>
        <h1 className='text-xl text-[#80003a]'>Speech Content</h1>
      </div>  

      <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          {/* Original Transcript */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="border-card border-green-500 bg-green-50 p-6 shadow-xl rounded-xl"
          >
            <h3 className="font-display text-xl text-green-700 mb-4">Original Transcript</h3>
            <p 
              className="font-body text-gray-800 leading-relaxed"
              dangerouslySetInnerHTML={{ 
                __html: applyUnderlinesToText(results.transcript, results.floss_spans || []) 
              }}
            />
          </motion.div>

          {/* Corrected Transcript with Highlights */}
          {results.corrected_transcript && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="border-card border-blue-500 bg-blue-50 p-6 shadow-xl rounded-xl flex flex-col gap-4 relative"
            >
              <h3 className="font-display text-xl text-blue-700 mb-4">Corrected Transcript</h3>
              <p
                className="font-body text-gray-800 leading-relaxed grammar-highlight"
                dangerouslySetInnerHTML={{ __html: results.corrected_transcript.replace(/<c>/g, '<span class="bg-yellow-300 px-1 rounded font-semibold underline decoration-wavy decoration-orange-500">').replace(/<\/c>/g, '</span>') }}
              />
              {copyAlertVisible && (
                <div className="absolute bottom-16 right-6 bg-blue-600 text-white text-xs font-medium px-3 py-1 rounded shadow-lg">
                  Copied!
                </div>
              )}
              <button
                type="button"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(results.corrected_transcript);
                    setCopyAlertVisible(true);
                    setTimeout(() => setCopyAlertVisible(false), 1000);
                  } catch (error) {
                    console.error("Failed to copy transcript", error);
                  }
                }}
                className="self-end px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors"
              >
                Copy Transcript
              </button>
              <style jsx global>{`
                .grammar-highlight span {
                  cursor: help;
                }
              `}</style>
            </motion.div>
          )}

          {/* Grammar Suggestions List */}
          {results.grammar_mistakes && results.grammar_mistakes.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="border-card border-purple-500 bg-purple-50 p-6 shadow-xl rounded-xl"
            >
              <h3 className="font-display text-xl text-purple-700 mb-4">Grammar Suggestions</h3>
              <ul className="list-disc pl-5 font-body text-gray-800 space-y-2">
                {results.grammar_mistakes.map((mistake, index) => {
                  const [range, suggestion, original] = mistake;
                  return (
                    <li key={index}>
                      "{original}" should be "{suggestion}"
                    </li>
                  );
                })}
              </ul>
            </motion.div>
          )}
      </div>

      
    </motion.div>
  );
} 
