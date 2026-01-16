import React from 'react';
import { Medal, Flame } from 'lucide-react';

const GamificationPanel = ({ leaderboard }) => {
    if (!leaderboard || leaderboard.length === 0) return (
        <div className="text-center text-slate-500 py-8 text-sm">
            Start session to see live leaderboard
        </div>
    );

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-full">
            <h3 className="text-sm font-bold uppercase tracking-widest text-yellow-400 mb-4 flex items-center gap-2">
                <Medal size={16} /> Live Leaderboard
            </h3>

            <div className="space-y-2">
                {leaderboard.map((student, idx) => (
                    <div key={student.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:bg-slate-800 transition">
                        <div className="flex items-center gap-3">
                            <div className={`w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs
                            ${idx === 0 ? 'bg-yellow-500 text-black shadow-lg shadow-yellow-500/20' :
                                    idx === 1 ? 'bg-slate-300 text-black' :
                                        idx === 2 ? 'bg-orange-400 text-black' :
                                            'bg-slate-700 text-slate-400'}`}>
                                {idx + 1}
                            </div>
                            <div>
                                <p className="font-medium text-sm">Student {student.id}</p>
                                {student.badge && (
                                    <span className="text-[10px] bg-orange-500/10 text-orange-400 px-1.5 py-0.5 rounded flex items-center gap-1 w-fit">
                                        <Flame size={8} /> {student.badge}
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className="font-mono font-bold text-green-400 text-sm">
                            {student.points} pts
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GamificationPanel;
