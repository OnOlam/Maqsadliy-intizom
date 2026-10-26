import { TEMPLATE_CONTENTS } from '../utils/templateContents';
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Save, ArrowLeft, Calendar, Tag, FileText } from 'lucide-react';
import { getNoteById, addNote, updateNote, getAllCategories } from '../db/database';
import { NOTE_STATUS, NOTE_STATUS_LABEL } from '../utils/constants';
import { todayStr, addDays, REVIEW_INTERVALS } from '../utils/dateHelpers';
import RichTextEditor from '../components/RichTextEditor';
import { getSettings, TEMPLATES_INFO } from '../utils/settings';

export default function NoteEditorPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = Boolean(id);

  const [loading, setLoading] = useState(isEditing);
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState([]);

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState(NOTE_STATUS.LEARNING);
  const [categoryId, setCategoryId] = useState('');
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [reviewMode, setReviewMode] = useState('auto');
  const [manualDate, setManualDate] = useState(todayStr());
  const [showTemplates, setShowTemplates] = useState(false);

  // Faqat yoqilgan shablonlarni olish
  const settings = getSettings();
  const enabledTemplates = Object.entries(settings.templates)
    .filter(([id, enabled]) => enabled)
    .map(([id]) => ({ id, ...TEMPLATES_INFO[id] }))
    .filter(t => t.name);

  useEffect(() => {
    async function loadCategories() {
      try {
        const cats = await getAllCategories();
        setCategories(cats);
        if (cats.length > 0 && !categoryId) {
          setCategoryId(cats[0].id);
        }
      } catch (error) {
        console.error("Kategoriyalarni yuklashda xato:", error);
      }
    }
    loadCategories();
  }, []);

  useEffect(() => {
    if (isEditing) {
      loadNote();
    }
  }, [id]);

  async function loadNote() {
    try {
      const note = await getNoteById(id);
      if (note) {
        setTitle(note.title || '');
        setContent(note.content || '');
        setStatus(note.status || NOTE_STATUS.LEARNING);
        setCategoryId(note.categoryId || '');
        setTags(note.tags || []);
        if (note.reviewMode) setReviewMode(note.reviewMode);
        if (note.nextReviewDate) setManualDate(note.nextReviewDate);
      } else {
        alert("Yozuv topilmadi yoki bu sizning hotirangizga tegishli emas!");
        navigate('/notes');
      }
    } catch (error) {
      console.error("Yozuvni yuklashda xato:", error);
      alert("Xatolik: " + error.message);
      navigate('/notes');
    } finally {
      setLoading(false);
    }
  }

  function handleAddTag() {
    const tag = tagInput.trim();
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag]);
      setTagInput('');
    }
  }

  function handleRemoveTag(tag) {
    setTags(tags.filter(t => t !== tag));
  }

  function handleSelectTemplate(templateId) {
    const templateContent = TEMPLATE_CONTENTS[templateId];
    if (templateContent) {
      setContent(templateContent);
      setShowTemplates(false);
    }
  }

  async function handleSave() {
    if (!title.trim()) {
      alert("Sarlavha kiritish shart!");
      return;
    }

    setSaving(true);

    try {
      let nextReviewDate = null;
      let reviewStage = 0;

      if (reviewMode === 'auto') {
        nextReviewDate = addDays(todayStr(), REVIEW_INTERVALS[0]);
      } else if (reviewMode === 'manual') {
        nextReviewDate = manualDate;
      }

      const excerpt = content.replace(/<[^>]*>/g, '').slice(0, 150);

      const noteData = {
        title: title.trim(),
        content,
        excerpt,
        status,
        categoryId,
        tags,
        reviewMode,
        reviewStage,
        nextReviewDate,
      };

      if (isEditing) {
        await updateNote(id, noteData);
        navigate(`/notes/${id}/view`);
      } else {
        const newId = await addNote(noteData);
        navigate(`/notes/${newId}/view`);
      }
    } catch (error) {
      console.error("Saqlashda xato:", error);
      alert("Xatolik yuz berdi: " + error.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="card text-center py-12">
        <p className="text-ink-soft">Yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="btn-ghost">
          <ArrowLeft size={16} />
          Orqaga
        </button>

        <button onClick={handleSave} disabled={saving || !title.trim()} className="btn-primary">
          <Save size={16} />
          {saving ? 'Saqlanmoqda...' : 'Saqlash'}
        </button>
      </div>

      <div>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Yozuv sarlavhasi..."
          className="w-full bg-transparent text-3xl font-serif font-semibold placeholder:text-ink-soft/50 focus:outline-none"
          autoFocus
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-ink-soft mb-2">Holat</label>
          <div className="flex gap-2">
            {Object.entries(NOTE_STATUS).map(([key, value]) => (
              <button
                key={value}
                onClick={() => setStatus(value)}
                className={`flex-1 px-3 py-2 rounded-xl text-sm font-semibold transition-colors ${
                  status === value ? 'bg-ink text-cream' : 'bg-card border border-line text-ink-soft hover:bg-line/30'
                }`}
              >
                {NOTE_STATUS_LABEL[value]}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-ink-soft mb-2">Kategoriya</label>
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} className="input-field">
            <option value="">Kategoriyasiz</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-ink-soft mb-2">
          <Tag size={14} className="inline mr-1" />
          Teglar
        </label>
        <div className="flex gap-2 flex-wrap mb-2">
          {tags.map((tag) => (
            <span key={tag} className="inline-flex items-center gap-1 bg-card border border-line rounded-full px-3 py-1 text-sm">
              #{tag}
              <button onClick={() => handleRemoveTag(tag)} className="text-ink-soft hover:text-rose">×</button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddTag(); } }}
            placeholder="Teg qo'shish (Enter bosing)..."
            className="input-field flex-1"
          />
          <button onClick={handleAddTag} className="btn-secondary">Qo'shish</button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-ink-soft mb-2">
          <Calendar size={14} className="inline mr-1" />
          Takrorlash
        </label>
        <div className="flex gap-2 mb-3">
          <button onClick={() => setReviewMode('auto')} className={`flex-1 px-3 py-2 rounded-xl text-sm font-semibold transition-colors ${reviewMode === 'auto' ? 'bg-ink text-cream' : 'bg-card border border-line text-ink-soft hover:bg-line/30'}`}>
            Avtomatik
          </button>
          <button onClick={() => setReviewMode('manual')} className={`flex-1 px-3 py-2 rounded-xl text-sm font-semibold transition-colors ${reviewMode === 'manual' ? 'bg-ink text-cream' : 'bg-card border border-line text-ink-soft hover:bg-line/30'}`}>
            Qo'lda sana
          </button>
          <button onClick={() => setReviewMode('none')} className={`flex-1 px-3 py-2 rounded-xl text-sm font-semibold transition-colors ${reviewMode === 'none' ? 'bg-ink text-cream' : 'bg-card border border-line text-ink-soft hover:bg-line/30'}`}>
            Kerak emas
          </button>
        </div>

        {reviewMode === 'manual' && (
          <input type="date" value={manualDate} onChange={(e) => setManualDate(e.target.value)} className="input-field" />
        )}

        {reviewMode === 'auto' && (
          <p className="text-xs text-ink-soft mt-2">
            Birinchi takrorlash: {addDays(todayStr(), REVIEW_INTERVALS[0])}
          </p>
        )}
      </div>

      <div className="mb-4">
        <button onClick={() => setShowTemplates(!showTemplates)} className="btn-secondary w-full">
          <FileText size={16} />
          {showTemplates ? 'Shablonlarni yopish' : 'Shablon tanlash'}
        </button>
        
        {showTemplates && (
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2">
            {enabledTemplates.map(template => (
              <button
                key={template.id}
                onClick={() => handleSelectTemplate(template.id)}
                className="card text-left hover:border-ink/30 transition-colors"
              >
                <div className="font-semibold text-sm">{template.name}</div>
                <div className="text-xs text-ink-soft mt-1">{template.category}</div>
              </button>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-semibold text-ink-soft mb-2">Ma'lumot</label>
        <RichTextEditor content={content} onChange={setContent} />
      </div>
    </div>
  );
}
