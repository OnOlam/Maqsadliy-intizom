// 30+ PROFESSIONAL SHABLONLAR (global konstanta, o'zgarmaydi)
const DEFAULT_TEMPLATES = {
  error: true, project: true, concept: true, security: true, api: true,
  database: true, bug: true, refactor: true, word: true, book: true,
  notes: true, course: true, tutorial: true, research: true, meeting: true,
  idea: true, strategy: true, analysis: true, swot: true, business_plan: true,
  design: true, ux: true, wireframe: true, color_palette: true, habit: true,
  goal: true, reflection: true, journal: true, workout: true, expense: true,
  budget: true, investment: true, legal: true, contract: true, emotion: true,
  mindfulness: true, therapy: true,
};

const DEFAULT_SETTINGS = {
  timer: { workDuration: 25, breakDuration: 5 },
  templates: DEFAULT_TEMPLATES,
};

export const TEMPLATES_INFO = {
  error: { name: '❌ Xato va Yechimi', category: '💻 Dasturlash' },
  project: { name: '💡 Loyiha G\'oyasi', category: '💻 Dasturlash' },
  concept: { name: '🧠 Tushuncha', category: '💻 Dasturlash' },
  security: { name: '🛡️ Kiberxavfsizlik', category: '💻 Dasturlash' },
  api: { name: '🔌 API Hujjati', category: '💻 Dasturlash' },
  database: { name: '🗄️ Ma\'lumotlar Bazasi', category: '💻 Dasturlash' },
  bug: { name: '🐛 Bug Report', category: '💻 Dasturlash' },
  refactor: { name: '♻️ Refactoring', category: '💻 Dasturlash' },
  word: { name: '📚 Yangi So\'z', category: '🎓 Ta\'lim' },
  book: { name: '📖 Kitob Xulosasi', category: '🎓 Ta\'lim' },
  notes: { name: '📋 Dars Qaydlari', category: '🎓 Ta\'lim' },
  course: { name: '🎓 Kurs Qaydlari', category: '🎓 Ta\'lim' },
  tutorial: { name: '📺 Tutorial', category: '🎓 Ta\'lim' },
  research: { name: '🔬 Tadqiqot', category: '🎓 Ta\'lim' },
  meeting: { name: '🤝 Uchrashuv', category: '💼 Biznes' },
  idea: { name: '💼 Biznes G\'oya', category: '💼 Biznes' },
  strategy: { name: '🎯 Strategiya', category: '💼 Biznes' },
  analysis: { name: '📊 Tahlil', category: '💼 Biznes' },
  swot: { name: '📈 SWOT Tahlili', category: '💼 Biznes' },
  business_plan: { name: '📋 Biznes Reja', category: '💼 Biznes' },
  design: { name: '🎨 Dizayn', category: '🎨 Dizayn' },
  ux: { name: '🔍 UX Tadqiqot', category: '🎨 Dizayn' },
  wireframe: { name: '📐 Wireframe', category: '🎨 Dizayn' },
  color_palette: { name: '🌈 Rang Palitrasi', category: '🎨 Dizayn' },
  habit: { name: '🔄 Odat', category: '💪 Salomatlik' },
  goal: { name: '🎯 Maqsad', category: '💪 Salomatlik' },
  reflection: { name: '💭 Refleksiya', category: '💪 Salomatlik' },
  journal: { name: '📔 Kundalik', category: '💪 Salomatlik' },
  workout: { name: '💪 Mashq', category: '💪 Salomatlik' },
  expense: { name: '💰 Xarajat', category: '💵 Moliya' },
  budget: { name: '📊 Byudjet', category: '💵 Moliya' },
  investment: { name: '📈 Investitsiya', category: '💵 Moliya' },
  legal: { name: '⚖️ Huquqiy', category: '⚖️ Huquq' },
  contract: { name: '📄 Shartnoma', category: '⚖️ Huquq' },
  emotion: { name: '💚 His-tuyg\'u', category: '🧠 Psixologiya' },
  mindfulness: { name: '🧘 Mindfulness', category: '🧠 Psixologiya' },
  therapy: { name: '🛋️ Terapiya', category: '🧠 Psixologiya' },
};

// Timer presetlari (olimlar tavsiyasi) - global konstanta
export const TIMER_PRESETS = [
  { id: 'pomodoro', name: '🍅 Klassik Pomodoro', work: 25, break: 5, desc: 'Qisqa vazifalar uchun' },
  { id: 'deep', name: '🎯 Deep Work', work: 50, break: 10, desc: 'Chuqur ishlash' },
  { id: 'ultradian', name: '🌊 Ultradian Rhythm', work: 90, break: 20, desc: 'Ijodiy ishlar' },
  { id: 'flow', name: '🌟 Flow State', work: 120, break: 30, desc: 'Maksimal fokus' },
];

// ⭐ ENG MUHIM QISM: Har bir hotira uchun ALOHIDA kalit qaytarish
function getStorageKey() {
  const hotiraId = localStorage.getItem('active_hotira_id');
  return hotiraId ? `app_settings_${hotiraId}` : 'app_settings_default';
}

// Standart sozlamalarning toza nusxasini qaytarish
function getDefaultSettings() {
  return {
    timer: { ...DEFAULT_SETTINGS.timer },
    templates: { ...DEFAULT_TEMPLATES },
  };
}

export function getSettings() {
  try {
    const saved = localStorage.getItem(getStorageKey());
    if (saved) {
      const parsed = JSON.parse(saved);
      return {
        timer: { ...DEFAULT_SETTINGS.timer, ...parsed.timer },
        templates: { ...DEFAULT_TEMPLATES, ...parsed.templates },
      };
    }
  } catch (error) {
    console.error("Sozlamalarni o'qishda xato:", error);
  }
  return getDefaultSettings();
}

export function saveSettings(newSettings) {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(newSettings));
    window.dispatchEvent(new Event('settingsChanged'));
    return newSettings;
  } catch (error) {
    console.error("Sozlamalarni saqlashda xato:", error);
    return getSettings();
  }
}

export function resetSettings() {
  localStorage.removeItem(getStorageKey());
  window.dispatchEvent(new Event('settingsChanged'));
  return getDefaultSettings();
}
