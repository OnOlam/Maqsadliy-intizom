import { useState, useEffect } from 'react';
import { Search, Filter, Calendar, X } from 'lucide-react';
import NoteCard from '../components/NoteCard';
import { getAllNotes, deleteNote, getAllCategories } from '../db/database';
import { NOTE_STATUS, NOTE_STATUS_LABEL } from '../utils/constants';

export default function NotesPage() {
  const [notes, setNotes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Qidiruv va filtrlar
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [notesData, catsData] = await Promise.all([
        getAllNotes(),
        getAllCategories(),
      ]);
      setNotes(notesData);
      setCategories(catsData);
    } catch (error) {
      console.error("Ma'lumotlarni yuklashda xato:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (window.confirm("Bu yozuvni o'chirishni xohlaysizmi?")) {
      await deleteNote(id);
      setNotes(notes.filter(n => n.id !== id));
    }
  }

  // Kuchli qidiruv funksiyasi
  function searchInContent(content, query) {
    if (!content) return false;
    // HTML teglarni olib tashlash
    const plainText = content.replace(/<[^>]*>/g, ' ').toLowerCase();
    return plainText.includes(query.toLowerCase());
  }

  // Filtrlash
  const filteredNotes = notes.filter((note) => {
    // Qidiruv (sarlavha, kontent, teglar)
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesTitle = note.title.toLowerCase().includes(query);
      const matchesContent = searchInContent(note.content, query);
      const matchesTags = note.tags && note.tags.some(tag => tag.toLowerCase().includes(query));
      
      if (!matchesTitle && !matchesContent && !matchesTags) {
        return false;
      }
    }

    // Holat bo'yicha filtr
    if (filterStatus !== 'all' && note.status !== filterStatus) {
      return false;
    }

    // Kategoriya bo'yicha filtr
    if (filterCategory !== 'all' && note.categoryId !== filterCategory) {
      return false;
    }

    // Sana bo'yicha filtr (dan)
    if (filterDateFrom && note.createdAt) {
      const noteDate = note.createdAt.split('T')[0];
      if (noteDate < filterDateFrom) {
        return false;
      }
    }

    // Sana bo'yicha filtr (gacha)
    if (filterDateTo && note.createdAt) {
      const noteDate = note.createdAt.split('T')[0];
      if (noteDate > filterDateTo) {
        return false;
      }
    }

    return true;
  });

  // Filtrlarni tozalash
  function clearFilters() {
    setSearchQuery('');
    setFilterStatus('all');
    setFilterCategory('all');
    setFilterDateFrom('');
    setFilterDateTo('');
  }

  // Faol filtrlar soni
  const activeFiltersCount = [
    filterStatus !== 'all',
    filterCategory !== 'all',
    filterDateFrom !== '',
    filterDateTo !== '',
  ].filter(Boolean).length;

  if (loading) {
    return (
      <div className="card text-center py-12">
        <p className="text-ink-soft">Yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Qidiruv va filtrlar */}
      <div className="space-y-3">
        {/* Qidiruv */}
        <div className="relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-soft" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Qidirish (sarlavha, kontent, teglar)..."
            className="input-field pl-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-soft hover:text-ink"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Filtrlar tugmasi */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex-1"
          >
            <Filter size={16} />
            Filtrlar
            {activeFiltersCount > 0 && (
              <span className="ml-2 px-2 py-0.5 rounded-full bg-ink text-cream text-xs">
                {activeFiltersCount}
              </span>
            )}
          </button>
          
          {activeFiltersCount > 0 && (
            <button
              onClick={clearFilters}
              className="btn-ghost"
            >
              Tozalash
            </button>
          )}
        </div>

        {/* Kengaytirilgan filtrlar */}
        {showFilters && (
          <div className="card space-y-3 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Holat */}
              <div>
                <label className="block text-sm font-semibold text-ink-soft mb-2">
                  Holat
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="input-field"
                >
                  <option value="all">Barcha holatlar</option>
                  {Object.entries(NOTE_STATUS).map(([key, value]) => (
                    <option key={value} value={value}>
                      {NOTE_STATUS_LABEL[value]}
                    </option>
                  ))}
                </select>
              </div>

              {/* Kategoriya */}
              <div>
                <label className="block text-sm font-semibold text-ink-soft mb-2">
                  Kategoriya
                </label>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="input-field"
                >
                  <option value="all">Barcha kategoriyalar</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sana (dan) */}
              <div>
                <label className="block text-sm font-semibold text-ink-soft mb-2">
                  <Calendar size={14} className="inline mr-1" />
                  Sanadan
                </label>
                <input
                  type="date"
                  value={filterDateFrom}
                  onChange={(e) => setFilterDateFrom(e.target.value)}
                  className="input-field"
                />
              </div>

              {/* Sana (gacha) */}
              <div>
                <label className="block text-sm font-semibold text-ink-soft mb-2">
                  <Calendar size={14} className="inline mr-1" />
                  Sanagacha
                </label>
                <input
                  type="date"
                  value={filterDateTo}
                  onChange={(e) => setFilterDateTo(e.target.value)}
                  className="input-field"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Natijalar soni */}
      <div className="flex items-center justify-between text-sm text-ink-soft">
        <span>
          {filteredNotes.length} ta yozuv topildi
          {searchQuery && ` "${searchQuery}" bo'yicha`}
        </span>
        {notes.length > 0 && (
          <span>
            Jami: {notes.length} ta
          </span>
        )}
      </div>

      {/* Yozuvlar ro'yxati */}
      {filteredNotes.length === 0 ? (
        <div className="card text-center py-12">
          {notes.length === 0 ? (
            <>
              <p className="text-ink-soft mb-4">Hozircha yozuvlar yo'q</p>
              <a href="/notes/new" className="btn-primary inline-flex">
                Birinchi yozuvni qo'shish
              </a>
            </>
          ) : (
            <>
              <p className="text-ink-soft mb-4">Filtrlar bo'yicha yozuvlar topilmadi</p>
              <button
                onClick={clearFilters}
                className="btn-secondary"
              >
                Filtrlarni tozalash
              </button>
            </>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredNotes.map((note) => (
            <NoteCard
              key={note.id}
              note={{
                ...note,
                categoryId: categories.find(c => c.id === note.categoryId)?.name || null,
              }}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
