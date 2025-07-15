"use client";
import {
  PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { motion } from "framer-motion";

interface AnalysisResults {
  transcript: string;
  corrected_transcript: string;
  word_count: number;
  rate_of_speech_points: [number, number][];
  volume_points: Record<string, number>;
  tone_scores?: Record<string, number>;
  parts_of_speech: Record<string, number>;
  grammar_mistakes: [[number, number], string, string][];
  custom_tone_results: [number, string, string][];
  hand_position_results: string;
  gaze_angle_x?: number;
  gaze_angle_y?: number;
  all_aus_sum?: number;
}

export default function ResultsDisplay({ results }: { results: AnalysisResults }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      transition={{ duration: 0.8 }}
      className="space-y-6 reveal w-full"
    >
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
      {results.corrected_transcript && results.corrected_transcript !== results.transcript && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="border-card border-blue-500 bg-blue-50 p-6 shadow-xl rounded-xl"
        >
          <h3 className="font-display text-xl text-blue-700 mb-4">Corrected Transcript</h3>
          <p
            className="font-body text-gray-800 leading-relaxed grammar-highlight"
            dangerouslySetInnerHTML={{ __html: results.corrected_transcript.replace(/<c>/g, '<c>').replace(/<\/c>/g, '</c>') }}
          />
          <style jsx global>{`
            .grammar-highlight c {
              background-color: #ffd700; /* Gold-like background for highlight */
              padding: 0 2px;
              border-radius: 3px;
              font-weight: bold;
              text-decoration: underline wavy #ff4500; /* OrangeRed underline for mistakes */
            }
            .grammar-highlight c:hover {
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

      {/* Grid for various analysis metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Word Count */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="border-card border-yellow-500 bg-yellow-50 p-6 shadow-xl rounded-xl"
        >
          <h3 className="font-display text-lg text-yellow-700 mb-2">Word Count</h3>
          <p className="text-3xl font-bold text-yellow-600">{results.word_count}</p>
        </motion.div>

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
                    Volume: Math.min(Math.max(volume * 100, 0), 100) // Scale to 0-100 for display
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

        {/* Tone Analysis (Custom Tone Results) */}
        {results.custom_tone_results && results.custom_tone_results.length > 0 && (
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
        )}
      </div>

      {/* Parts of Speech Analysis Chart */}
      <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="border-card border-indigo-700 bg-indigo-50 p-6 shadow-xl rounded-xl"
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

      {/* Hand Position Analysis */}
      {results.hand_position_results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="border-card border-gray-500 bg-gray-50 p-6 shadow-xl rounded-xl"
        >
          <h3 className="font-display text-xl text-gray-700 mb-4">Hand Position Analysis</h3>
          <pre className="font-mono text-sm text-gray-800 whitespace-pre-wrap">{results.hand_position_results}</pre>
        </motion.div>
      )}

      {/* OpenFace Gaze & AU Analysis */}
      { results.gaze_angle_x && results.gaze_angle_y && results.all_aus_sum && (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="border-card border-pink-500 bg-pink-50 p-6 shadow-xl rounded-xl"
      >
        <h3 className="font-display text-xl text-pink-700 mb-4">OpenFace Gaze & AU Analysis</h3>
        <div className="font-body text-gray-800 space-y-2">
          <div><span className="font-semibold">Gaze Angle X:</span> {results.gaze_angle_x?.toFixed(3)}</div>
          <div><span className="font-semibold">Gaze Angle Y:</span> {results.gaze_angle_y?.toFixed(3)}</div>
          <div><span className="font-semibold">Sum of All AU Diffs:</span> {results.all_aus_sum?.toFixed(3)}</div>
        </div>
      </motion.div>
      )}
    </motion.div>
  );
} 
