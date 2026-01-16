import React from 'react';
import { Mic, Activity, Volume2 } from 'lucide-react';

const AudioDisplay = ({ metrics }) => {
    const { noise_db, speech_ratio, activity_type, engagement_level } = metrics || {};

    // Format values
    const db = noise_db ? Math.round(noise_db) : 0;
    // const speech = speech_ratio ? Math.round(speech_ratio * 100) : 0;

    // Normalize dB for display (20dB to 80dB range)
    const percentage = Math.min(100, Math.max(0, ((db - 20) / 60) * 100));

    const getActivityColor = (type) => {
        switch (type) {
            case 'silent': return 'text-slate-400';
            case 'normal_discussion': return 'text-green-400';
            case 'chaotic_loud': return 'text-red-400';
            default: return 'text-slate-400';
        }
    };

    return (
        <div className="bg-slate-800/30 rounded-2xl p-6 border border-slate-700 backdrop-blur-sm">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
                <Mic className="w-5 h-5 text-blue-400" />
                Audio Analysis
            </h3>

            <div className="space-y-6">
                {/* Noise Gauge */}
                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-slate-400 flex items-center gap-2">
                            <Volume2 className="w-4 h-4" /> Noise Level
                        </span>
                        <span className="font-mono font-bold text-white">{db} dB</span>
                    </div>
                    <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden relative">
                        <div
                            className={`h-full transition-all duration-300 ease-out bg-gradient-to-r from-green-400 via-yellow-400 to-red-500`}
                            style={{ width: `${percentage}%` }}
                        />
                        {/* Markers for 20, 50, 80 */}
                        <div className="absolute top-0 bottom-0 left-[0%] w-0.5 bg-slate-900/50"></div>
                        <div className="absolute top-0 bottom-0 left-[50%] w-0.5 bg-slate-900/50"></div>
                        <div className="absolute top-0 bottom-0 right-[0%] w-0.5 bg-slate-900/50"></div>
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                        <span>20dB</span>
                        <span>50dB</span>
                        <span>80dB+</span>
                    </div>
                </div>

                {/* Activity Status */}
                <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50">
                    <div className="flex items-center gap-3">
                        <Activity className={`w-5 h-5 ${getActivityColor(activity_type)}`} />
                        <div>
                            <div className="text-xs text-slate-500 uppercase tracking-wider">Current State</div>
                            <div className={`font-semibold capitalize ${getActivityColor(activity_type)}`}>
                                {activity_type ? activity_type.replace('_', ' ') : 'Waiting...'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AudioDisplay;
