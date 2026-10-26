import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, Trash2, Download, Upload, FolderOpen, CheckCircle2,
  CheckCircle, XCircle, FileJson, Database, AlertTriangle
} from 'lucide-react';
import { getAllHotiras, createHotira, deleteHotira, exportHotira, importHotira } from '../utils/hotira';
import { exportAllData, importData } from '../utils/exportImport';

export default function HotiraPage() {
  const navigate = useNavigate();
  const workspaceFileRef = useRef(null);
  const notesFileRef = useRef(null);
  
  const [hotiras, setHotiras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeHotiraId, setActiveHotiraId] = useState(null);
  const [message, setMessage] = useState(null);
  
  const [noteExporting, setNoteExporting] = useState(false);
  const [noteImporting, setNoteImporting] = useState(false);

  useEffect(() => {
    loadHotiras();
    const id = localStorage.getItem('active_hotira_id');
    setActiveHotiraId(id);
  }, []);

  async function loadHotiras() {
    setLoading(true);
    try {
      const data = await getAllHotiras();
      setHotiras(data);
    } catch (error) {
      console.error("Hotiralar yuklanmadi:", error);
    } finally {
      setLoading(false);
    }
  }

  function showMessage(text, type) {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 4000);
  }

  // --- HOTIRA (WORKSPACE) AMALLARI ---
  function handleCreateWorkspace() {
    const name = prompt("Yangi hotira nomini kiriting (Masalan: 'Ish', 'Shaxsiy'):", `Hotira-${Date.now().toString().slice(-4)}`);
    if (name) {
      createHotira(name).then(() => {
        loadHotiras();
        showMessage(`✅ "${name}" muvaffaqiyatli yaratildi!`, 'success');
      }).catch(err => showMessage(`❌ Xato: ${err.message}`, 'error'));
    }
  }

  function handleDeleteWorkspace(id, name) {
    if (window.confirm(`"${name}" hotirasini butunlay o'chirmoqchimisiz? Barcha yozuvlar va kategoriyalar yo'qoladi!`)) {
      deleteHotira(id).then(() => {
        loadHotiras();
        if (activeHotiraId === id) {
          localStorage.removeItem('active_hotira_id');
          setActiveHotiraId(null);
        }
        showMessage("✅ Hotira o'chirildi!", 'success');
      }).catch(err => showMessage(`❌ Xato: ${err.message}`, 'error'));
    }
  }

  function handleExportWorkspace(id) {
    exportHotira(id).then(() => showMessage("✅ Butun hotira muvaffaqiyatli yuklab olindi!", 'success'))
                    .catch(err => showMessage(`❌ Xato: ${err.message}`, 'error'));
  }

  function handleImportWorkspace(e) {
    const file = e.target.files[0];
    if (!file) return;
    if (!window.confirm("Eslatma: Bu butun boshli Hotira fayli (.aqlli). Import qilganda yangi hotira sifatida qo'shiladi. Davom etasizmi?")) return;
    
    importHotira(file).then(() => {
      loadHotiras();
      showMessage("✅ Butun hotira muvaffaqiyatli import qilindi!", 'success');
    }).catch(err => showMessage(`❌ Xato: ${err.message}`, 'error'));
  }

  function handleActivateWorkspace(id) {
    setActiveHotiraId(id);
    localStorage.setItem('active_hotira_id', id);
    window.dispatchEvent(new Event('hotiraChanged'));
    showMessage("✅ Hotira faollashtirildi! Sahifa yangilanmoqda...", 'success');
    setTimeout(() => window.location.reload(), 800);
  }

  // --- YOZUVLAR (NOTES) AMALLARI ---
  async function handleExportNotes() {
    setNoteExporting(true);
    const result = await exportAllData();
    if (result.success) showMessage(`✅ ${result.count} ta yozuv eksport qilindi!`, 'success');
    else showMessage(`❌ Xato: ${result.error}`, 'error');
    setNoteExporting(false);
  }

  async function handleImportNotes(e) {
    const file = e.target.files[0];
    if (!file) return;
    setNoteImporting(true);
    const result = await importData(file);
    if (result.success) showMessage(`✅ ${result.count} ta yozuv import qilindi!`, 'success');
    else showMessage(`❌ Xato: ${result.error}`, 'error');
    setNoteImporting(false);
    if (notesFileRef.current) notesFileRef.current.value = '';
  }

  if (loading) return <div className="card text-center py-12"><p className="text-ink-soft">Yuklanmoqda...</p></div>;

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {message && (
        <div className={`card flex items-center gap-3 ${message.type === 'success' ? 'border-sage bg-sage-bg' : 'border-rose bg-rose-bg'}`}>
          {message.type === 'success' ? <CheckCircle size={20} className="text-sage" /> : <XCircle size={20} className="text-rose" />}
          <span className="text-sm font-medium">{message.text}</span>
        </div>
      )}

      {/* 1-BO'LIM: HOTIRALAR RO'YXATI */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif font-bold text-xl flex items-center gap-2">
            <FolderOpen className="text-sage" /> Mening Hotiralarim
          </h2>
          <button onClick={handleCreateWorkspace} className="btn-primary flex items-center gap-2">
            <Plus size={16} /> Yangi hotira
          </button>
        </div>

        {hotiras.length === 0 ? (
          <div className="card text-center py-12 border-dashed">
            <p className="text-ink-soft mb-4">Hozircha hech qanday hotira yaratilmagan.</p>
            <button onClick={handleCreateWorkspace} className="btn-primary">Birinchi hotirani yaratish</button>
          </div>
        ) : (
          <div className="space-y-3">
            {hotiras.map(hotira => {
              const isActive = activeHotiraId === hotira.id;
              return (
                <div key={hotira.id} className={`card flex items-center justify-between p-4 transition-all ${isActive ? 'border-2 border-sage bg-sage-bg/30' : 'hover:border-ink/20'}`}>
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isActive ? 'bg-sage text-cream' : 'bg-ink/10 text-ink'}`}>
                      {isActive ? <CheckCircle2 size={24} /> : <FolderOpen size={24} />}
                    </div>
                    <div>
                      <h3 className="font-serif font-semibold text-lg">{hotira.name}</h3>
                      <p className="text-xs text-ink-soft">
                        Yaratilgan: {hotira.createdAt ? new Date(hotira.createdAt).toLocaleDateString('uz-UZ') : 'Noma\'lum'}
                      </p>
                      {isActive && <span className="text-xs font-bold text-sage mt-1 block">🟢 Hozir shu hotirada ishlamoqdasiz</span>}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {!isActive && (
                      <button onClick={() => handleActivateWorkspace(hotira.id)} className="btn-secondary text-sm" title="Shu hotiraga o'tish">
                        Tanlash
                      </button>
                    )}
                    <button onClick={() => handleExportWorkspace(hotira.id)} className="p-2.5 rounded-xl hover:bg-line/30 text-ink-soft" title="Butun hotirani yuklab olish">
                      <Download size={18} />
                    </button>
                    <button onClick={() => handleDeleteWorkspace(hotira.id, hotira.name)} className="p-2.5 rounded-xl hover:bg-rose-bg text-rose" title="Hotirani butunlay o'chirish">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2-BO'LIM: BUTUN HOTIRANI KO'CHIRISH (.aqlli) */}
      <div className="card border-gold/30 bg-gold-bg/20">
        <div className="flex items-center gap-3 mb-4">
          <Database size={24} className="text-gold" />
          <h2 className="font-serif font-bold text-xl">🌍 Butun Hotirani Ko'chirish</h2>
        </div>
        <p className="text-sm text-ink-soft mb-6">
          Barcha yozuvlar, kategoriyalar va sozlamalarni <strong>bitta fayl (.aqlli)</strong> sifatida saqlaydi yoki tiklaydi. 
          Telefon va kompyuter o'rtasida to'liq almashish uchun ayni muddao.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button onClick={() => activeHotiraId && handleExportWorkspace(activeHotiraId)} disabled={!activeHotiraId} className="card flex flex-col items-center justify-center p-6 hover:border-gold transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            <Download size={32} className="text-gold mb-3" />
            <span className="font-semibold">Hotirani Yuklab Olish</span>
            <span className="text-xs text-ink-soft text-center mt-1">Hozirgi faol hotirani .aqlli fayl qiladi</span>
          </button>

          <button onClick={() => workspaceFileRef.current.click()} className="card flex flex-col items-center justify-center p-6 hover:border-gold transition-colors cursor-pointer">
            <Upload size={32} className="text-gold mb-3" />
            <span className="font-semibold">Hotirani Tiklash (Import)</span>
            <span className="text-xs text-ink-soft text-center mt-1">Oldin saqlangan .aqlli faylni yuklaydi</span>
          </button>
        </div>
        <input type="file" accept=".aqlli,.json" onChange={handleImportWorkspace} ref={workspaceFileRef} className="hidden" id="workspace-import-file" />
      </div>

      {/* 3-BO'LIM: FAQAT YOZUVLARNI KO'CHIRISH (.json) */}
      <div className="card border-sage/30 bg-sage-bg/20">
        <div className="flex items-center gap-3 mb-4">
          <FileJson size={24} className="text-sage" />
          <h2 className="font-serif font-bold text-xl">📝 Faqat Yozuvlarni Ko'chirish</h2>
        </div>
        <p className="text-sm text-ink-soft mb-6">
          Faqat yozuvlar va kategoriyalar ro'yxatini <strong>.json</strong> formatida saqlaydi yoki tiklaydi. 
          Sozlamalar va timer vaqtlari bu faylga kirmaydi.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button onClick={handleExportNotes} disabled={noteExporting} className="card flex flex-col items-center justify-center p-6 hover:border-sage transition-colors disabled:opacity-50">
            <Download size={32} className="text-sage mb-3" />
            <span className="font-semibold">{noteExporting ? 'Saqlanmoqda...' : 'Yozuvlarni Yuklab Olish'}</span>
            <span className="text-xs text-ink-soft text-center mt-1">Faqat yozuvlar va kategoriyalar (.json)</span>
          </button>

          <button onClick={() => notesFileRef.current.click()} disabled={noteImporting} className="card flex flex-col items-center justify-center p-6 hover:border-sage transition-colors cursor-pointer disabled:opacity-50">
            <Upload size={32} className="text-sage mb-3" />
            <span className="font-semibold">{noteImporting ? 'Yuklanmoqda...' : 'Yozuvlarni Tiklash (Import)'}</span>
            <span className="text-xs text-ink-soft text-center mt-1">Eski .json faylni bazaga qo'shadi</span>
          </button>
        </div>
        <input type="file" accept=".json" onChange={handleImportNotes} ref={notesFileRef} className="hidden" id="notes-import-file" />
      </div>

      {/* 4-BO'LIM: YO'RIQNOMA */}
      <div className="p-4 bg-cream rounded-xl border border-line">
        <h3 className="font-semibold text-sm mb-2 flex items-center gap-2"><AlertTriangle size={16} className="text-gold" /> Qaysi birini tanlash kerak?</h3>
        <ul className="text-xs text-ink-soft space-y-2 list-disc ml-4">
          <li><strong>🌍 Butun Hotira (.aqlli):</strong> Dasturning to'liq holatini (xuddi o'yin saqlash fayli kabi) ko'chiradi. Boshqa qurilmaga to'liq ko'chib o'tish uchun shuni ishlating.</li>
          <li><strong>📝 Faqat Yozuvlar (.json):</strong> Faqat matnlaringizni zaxira qilish yoki boshqa dasturlar bilan ulashish uchun qulay. Sozlamalarni o'z ichiga olmaydi.</li>
        </ul>
      </div>
    </div>
  );
}
