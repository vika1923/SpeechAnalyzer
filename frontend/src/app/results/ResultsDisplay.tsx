"use client";
import {
  PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { motion } from "framer-motion";

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
  
  // Get alpha values (percentages as decimals, multiplied by 1.5, clamped between 0.1 and 0.8 for visibility)
  const getAlpha = (percentage: number) => {
    return Math.max(0.1, Math.min(0.9, (percentage * 1.6) / 100));
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative inline-block">
        {/* Stickman base image */}
        <img 
          src="/stickman.png" 
          alt="Stickman" 
          className="w-64 h-64 object-contain block"
        />
        
        {/* Overlay divs for 8 regions - positioned to match image exactly */}
        {/* Upper row */}
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: 0,
            left: 0,
            width: '50%',
            height: '24%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.uul || 0)})` 
          }}
          title={`Upper Upper Left: ${percentages.uul || 0}%`}
        />
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: 0,
            right: 0,
            width: '50%',
            height: '24%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.uur || 0)})` 
          }}
          title={`Upper Upper Right: ${percentages.uur || 0}%`}
        />
        
        {/* Upper middle row */}
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: '24%',
            left: 0,
            width: '50%',
            height: '18%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ul || 0)})` 
          }}
          title={`Upper Left: ${percentages.ul || 0}%`}
        />
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: '24%',
            right: 0,
            width: '50%',
            height: '18%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ur || 0)})` 
          }}
          title={`Upper Right: ${percentages.ur || 0}%`}
        />
        
        {/* Lower middle row */}
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: '42%',
            left: 0,
            width: '50%',
            height: '15%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.dl || 0)})` 
          }}
          title={`Down Left: ${percentages.dl || 0}%`}
        />
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: '42%',
            right: 0,
            width: '50%',
            height: '15%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.dr || 0)})` 
          }}
          title={`Down Right: ${percentages.dr || 0}%`}
        />
        
        {/* Bottom row */}
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: '57%',
            left: 0,
            width: '50%',
            height: '43%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ddl || 0)})` 
          }}
          title={`Down Down Left: ${percentages.ddl || 0}%`}
        />
        <div 
          className="absolute pointer-events-none"
          style={{ 
            top: '57%',
            right: 0,
            width: '50%',
            height: '43%',
            backgroundColor: `rgba(59, 130, 246, ${getAlpha(percentages.ddr || 0)})` 
          }}
          title={`Down Down Right: ${percentages.ddr || 0}%`}
        />
      </div>
      
      {/* Legend */}
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
      </div>
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
  hand_position_results: string;
  // Backend currently returns gaze_x/gaze_y; keep backward-compat with gaze_angle_x/gaze_angle_y
  gaze_x?: number[];
  gaze_y?: number[];
  gaze_angle_x?: number[];
  gaze_angle_y?: number[];
  aus_sum: number;
  blinks: number;
  active: number;
  passive: number;
  readability_score: string;
  cefr: string;
  ielts: string;
}

