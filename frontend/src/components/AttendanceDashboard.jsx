import React, { useEffect, useRef, useState } from 'react';
import Sidebar from './Sidebar';
import MetricsPanel from './MetricsPanel';
import AudioCapture from './AudioCapture';
import RecommendationsPanel from './RecommendationsPanel';
import AnalyticsPage from './AnalyticsPage';
import TeacherProfile from './TeacherProfile';
import SuggestionBox from './SuggestionBox';
import GamificationPanel from './GamificationPanel';
import { BarChart2, LayoutDashboard, UserCheck, Zap } from 'lucide-react';

const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000';

const AttendanceDashboard = () => {
    const [sessionActive, setSessionActive] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [peopleCount, setPeopleCount] = useState(0);
    const [duration, setDuration] = useState(0);
    const [videoSrc, setVideoSrc] = useState(null);
    const [view, setView] = useState('dashboard'); // dashboard | analytics | teacher

    // Metrics State
    const [emotionCounts, setEmotionCounts] = useState({ happy: 0, neutral: 0, bored: 0, confused: 0 });
    const [audioMetrics, setAudioMetrics] = useState({ noise_db: 0, activity_type: 'Quiet' });
    const [insight, setInsight] = useState(null);
    const [loadingInsight, setLoadingInsight] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);

    const wsVideo = useRef(null);
    const timerRef = useRef(null);

    // Initial check
    useEffect(() => {
        fetchStatus();
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/session/status`);
            const data = await res.json();
            setSessionActive(data.active);
            if (data.id) setSessionId(data.id);
            if (data.active && data.duration) setDuration(data.duration);
        } catch (e) {
            console.error("Status fetch failed", e);
        }
    };

    const fetchInsight = async () => {
        setLoadingInsight(true);
        try {
            const res = await fetch(`${API_BASE}/api/insights/classroom`);
            const data = await res.json();
            setInsight(data.insight);
        } catch (e) { console.error("Insight failed"); }
        setLoadingInsight(false);
    };

    const handleStart = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ teacher_id: "T1", class_id: "C1" })
            });
            const data = await res.json();
            if (data.status === 'started') {
                setSessionActive(true);
                setSessionId(data.session_id);
                startTimer();
                connectVideoWebSocket();
            }
        } catch (e) { alert("Failed to start"); }
    };

    const handleStop = async () => {
        try {
            await fetch(`${API_BASE}/api/session/stop`, { method: 'POST' });
            setSessionActive(false);
            stopTimer();
            if (wsVideo.current) wsVideo.current.close();
            setVideoSrc(null);
            setView('analytics');
        } catch (e) { alert("Failed to stop"); }
    };

    const startTimer = () => {
        if (timerRef.current) clearInterval(timerRef.current);
        const startTime = Date.now() - (duration * 1000);
        timerRef.current = setInterval(() => {
            setDuration(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
    };
    const stopTimer = () => { if (timerRef.current) clearInterval(timerRef.current); };

    const connectVideoWebSocket = () => {
        if (wsVideo.current) wsVideo.current.close();
        wsVideo.current = new WebSocket(`${WS_BASE}/ws/video`);
        wsVideo.current.binaryType = 'blob'; // Or string if mixed
        wsVideo.current.onopen = () => console.log("Video WS Connected");
        wsVideo.current.onmessage = (event) => {
            if (typeof event.data === 'string') {
                try {
                    const metrics = JSON.parse(event.data);
                    if (metrics.total_people !== undefined) setPeopleCount(metrics.total_people);
                    if (metrics.recommendations) setRecommendations(metrics.recommendations);
                    if (metrics.leaderboard) setLeaderboard(metrics.leaderboard);

                    if (metrics.people) {
                        const counts = { happy: 0, neutral: 0, bored: 0, confused: 0, sad: 0, frustrated: 0, anxious: 0 };
                        metrics.people.forEach(p => {
                            if (counts[p.emotion] !== undefined) counts[p.emotion]++;
                            else counts[p.emotion] = 1;
                        });
                        setEmotionCounts(counts);
                    }
                } catch (e) { console.error("Parse error", e); }
            } else {
                const url = URL.createObjectURL(event.data);
                setVideoSrc(prev => {
                    if (prev) URL.revokeObjectURL(prev);
                    return url;
                });
            }
        };
    };

    useEffect(() => {
        if (sessionActive) {
            connectVideoWebSocket();
            startTimer();
        }
        return () => {
            stopTimer();
            if (wsVideo.current) wsVideo.current.close();
        };
    }, [sessionActive]);

    if (view === 'analytics') {
        return (
            <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans flex-col">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
                    <h2 className="font-bold text-xl">Analytics & Reports</h2>
                    <button onClick={() => setView('dashboard')} className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 flex gap-2 items-center">
                        <LayoutDashboard size={18} /> Back to Dashboard
                    </button>
                </div>
                <div className="flex-1 overflow-auto">
                    <AnalyticsPage sessionId={sessionId} />
                </div>
            </div>
        );
    }

    if (view === 'teacher') {
        return (
            <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans flex-col">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
                    <h2 className="font-bold text-xl">Teacher Central</h2>
                    <button onClick={() => setView('dashboard')} className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 flex gap-2 items-center">
                        <LayoutDashboard size={18} /> Back to Dashboard
                    </button>
                </div>
                <div className="flex-1 overflow-auto">
                    <TeacherProfile />
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans">
            <Sidebar
                sessionActive={sessionActive}
                peopleCount={peopleCount}
                duration={duration}
                onStart={handleStart}
                onStop={handleStop}
            />

            <AudioCapture active={sessionActive} onMetrics={setAudioMetrics} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col relative bg-slate-950">

                {/* Top Overlay Buttons */}
                <div className="absolute top-4 right-4 z-40 flex gap-2">
                    <button onClick={() => setView('teacher')} className="bg-slate-800/80 backdrop-blur p-2 rounded-lg hover:bg-slate-700 border border-slate-700 text-slate-300 transition" title="Teacher Profile">
                        <UserCheck size={24} />
                    </button>
                    {sessionId && (
                        <button onClick={() => setView('analytics')} className="bg-slate-800/80 backdrop-blur p-2 rounded-lg hover:bg-slate-700 border border-slate-700 text-slate-300 transition" title="View Analytics">
                            <BarChart2 size={24} />
                        </button>
                    )}
                </div>

                {/* Recommendations Overlay */}
                <RecommendationsPanel recommendations={recommendations} />

                {/* Video Stage */}
                <div className="flex-[3] relative flex items-center justify-center overflow-hidden p-4">
                    {videoSrc ? (
                        <div className="relative w-full h-full max-w-5xl aspect-video rounded-2xl overflow-hidden shadow-2xl border border-slate-800 bg-black">
                            <img src={videoSrc} alt="Live Feed" className="w-full h-full object-contain" />
                            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-xs font-mono text-green-400 border border-green-500/30 flex items-center">
                                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                                LIVE
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center text-center p-12 max-w-2xl w-full">
                            {/* Landing Content ... */}
                            <div className="mb-8 relative">
                                <div className="absolute inset-0 bg-blue-500 blur-3xl opacity-20 rounded-full"></div>
                                <div className="relative bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-2xl">
                                    <div className="text-6xl mb-2">🎓</div>
                                </div>
                            </div>
                            <h2 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">EduSense AI <span className="text-sm font-mono text-slate-400 ml-2">v4.0</span></h2>
                            <p className="text-slate-400 text-lg mb-8 max-w-md">Teacher Intelligence & Gamification Active</p>
                            <div className="flex gap-4">
                                <button onClick={handleStart} className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-900/40 transition-all flex items-center">
                                    <span>Start Session</span><span className="ml-2">→</span>
                                </button>
                                <button onClick={() => setView('teacher')} className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium border border-slate-700">Teacher Profile</button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Bottom Phase 4 Config Panel */}
                {sessionActive && (
                    <div className="flex-1 bg-slate-900/50 border-t border-slate-800 p-4 grid grid-cols-2 gap-4 h-64 overflow-hidden">
                        <GamificationPanel leaderboard={leaderboard} />
                        <SuggestionBox />
                    </div>
                )}
            </div>

            <MetricsPanel
                emotionCounts={emotionCounts}
                audioMetrics={audioMetrics}
                insights={insight}
                loadingInsights={loadingInsight}
                onRefreshInsights={fetchInsight}
            />
        </div>
    );
};

export default AttendanceDashboard;
