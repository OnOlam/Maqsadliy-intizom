import { useState, useEffect, useRef } from 'react';
import {
  Download, Upload, Trash2, AlertTriangle,
  CheckCircle, XCircle, FileJson, Database,
  Clock, FileText, RotateCcw, Save, X
} from 'lucide-react';
import { exportAllData, importData, clearAllData } from '../utils/exportImport';
import { getAllNotes, getAllCategories } from '../db/database';
import { getSettings, saveSettings, resetSettings, TEMPLATES_INFO, TIMER_PRESETS } from '../utils/settings';

export default function SettingsPage() {
  const fileInputRef = useRef(null);
  const [message, setMessage] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);

  const [savedSettings, setSavedSettings] = useState(getSettings());
  const [localSettings, setLocalSettings] = useState(getSettings());
  const [hasChanges, setHasChanges] = useState(false);

  // Timer presetlari uchun state
  const [selectedPreset, setSelectedPreset] = useState('pomodoro');
  const [showCustomTimer, setShowCustomTimer] = useState(false);
  const [customWork, setCustomWork] = useState('');
  const [customBreak, setCustomBreak] = useState('');

  function showMessage(text, type) {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 4000);
  }

  function handleTemplateToggle(templateId, isEnabled) {
    const newSettings = {
      ...localSettings,
      templates: {
        ...localSettings.templates,
        [templateId]: isEnabled,
      },
    };
    setLocalSettings(newSettings);
    setHasChanges(true);
  }

  // ✅ TUZATILGAN: Preset tanlash (ikkita state ni bir vaqtda yangilaydi)
  function handlePresetChange(presetId) {
    setSelectedPreset(presetId);
    if (presetId === 'custom') {
      setShowCustomTimer(true);
    } else {
      setShowCustomTimer(false);
      const preset = TIMER_PRESETS.find(p => p.id === presetId);
      if (preset) {
        const newSettings = {
          ...localSettings,
          timer: {
            ...localSettings.timer,
            workDuration: preset.work,
            breakDuration: preset.break,
          }
        };
        setLocalSettings(newSettings);
        setHasChanges(true);
      }
    }
  }

  // ✅ TUZATILGAN: Custom vaqtni saqlash
  function handleCustomTimerSave() {
    const work = parseInt(customWork);
    const brk = parseInt(customBreak);
    if (work > 0 && brk > 0) {
      const newSettings = {
        ...localSettings,
        timer: {
          ...localSettings.timer,
          workDuration: work,
          breakDuration: brk,
        }
      };
      setLocalSettings(newSettings);
      setHasChanges(true);
      setShowCustomTimer(false);
    }
  }

  function handleSave() {
    saveSettings(localSettings);
    setSavedSettings(localSettings);
    setHasChanges(false);
    showMessage("Sozlamalar saqlandi!", 'success');
  }

  function handleCancel() {
    setLocalSettings(savedSettings);
    setHasChanges(false);
    showMessage("O'zgarishlar bekor qilindi", 'error');
  }

  function handleResetSettings() {
    if (window.confirm("Barcha sozlamalarni standart holatga qaytarmoqchimisiz?")) {
      const defaultSettings = resetSettings();
      setLocalSettings(defaultSettings);
      setSavedSettings(defaultSettings);
      setHasChanges(false);
      setSelectedPreset('pomodoro');
      setShowCustomTimer(false);
      showMessage("Sozlamalar tiklandi!", 'success');
    }
  }

  async function handleExport() {
    setExporting(true);
    const result = await exportAllData();
    if (result.success) showMessage(`${result.count} ta yozuv eksport qilindi!`, 'success');
    else showMessage(`Xato: ${result.error}`, 'error');
    setExporting(false);
  }

  async function handleImport(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImporting(true);
    const result = await importData(file);
    if (result.success) showMessage(`${result.count} ta yozuv import qilindi!`, 'success');
    else showMessage(`Xato: ${result.error}`, 'error');
    setImporting(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  async function handleClearAll() {
    if (window.confirm("DIQQAT! Barcha ma'lumotlar o'chiriladi!") &&
        window.confirm("Rostdan ham o'chirmoqchimisiz?")) {
      await clearAllData();
      showMessage("Barcha ma'lumotlar o'chirildi!", 'success');
    }
  }

  const [stats, setStats] = useState(null);
  useEffect(() => {
    async function loadStats() {
      const [notes, cats] = await Promise.all([getAllNotes(), getAllCategories()]);
      setStats({ notes: notes.length, categories: cats.length });
    }
    loadStats();
  }, []);

  // Shablonlarni kategoriya bo'yicha guruhlash
  const templatesByCategory = {};
  Object.entries(TEMPLATES_INFO).forEach(([id, info]) => {
    if (!templatesByCategory[info.category]) {
      templatesByCategory[info.category] = [];
    }
    templatesByCategory[info.category].push({ id, ...info });
  });

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {message && (
        <div className={`card flex items-center gap-3 ${
          message.type === 'success' ? 'border-sage bg-sage-bg' : 'border-rose bg-rose-bg'
        }`}>
          {message.type === 'success' ? <CheckCircle size={20} className="text-sage" /> : <XCircle size={20} className="text-rose" />}
          <span className="text-sm font-medium">{message.text}</span>
        </div>
      )}

      {hasChanges && (
        <div className="sticky top-0 z-10 bg-card border border-line rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-gold rounded-full animate-pulse"></div>
              <span className="font-semibold text-sm">O'zgarishlar saqlanmagan</span>
            </div>
            <div className="flex gap-2">
              <button onClick={handleCancel} className="btn-ghost">
                <X size={16} />
                Bekor qilish
              </button>
              <button onClick={handleSave} className="btn-primary">
                <Save size={16} />
                Saqlash
              </button>
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div className="card">
          <div className="flex items-center gap-3 mb-3">
            <Database size={20} className="text-ink-soft" />
            <h3 className="font-serif font-semibold text-lg">Ma'lumotlar bazasi</h3>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-cream rounded-xl p-3 text-center">
              <div className="font-serif font-semibold text-2xl">{stats.notes}</div>
              <div className="text-xs text-ink-soft mt-1">Yozuvlar</div>
            </div>
            <div className="bg-cream rounded-xl p-3 text-center">
              <div className="font-serif font-semibold text-2xl">{stats.categories}</div>
              <div className="text-xs text-ink-soft mt-1">Kategoriyalar</div>
            </div>
          </div>
        </div>
      )}

      {/* TIMER SOZLAMALARI - PRESETLAR BILAN */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <Clock size={20} className="text-sage" />
          <h3 className="font-serif font-semibold text-lg">Pomodoro Timer</h3>
        </div>

        <div className="space-y-4">
          <label className="block text-sm font-semibold text-ink-soft mb-2">
            Tayyor rejimlar (olimlar tavsiyasi):
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {TIMER_PRESETS.map(preset => (
              <button
                key={preset.id}
                onClick={() => handlePresetChange(preset.id)}
                className={`p-3 rounded-xl text-left transition-all border-2 ${
                  selectedPreset === preset.id && !showCustomTimer
                    ? 'border-sage bg-sage-bg'
                    : 'border-line bg-cream hover:border-ink/30'
                }`}
              >
                <div className="font-semibold text-sm">{preset.name}</div>
                <div className="text-xs text-ink-soft mt-1">
                  {preset.work}/{preset.break} daq — {preset.desc}
                </div>
              </button>
            ))}

            <button
              onClick={() => handlePresetChange('custom')}
              className={`p-3 rounded-xl text-left transition-all border-2 ${
                showCustomTimer
                  ? 'border-sage bg-sage-bg'
                  : 'border-line bg-cream hover:border-ink/30'
              }`}
            >
              <div className="font-semibold text-sm">✏️ Boshqa (o'zim kiritaman)</div>
              <div className="text-xs text-ink-soft mt-1">
                {showCustomTimer ? 'Quyida kiriting...' : 'O\'z vaqtingizni belgilang'}
              </div>
            </button>
          </div>

          {showCustomTimer && (
            <div className="p-4 bg-cream rounded-xl space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-ink-soft mb-1">
                    Ish vaqti (daqiqa)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="240"
                    value={customWork}
                    onChange={(e) => setCustomWork(e.target.value)}
                    placeholder="Masalan: 45"
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-ink-soft mb-1">
                    Dam vaqti (daqiqa)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={customBreak}
                    onChange={(e) => setCustomBreak(e.target.value)}
                    placeholder="Masalan: 10"
                    className="input-field"
                  />
                </div>
              </div>
              <button
                onClick={handleCustomTimerSave}
                disabled={!customWork || !customBreak}
                className="btn-primary w-full text-sm"
              >
                <Save size={14} />
                Ushbu vaqtni qo'llash
              </button>
            </div>
          )}

          <div className="p-3 bg-line/30 rounded-xl text-sm">
            <span className="text-ink-soft">Hozirgi sozlama: </span>
            <strong>{localSettings.timer.workDuration} daqiqa ish</strong> /
            <strong> {localSettings.timer.breakDuration} daqiqa dam</strong>
          </div>
        </div>
      </div>

      {/* 30+ SHABLONLAR */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <FileText size={20} className="text-gold" />
          <h3 className="font-serif font-semibold text-lg">Shablonlar ({Object.keys(TEMPLATES_INFO).length} ta)</h3>
        </div>
        <p className="text-sm text-ink-soft mb-4">
          Keraksiz shablonlarni o'chiring. Ular "Shablon tanlash" menyusida ko'rinmaydi.
        </p>

        <div className="space-y-6">
          {Object.entries(templatesByCategory).map(([category, templates]) => (
            <div key={category}>
              <h4 className="font-semibold text-sm text-ink-soft mb-2">
                {category}
              </h4>
              <div className="space-y-2">
                {templates.map(template => (
                  <div key={template.id} className="flex items-center justify-between p-3 bg-cream rounded-xl">
                    <span className="font-medium text-sm">{template.name}</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={localSettings.templates[template.id]}
                        onChange={(e) => handleTemplateToggle(template.id, e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-line rounded-full peer peer-checked:bg-sage peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-cream after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
