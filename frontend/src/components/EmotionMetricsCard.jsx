import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const EmotionMetricsCard = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    const processData = (history) => {
        // Count occurrences
        const counts = {};
        history.forEach(item => {
            const em = item.emotion || 'unknown';
            counts[em] = (counts[em] || 0) + 1;
        });

        const total = history.length;
        return Object.keys(counts).map(key => ({
            name: key,
            value: counts[key],
            percentage: Math.round((counts[key] / total) * 100)
        }));
    };

    const fetchData = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/history/emotions?limit=100');
            const history = await res.json();
            const chartData = processData(history);
            setData(chartData);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch emotion metrics", err);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Update every 5s
        return () => clearInterval(interval);
    }, []);

    const COLORS = {
        happy: '#4ade80',    // green-400
        neutral: '#94a3b8',  // slate-400
        surprise: '#facc15', // yellow-400
        sad: '#60a5fa',      // blue-400
        angry: '#f87171',    // red-400
        fear: '#c084fc',     // purple-400
        disgust: '#a3e635',  // lime-400
        unknown: '#475569'
    };

    return (
        <div className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700 backdrop-blur-sm h-80 flex flex-col">
            <h3 className="text-lg font-semibold mb-4 text-white">Emotion Distribution (Last 5 mins)</h3>

            {loading ? (
                <div className="flex-1 flex items-center justify-center text-slate-500">Loading...</div>
            ) : data.length === 0 ? (
                <div className="flex-1 flex items-center justify-center text-slate-500">No data yet</div>
            ) : (
                <div className="flex-1 w-full h-full min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#cbd5e1'} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                                itemStyle={{ color: '#f8fafc' }}
                            />
                            <Legend verticalAlign="bottom" height={36} iconType="circle" />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
};

export default EmotionMetricsCard;
