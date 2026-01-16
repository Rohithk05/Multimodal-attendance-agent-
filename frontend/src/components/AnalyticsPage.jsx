import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Download, Calendar, Filter } from 'lucide-react';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300'];

const AnalyticsPage = ({ sessionId }) => {
    const [trendData, setTrendData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (sessionId) {
            fetchTrends(sessionId);
        }
    }, [sessionId]);

    const fetchTrends = async (sid) => {
        try {
            const res = await fetch(`http://localhost:8000/api/analytics/trends/${sid}`);
            const data = await res.json();
            setTrendData(data);
        } catch (e) {
            console.error("Failed to fetch trends", e);
        } finally {
            setLoading(false);
        }
    };

    const handleExport = (type) => {
        window.location.href = `http://localhost:8000/api/reports/export/${sessionId}/${type}`;
    };

    if (loading) return <div className="p-8 text-white">Loading Analytics...</div>;

    return (
        <div className="p-6 bg-slate-950 min-h-screen text-white">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
                        Session Analytics
                    </h1>
                    <p className="text-slate-400">Deep dive into clssroom engagement</p>
                </div>
                <div className="flex gap-4">
                    <button onClick={() => handleExport('pdf')} className="flex items-center gap-2 px-4 py-2 bg-red-600 rounded hover:bg-red-500 transition">
                        <Download size={18} /> PDF Report
                    </button>
                    <button onClick={() => handleExport('csv')} className="flex items-center gap-2 px-4 py-2 bg-green-600 rounded hover:bg-green-500 transition">
                        <Download size={18} /> CSV Data
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Attention Trend */}
                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                    <h3 className="text-lg font-semibold mb-4">Attention Trend</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="time" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                                <Legend />
                                <Line type="monotone" dataKey="avg_attention" stroke="#8884d8" strokeWidth={3} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Emotion Stack */}
                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                    <h3 className="text-lg font-semibold mb-4">Emotion Distribution Over Time</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="time" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                                <Bar dataKey="happy" stackId="a" fill="#4ade80" />
                                <Bar dataKey="neutral" stackId="a" fill="#94a3b8" />
                                <Bar dataKey="bored" stackId="a" fill="#f87171" />
                                <Bar dataKey="confused" stackId="a" fill="#fbbf24" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
