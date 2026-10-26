import { useState, useEffect } from 'react';
import { Clock, Play, Pause, RotateCcw, CheckCircle } from 'lucide-react';
import { getSettings } from '../utils/settings';

export default function PomodoroTimer() {
  // Joriy faol hotira id si (har bir hotira o'z timeriga ega bo'lishi uchun)
  const activeHotiraId = localStorage.getItem('active_hotira_id') || 'default';
  
  // ⭐ KALIT ENDI HOTIRAGA BOG'LIQ!
  const STORAGE_KEY = `aqlli_daftar_timer_state_${activeHotiraId}`;

  const settings = getSettings();
  const workDuration = (settings.timer?.workDuration || 25) * 60;
  const breakDuration = (settings.timer?.breakDuration || 5) * 60;

  // 1. Boshlang'ich holatni SHU HOTIRANING localStorage idan yuklash
  const getInitialState = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.isRunning && parsed.endTime) {
          const remaining = Math.floor((parsed.endTime - Date.now()) / 1000);
          if (remaining > 0) {
            return { timeLeft: remaining, mode: parsed.mode, isRunning: true, endTime: parsed.endTime };
          }
        }
        if (!parsed.isRunning && parsed.timeLeft > 0) {
          return { timeLeft: parsed.timeLeft, mode: parsed.mode, isRunning: false, endTime: null };
        }
      }
    } catch (e) {
      console.error("Timer holatini yuklashda xato:", e);
    }
    return { timeLeft: workDuration, mode: 'work', isRunning: false, endTime: null };
  };

  const [state, setState] = useState(getInitialState);
  const { timeLeft, mode, isRunning, endTime } = state;
  const [completedSessions, setCompletedSessions] = useState(0);

  // 2. Holat o'zgarganda SHU HOTIRANING kalitiga saqlash
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ timeLeft, mode, isRunning, endTime }));
  }, [timeLeft, mode, isRunning, endTime, STORAGE_KEY]);

  // 3. Sozlama o'zgarganda KATTA SOATNI yangilash (timer ishlamayotgan bo'lsa)
  useEffect(() => {
    if (!isRunning) {
      setState(prev => ({
        ...prev,
        timeLeft: prev.mode === 'work' ? workDuration : breakDuration
      }));
    }
  }, [workDuration, breakDuration]);

  // 4. Timer mexanizmi
  useEffect(() => {
    let interval;
    if (isRunning && endTime) {
      interval = setInterval(() => {
        const now = Date.now();
        const remaining = Math.floor((endTime - now) / 1000);

        if (remaining <= 0) {
          clearInterval(interval);
          const newMode = mode === 'work' ? 'break' : 'work';
          const newDuration = newMode === 'work' ? workDuration : breakDuration;
          const newEndTime = Date.now() + newDuration * 1000;

          setState({ timeLeft: newDuration, mode: newMode, isRunning: true, endTime: newEndTime });
          if (mode === 'work') setCompletedSessions(prev => prev + 1);
        } else {
          setState(prev => ({ ...prev, timeLeft: remaining }));
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, endTime, mode, workDuration, breakDuration]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStart = () => {
    const newEndTime = Date.now() + timeLeft * 1000;
    setState(prev => ({ ...prev, isRunning: true, endTime: newEndTime }));
  };

  const handlePause = () => {
    setState(prev => ({ ...prev, isRunning: false, endTime: null }));
  };

  const handleReset = () => {
    setState({ timeLeft: mode === 'work' ? workDuration : breakDuration, mode: mode, isRunning: false, endTime: null });
  };

  return (
    <div className="card bg-card border-line rounded-2xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Clock size={20} className="text-ink-soft" />
          <h3 className="font-serif font-semibold text-lg">
            {mode === 'work' ? 'Ish vaqti' : 'Dam vaqti'}
          </h3>
        </div>
        {completedSessions > 0 && (
          <div className="flex items-center gap-1 text-ink-soft">
            <CheckCircle size={16} />
            <span>{completedSessions} ta</span>
          </div>
        )}
      </div>

      <div className="text-center mb-4">
        <div className="text-4xl font-mono font-bold text-ink">
          {formatTime(timeLeft)}
        </div>
        <div className="text-xs text-ink-soft mt-1">
          {mode === 'work'
            ? `${settings.timer?.workDuration || 25} daqiqa ish`
            : `${settings.timer?.breakDuration || 5} daqiqa dam`}
        </div>
      </div>

      <div className="flex justify-center gap-3">
        {isRunning ? (
          <button onClick={handlePause} className="p-3 rounded-xl bg-rose text-cream hover:bg-rose/80 transition-all" title="To'xtatish">
            <Pause size={20} />
          </button>
        ) : (
          <button onClick={handleStart} className="p-3 rounded-xl bg-sage text-cream hover:bg-sage/80 transition-all" title="Boshlash">
            <Play size={20} />
          </button>
        )}
        <button onClick={handleReset} className="p-3 rounded-xl bg-line/30 text-ink-soft hover:bg-line/50 transition-all" title="Qayta boshlash">
          <RotateCcw size={20} />
        </button>
      </div>
    </div>
  );
}
