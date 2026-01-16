import React, { useEffect, useState } from 'react';
import { Trophy, TrendingUp, BookOpen, AlertCircle, Award } from 'lucide-react';

const TeacherProfile = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Mocking ID for now
        fetchProfile("T1");
    }, []);

    const fetchProfile = async (id) => {
        try {
            const res = await fetch(`http://localhost:8000/api/teacher/profile/${id}`);
            const data = await res.json();
            setProfile(data);
        } catch (e) {
            console.error("Failed to load profile", e);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-white">Loading Profile...</div>;
    if (!profile) return <div className="p-8 text-white">Profile not found.</div>;

    return (
        <div className="p-8 bg-slate-950 min-h-screen text-white">
            <header className="mb-12">
                <h1 className="text-4xl font-bold mb-2">Teacher Profile</h1>
                <p className="text-slate-400">Effectiveness Dashboard & Insights</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                {/* Effectiveness Score */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Award size={100} />
                    </div>
                    <h3 className="text-slate-400 font-medium mb-4 uppercase tracking-widest">Teaching Effectiveness</h3>
                    <div className="flex items-baseline gap-4">
                        <span className="text-6xl font-bold text-green-400">{profile.effectiveness_score}</span>
                        <span className="text-xl text-slate-500">/ 100</span>
                    </div>
                    <div className="mt-4 flex items-center text-green-500 bg-green-900/20 py-1 px-3 rounded-full w-fit">
                        <TrendingUp size={16} className="mr-2" />
                        <span>+{profile.trend}% 30-day trend</span>
                    </div>
                </div>

                {/* Teaching Strengths */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h3 className="text-slate-400 font-medium mb-4 uppercase tracking-widest flex items-center gap-2">
                        <Trophy size={18} className="text-yellow-500" /> Strengths
                    </h3>
                    <ul className="space-y-3">
                        {profile.strengths.map((s, i) => (
                            <li key={i} className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                                <span>{s}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Recommended Actions */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h3 className="text-slate-400 font-medium mb-4 uppercase tracking-widest flex items-center gap-2">
                        <BookOpen size={18} className="text-blue-500" /> Recommendations
                    </h3>
                    <ul className="space-y-3">
                        {profile.recommended_actions.map((s, i) => (
                            <li key={i} className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                <span>{s}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Class History */}
            <div className="mb-12">
                <h2 className="text-2xl font-bold mb-6">Class History Comparison</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {profile.class_history.map((cls, i) => (
                        <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-xl hover:bg-slate-800 transition">
                            <h4 className="font-bold text-lg">{cls.name}</h4>
                            <div className="mt-2 text-2xl font-mono text-purple-400">{cls.engagement}% Avg</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TeacherProfile;
