import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Sparkles, FolderOpen, AlertTriangle } from 'lucide-react';
import PomodoroTimer from '../components/PomodoroTimer';
import { getSettings } from '../utils/settings';

export default function HomePage() {
  const settings = getSettings();
  
  const [activeHotiraId, setActiveHotiraId] = useState(null);
  
  useEffect(() => {
    setActiveHotiraId(localStorage.getItem('active_hotira_id'));
    const handleChange = () => setActiveHotiraId(localStorage.getItem('active_hotira_id'));
    window.addEventListener('hotiraChanged', handleChange);
    return () => window.removeEventListener('hotiraChanged', handleChange);
  }, []);

  // ⭐ SEHRLI KALIT: vaqt O'ZGARGANDA ham, hotira O'ZGARGANDA ham timer qayta yaratiladi
  const timerKey = `timer-${settings.timer.workDuration}-${settings.timer.breakDuration}-${activeHotiraId}`;

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-sage-bg to-cream border border-line rounded-2xl p-6 md:p-8">
        <div className="flex items-center gap-3 mb-2">
          <Sparkles size={24} className="text-sage" />
          <h1 className="font-serif font-bold text-2xl md:text-3xl text-ink">
            Xush kelibsiz!
          </h1>
        </div>
        <p className="text-ink-soft max-w-2xl">
          Bilimingizni oshirish va yozuvlaringizni tartibga solish uchun ajoyib joydasiz.
        </p>
      </div>

      <div>
        <PomodoroTimer key={timerKey} />
      </div>

      {activeHotiraId ? (
        <div className="card text-center py-8">
          <p className="text-ink-soft mb-4">Yangi yozuv qo'shishga tayyormisiz?</p>
          <Link
            to="/notes/new"
            className="inline-flex items-center gap-2 bg-ink text-cream font-semibold px-6 py-3 rounded-xl hover:bg-ink/90 transition-colors"
          >
            <Plus size={18} />
            Yangi yozuv yaratish
          </Link>
        </div>
      ) : (
        <div className="card border-gold/30 bg-gold-bg/30 text-center py-8">
          <div className="w-14 h-14 rounded-2xl bg-gold/20 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle size={28} className="text-gold" />
          </div>
          <h3 className="font-serif font-semibold text-lg mb-2">Avval hotira tanlang!</h3>
          <p className="text-sm text-ink-soft mb-4 max-w-md mx-auto">
            Yozuv yozishni boshlashdan oldin, ish maydonini (hotirani) yarating yoki mavjudlaridan birini tanlang. Bu sizning ma'lumotlaringizni tartibli saqlashga yordam beradi.
          </p>
          <Link
            to="/hotira"
            className="inline-flex items-center gap-2 bg-gold text-cream font-semibold px-6 py-3 rounded-xl hover:bg-gold/90 transition-colors"
          >
            <FolderOpen size={18} />
            Hotira bo'limiga o'tish
          </Link>
        </div>
      )}
    </div>
  );
}
