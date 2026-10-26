import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, Trash2, Edit2, ChevronDown, ChevronRight, 
  FolderOpen, FileText 
} from 'lucide-react';
import { 
  getAllCategories, addCategory, updateCategory, deleteCategory, 
  getNotesByCategory, getAllNotes, updateNote 
} from '../db/database';

export default function CategoriesPage() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [allNotes, setAllNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState(new Set());
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [selectedParentId, setSelectedParentId] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [cats, notes] = await Promise.all([
        getAllCategories(),
        getAllNotes(),
      ]);
      
      setCategories(cats);
      
      setAllNotes(notes);
    } catch (error) {
      console.error("Ma'lumotlarni yuklashda xato:", error);
    } finally {
      setLoading(false);
    }
  }

  function toggleExpand(id) {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  }

  function buildTree(parentId = null) {
    return categories
      .filter(cat => cat.parentId === parentId)
      .map(cat => ({
        ...cat,
        children: buildTree(cat.id),
        notes: allNotes.filter(n => n.categoryId === cat.id),
      }));
  }

  // ✅ YANGI: AQLLI O'CHIRISH TIZIMI
  async function handleDelete(id, e) {
    e.stopPropagation();

    // 1. Ichidagi yozuvlarni topish
    const notes = await getNotesByCategory(id);

    // 2. Ichidagi sub-kategoriyalarni topish
    const children = categories.filter(c => c.parentId === id);

    // 3. Ogohlantirish xabarini shakllantirish
    let message = `Bu kategoriyani o'chirmoqchimisiz?`;
    if (notes.length > 0) {
      message += `\n\n⚠️ Ichida ${notes.length} ta yozuv bor. Ular "Kategoriyasiz" ga o'tkaziladi.`;
    }
    if (children.length > 0) {
      message += `\n\n️ Ichida ${children.length} ta sub-kategoriya bor. Ular ham o'chiriladi!`;
    }

    if (!window.confirm(message)) return;

    // 4. Yozuvlarni "Kategoriyasiz" qilish (categoryId = null)
    if (notes.length > 0) {
      for (const note of notes) {
        await updateNote(note.id, { categoryId: null });
      }
    }

    // 5. Sub-kategoriyalarni o'chirish
    if (children.length > 0) {
      for (const child of children) {
        await deleteCategory(child.id);
      }
    }

    // 6. Asosiy kategoriyani o'chirish
    await deleteCategory(id);

    // 7. Sahifani qayta yuklash
    await loadData();
  }

  function handleEdit(category, e) {
    e.stopPropagation();
    setEditingCategory(category);
    setShowAddModal(true);
  }

  function handleAddSubCategory(parentId, e) {
    e.stopPropagation();
    setSelectedParentId(parentId);
    setEditingCategory(null);
    setShowAddModal(true);
  }

  function handleNoteClick(noteId, e) {
    e.stopPropagation();
    navigate(`/notes/${noteId}/view`);
  }

  if (loading) {
    return (
      <div className="card text-center py-12">
        <p className="text-ink-soft">Yuklanmoqda...</p>
      </div>
    );
  }

  const tree = buildTree(null);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-soft">
          {categories.length} ta kategoriya
        </p>
        <button
          onClick={() => {
            setSelectedParentId(null);
            setEditingCategory(null);
            setShowAddModal(true);
          }}
          className="btn-primary"
        >
          <Plus size={16} />
          Yangi kategoriya
        </button>
      </div>

      <div className="space-y-2">
        {tree.map((cat) => (
          <CategoryNode
            key={cat.id}
            category={cat}
            level={0}
            expandedIds={expandedIds}
            onToggle={toggleExpand}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onAddSub={handleAddSubCategory}
            onNoteClick={handleNoteClick}
          />
        ))}
      </div>

      {showAddModal && (
        <CategoryModal
          category={editingCategory}
          parentId={selectedParentId}
          categories={categories}
          onClose={() => {
            setShowAddModal(false);
            setEditingCategory(null);
            setSelectedParentId(null);
          }}
          onSave={async (data) => {
            if (editingCategory) {
              await updateCategory(editingCategory.id, data);
            } else {
              await addCategory({
                ...data,
                id: `cat-${Date.now()}`,
              });
            }
            await loadData();
            setShowAddModal(false);
            setEditingCategory(null);
            setSelectedParentId(null);
          }}
        />
      )}
    </div>
  );
}