export default function ResultsDisplay({ results }: { results: AnalysisResults }) {
  // Prepare gaze arrays with fallback to older field names
  const gazeX: number[] = (results.gaze_x ?? results.gaze_angle_x ?? []) as number[];
  const gazeY: number[] = (results.gaze_y ?? results.gaze_angle_y ?? []) as number[];

  // Prepare raw-range-based plotting (supports negative and positive values)
  const gazePlotData = (() => {
    const length = Math.min(gazeX.length, gazeY.length);
    const xs = gazeX.slice(0, length);
    const ys = gazeY.slice(0, length);
    const hasData = length > 0;
    const minX = hasData ? Math.min(...xs) : 0;
    const maxX = hasData ? Math.max(...xs) : 1;
    const minY = hasData ? Math.min(...ys) : 0;
    const maxY = hasData ? Math.max(...ys) : 1;
    const spanX = maxX - minX || 1;
    const spanY = maxY - minY || 1;
    return { xs, ys, minX, maxX, minY, maxY, spanX, spanY, length };
  })();

  const GazeScatterPlot = () => {
    const PADDING_LEFT = 10;
    const PADDING_RIGHT = 5;
    const PADDING_TOP = 6;
    const PADDING_BOTTOM = 12;
    const INNER_WIDTH = 100 - PADDING_LEFT - PADDING_RIGHT;
    const INNER_HEIGHT = 100 - PADDING_TOP - PADDING_BOTTOM;

    const mapX = (x: number) => PADDING_LEFT + ((x - gazePlotData.minX) / gazePlotData.spanX) * INNER_WIDTH;
    const mapY = (y: number) => PADDING_TOP + ((gazePlotData.maxY - y) / gazePlotData.spanY) * INNER_HEIGHT;

    const zeroX = (gazePlotData.minX <= 0 && gazePlotData.maxX >= 0) ? mapX(0) : null;
    const zeroY = (gazePlotData.minY <= 0 && gazePlotData.maxY >= 0) ? mapY(0) : null;

    return (
      <div className="w-full">
        <div className="text-sm text-gray-600 mb-2">
          <span>Samples: {gazePlotData.length}</span>
        </div>
        <svg viewBox="0 0 100 100" className="w-full h-64 bg-white rounded-md border border-yellow-200">
          {/* Frame */}
          <rect x={PADDING_LEFT} y={PADDING_TOP} width={INNER_WIDTH} height={INNER_HEIGHT} fill="#fff" stroke="#ddd" strokeWidth="0.5" />

          {/* Zero axes if within range */}
          {zeroX !== null && (
            <line x1={zeroX} y1={PADDING_TOP} x2={zeroX} y2={PADDING_TOP + INNER_HEIGHT} stroke="#bbb" strokeWidth="0.6" />
          )}
          {zeroY !== null && (
            <line x1={PADDING_LEFT} y1={zeroY} x2={PADDING_LEFT + INNER_WIDTH} y2={zeroY} stroke="#bbb" strokeWidth="0.6" />
          )}

          {/* Points */}
          {gazePlotData.xs.map((x, idx) => (
            <circle key={idx} cx={mapX(x)} cy={mapY(gazePlotData.ys[idx])} r={1.5} fill="#eab308" fillOpacity="0.85" />
          ))}

          {/* Axis labels: min, 0, max on both axes */}
          {/* X axis labels */}
          <text x={PADDING_LEFT} y={PADDING_TOP + INNER_HEIGHT + 8} fontSize="3" fill="#666" textAnchor="start">{gazePlotData.minX.toFixed(1)}</text>
          {zeroX !== null && (
            <text x={zeroX} y={PADDING_TOP + INNER_HEIGHT + 8} fontSize="3" fill="#666" textAnchor="middle">0</text>
          )}
          <text x={PADDING_LEFT + INNER_WIDTH} y={PADDING_TOP + INNER_HEIGHT + 8} fontSize="3" fill="#666" textAnchor="end">{gazePlotData.maxX.toFixed(1)}</text>

          {/* Y axis labels */}
          <text x={PADDING_LEFT - 2} y={PADDING_TOP + INNER_HEIGHT} fontSize="3" fill="#666" textAnchor="end">{gazePlotData.minY.toFixed(1)}</text>
          {zeroY !== null && (
            <text x={PADDING_LEFT - 2} y={zeroY + 1} fontSize="3" fill="#666" textAnchor="end">0</text>
          )}
          <text x={PADDING_LEFT - 2} y={PADDING_TOP + 3} fontSize="3" fill="#666" textAnchor="end">{gazePlotData.maxY.toFixed(1)}</text>
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
      <div className='flex items-center justify-center pt-2'>
        <h1 className='text-xl text-[#80003a]'>Verbal part</h1>
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
            <h3 className="font-display text-lg text-indigo-700 mb-4">Active & Passive voice</h3>
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
        <h1 className='text-xl text-[#80003a]'>Visual part</h1>
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

        {/* Tone Analysis (Custom Tone Results) */}
        {/* {results.custom_tone_results && results.custom_tone_results.length > 0 && ( */}
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="border-card border-red-500 bg-red-50 p-6 shadow-xl rounded-xl"
          >
            <h3 className="font-display text-lg text-red-700 mb-2">Facial & hand activity</h3>
            <ul className="space-y-2">
              {results.custom_tone_results.map(([score, label, emoji], idx) => (
                <li key={idx} className="flex items-center space-x-2">
                  <span className="text-2xl">{emoji}</span>
                  <span className="font-medium text-gray-800">{label}</span>
                  <span className="ml-auto font-semibold text-red-600">{(score * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          </motion.div>
        {/* )} */}

        {/* Volume Analysis Chart */}
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="border-card border-orange-500 bg-orange-50 p-6 shadow-xl rounded-xl"
        >
            <h3 className="font-display text-lg text-orange-700 mb-2">Volume Analysis</h3>
            <ResponsiveContainer width="100%" height={200}>
                <BarChart data={Object.entries(results.volume_points).map(([time, volume]) => ({
                    time: time,
                    Volume: volume // Display raw decibels
                }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffe0b2" />
                    <XAxis dataKey="time" label={{ value: "Time Segment", position: "insideBottom", offset: -5 }} hide={true} /> {/* Hide X-axis labels if too many */}
                    <YAxis label={{ value: "Volume (%)", angle: -90, position: "insideLeft" }} />
                    <Tooltip />
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
        <h1 className='text-xl text-[#80003a]'>Text part</h1>
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
            <p className="font-body text-gray-800 leading-relaxed">{results.transcript}</p>
          </motion.div>

          {/* Corrected Transcript with Highlights */}
          {/* {results.corrected_transcript && results.corrected_transcript !== results.transcript && ( */}
            {/* <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="border-card border-blue-500 bg-blue-50 p-6 shadow-xl rounded-xl"
            > */}
              {/* <h3 className="font-display text-xl text-blue-700 mb-4">Corrected Transcript</h3>
              <p
                className="font-body text-gray-800 leading-relaxed grammar-highlight"
                dangerouslySetInnerHTML={{ __html: results.corrected_transcript.replace(/<c>/g, '<c>').replace(/<\/c>/g, '</c>') }}
              /> */}
              {/*
                <style jsx global>{`
                  .grammar-highlight c {
                    background-color: #ffd700;
                    padding: 0 2px;
                    border-radius: 3px;
                    font-weight: bold;
                    text-decoration: underline wavy #ff4500;
                  }

                  .grammar-highlight c:hover {
                    cursor: help;
                  }
                `}</style>
                */}
            {/* </motion.div> */}
          {/* )} */}

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

      

      

      

      {/* OpenFace section removed - not needed */}
    </motion.div>
  );
} 