function CategoryNode({ category, level, expandedIds, onToggle, onEdit, onDelete, onAddSub, onNoteClick }) {
  const isExpanded = expandedIds.has(category.id);
  const hasChildren = category.children.length > 0 || category.notes.length > 0;

  const colorClasses = {
    sage: 'bg-sage-bg text-sage border-sage/30',
    gold: 'bg-gold-bg text-gold border-gold/30',
    lavender: 'bg-lavender-bg text-lavender border-lavender/30',
    rose: 'bg-rose-bg text-rose border-rose/30',
    ink: 'bg-ink/5 text-ink border-ink/10',
  };

  return (
    <div className="relative">
      {level > 0 && (
        <div 
          className="absolute left-0 top-0 bottom-0 w-px bg-line"
          style={{ left: `${level * 24 - 12}px` }}
        />
      )}

      <div
        className={`card cursor-pointer transition-all ${
          isExpanded ? 'border-ink/30 shadow-sm' : 'hover:border-ink/20'
        }`}
        onClick={() => hasChildren && onToggle(category.id)}
        style={{ marginLeft: `${level * 24}px` }}
      >
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            {hasChildren ? (
              isExpanded ? <ChevronDown size={18} className="text-ink-soft" /> : <ChevronRight size={18} className="text-ink-soft" />
            ) : <div className="w-[18px]" />}
          </div>

          <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${colorClasses[category.color] || colorClasses.ink}`}>
            <FolderOpen size={20} />
          </div>

          <div className="flex-1 min-w-0">
            <div className="font-semibold text-base">{category.name}</div>
            <div className="flex items-center gap-3 mt-1 text-xs text-ink-soft">
              {category.children.length > 0 && <span>{category.children.length} ta sub-kategoriya</span>}
              {category.notes.length > 0 && <span>{category.notes.length} ta yozuv</span>}
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={(e) => onAddSub(category.id, e)}
              className="p-2 rounded-lg hover:bg-line/40 text-ink-soft hover:text-ink transition-colors"
              title="Sub-kategoriya qo'shish"
            >
              <Plus size={16} />
            </button>
            <button
              onClick={(e) => onEdit(category, e)}
              className="p-2 rounded-lg hover:bg-line/40 text-ink-soft hover:text-ink transition-colors"
              title="Tahrirlash"
            >
              <Edit2 size={16} />
            </button>
            <button
              onClick={(e) => onDelete(category.id, e)}
              className="p-2 rounded-lg hover:bg-rose-bg text-ink-soft hover:text-rose transition-colors"
              title="O'chirish"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </div>

      {isExpanded && hasChildren && (
        <div className="mt-2 space-y-2 animate-fadeIn">
          {category.children.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              level={level + 1}
              expandedIds={expandedIds}
              onToggle={onToggle}
              onEdit={onEdit}
              onDelete={onDelete}
              onAddSub={onAddSub}
              onNoteClick={onNoteClick}
            />
          ))}

          {category.notes.length > 0 && (
            <div 
              className="space-y-1"
              style={{ marginLeft: `${(level + 1) * 24}px` }}
            >
              <div className="text-xs font-semibold text-ink-soft mb-2 flex items-center gap-2">
                <FileText size={14} />
                Yozuvlar ({category.notes.length})
              </div>
              {category.notes.map((note) => (
                <div
                  key={note.id}
                  onClick={(e) => onNoteClick(note.id, e)}
                  className="card flex items-center gap-3 cursor-pointer hover:border-ink/30 transition-colors"
                >
                  <FileText size={16} className="text-ink-soft flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">{note.title}</div>
                    {note.excerpt && <div className="text-xs text-ink-soft truncate mt-0.5">{note.excerpt}</div>}
                  </div>
                  <ChevronRight size={14} className="text-ink-soft flex-shrink-0" />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CategoryModal({ category, parentId, categories, onClose, onSave }) {
  const [name, setName] = useState(category?.name || '');
  const [color, setColor] = useState(category?.color || 'ink');
  const [selectedParentId, setSelectedParentId] = useState(category?.parentId || parentId || '');

  const colors = ['ink', 'sage', 'gold', 'lavender', 'rose'];
  const parentCategories = categories.filter(c => !c.parentId);

  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;

    onSave({
      name: name.trim(),
      color,
      parentId: selectedParentId || null,
    });
  }

  return (
    <div className="fixed inset-0 bg-ink/30 z-50 flex items-center justify-center p-4">
      <div className="bg-card rounded-2xl max-w-md w-full p-6">
        <h3 className="font-serif font-semibold text-xl mb-4">
          {category ? 'Kategoriyani tahrirlash' : 'Yangi kategoriya'}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-ink-soft mb-2">Nomi</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Masalan: React"
              className="input-field"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-ink-soft mb-2">Ota-kategoriya (ixtiyoriy)</label>
            <select
              value={selectedParentId}
              onChange={(e) => setSelectedParentId(e.target.value)}
              className="input-field"
            >
              <option value="">Yo'q (asosiy kategoriya)</option>
              {parentCategories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-ink-soft mb-2">Rang</label>
            <div className="flex gap-2">
              {colors.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setColor(c)}
                  className={`w-10 h-10 rounded-xl border-2 transition-all ${
                    color === c ? 'border-ink scale-110' : 'border-transparent'
                  }`}
                  style={{
                    backgroundColor: c === 'ink' ? '#4A4032' : 
                                     c === 'sage' ? '#8FA37E' :
                                     c === 'gold' ? '#C9A55A' :
                                     c === 'lavender' ? '#A597C4' :
                                     '#C97F6C',
                  }}
                />
              ))}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Bekor qilish</button>
            <button type="submit" className="btn-primary flex-1" disabled={!name.trim()}>Saqlash</button>
          </div>
        </form>
      </div>
    </div>
  );
}
