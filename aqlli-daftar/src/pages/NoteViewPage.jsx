import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Edit2, Calendar, Tag, FolderOpen } from 'lucide-react';
import { getNoteById, getAllCategories } from '../db/database';
import { NOTE_STATUS_LABEL, NOTE_STATUS_COLOR } from '../utils/constants';
import { formatFullUz, dueLabel } from '../utils/dateHelpers';
import hljs from 'highlight.js';
import DOMPurify from 'dompurify';
import 'highlight.js/styles/atom-one-dark.css';

export default function NoteViewPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const contentRef = useRef(null);
  const [note, setNote] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadNote();
  }, [id]);

  // Kod bloklarini ranglash va Copy tugmasini qo'shish
  useEffect(() => {
    if (contentRef.current && note?.content) {
      try {
        const cleanHTML = DOMPurify.sanitize(note.content, {
          USE_PROFILES: { html: true },
          ADD_TAGS: ['pre', 'code'],
          ADD_ATTR: ['class'],
        });
        
        contentRef.current.innerHTML = cleanHTML;

        const preBlocks = contentRef.current.querySelectorAll('pre');
        
        preBlocks.forEach((pre) => {
          if (pre.parentElement.classList.contains('code-block-wrapper')) {
            return;
          }

          const codeBlock = pre.querySelector('code');
          
          if (codeBlock) {
            try {
              hljs.highlightElement(codeBlock);
            } catch (e) {
              console.warn("Kodni ranglashda xato:", e);
            }
          }

          // Copy tugmasini qo'shish
          const wrapper = document.createElement('div');
          wrapper.className = 'code-block-wrapper';
          
          const header = document.createElement('div');
          header.className = 'code-block-header';
          
          const language = codeBlock?.className?.replace('hljs language-', '') || 'code';
          
          const langLabel = document.createElement('span');
          langLabel.className = 'code-lang-label';
          langLabel.textContent = language;
          
          const copyBtn = document.createElement('button');
          copyBtn.className = 'code-copy-btn';
          copyBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg> 
            Nusxa olish
          `;
          
          copyBtn.addEventListener('click', () => {
            const codeText = pre.textContent;
            navigator.clipboard.writeText(codeText).then(() => {
              copyBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg> 
                Nusxa olindi!
              `;
              copyBtn.classList.add('copied');
              
              setTimeout(() => {
                copyBtn.innerHTML = `
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg> 
                  Nusxa olish
                `;
                copyBtn.classList.remove('copied');
              }, 2000);
            }).catch(err => {
              console.error('Nusxa olishda xato:', err);
            });
          });
          
          header.appendChild(langLabel);
          header.appendChild(copyBtn);
          
          pre.parentNode.insertBefore(wrapper, pre);
          wrapper.appendChild(header);
          wrapper.appendChild(pre);
        });
      } catch (e) {
        console.error("Kontentni ko'rsatishda xato:", e);
      }
    }
  }, [note?.content]);

  async function loadNote() {
    setLoading(true);
    setError(null);
    
    try {
      console.log("Yozuv yuklanmoqda, ID:", id);
      
      const [noteData, catsData] = await Promise.all([
        getNoteById(id),
        getAllCategories(),
      ]);

      console.log("Yuklandi:", noteData);

      if (noteData) {
        setNote(noteData);
        setCategories(catsData || []);
      } else {
        setError("Yozuv topilmadi yoki bu sizning hotirangizga tegishli emas.");
      }
    } catch (error) {
      console.error("Yozuvni yuklashda xato:", error);
      setError("Xatolik yuz berdi: " + error.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="card text-center py-12">
        <p className="text-ink-soft">Yuklanmoqda...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center py-12">
        <p className="text-rose mb-4">{error}</p>
        <button onClick={() => navigate('/notes')} className="btn-primary">
          Yozuvlarga qaytish
        </button>
      </div>
    );
  }

  if (!note) {
    return (
      <div className="card text-center py-12">
        <p className="text-ink-soft">Yozuv topilmadi</p>
        <button onClick={() => navigate('/notes')} className="btn-primary mt-4">
          Yozuvlarga qaytish
        </button>
      </div>
    );
  }

  const category = categories.find(c => c.id === note.categoryId);
  const statusColor = NOTE_STATUS_COLOR[note.status] || 'ink';

  const colorClasses = {
    sage: 'bg-sage-bg text-sage',
    gold: 'bg-gold-bg text-gold',
    lavender: 'bg-lavender-bg text-lavender',
    ink: 'bg-ink/5 text-ink',
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <button onClick={() => navigate(-1)} className="btn-ghost">
          <ArrowLeft size={16} /> Orqaga
        </button>
        <button onClick={() => navigate(`/notes/${id}/edit`)} className="btn-secondary">
          <Edit2 size={16} /> Tahrirlash
        </button>
      </div>

      <div className="mb-6">
        <h1 className="font-serif font-semibold text-4xl leading-tight mb-4">{note.title}</h1>

        <div className="flex items-center gap-3 flex-wrap text-sm">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-semibold ${colorClasses[statusColor]}`}>
            {NOTE_STATUS_LABEL[note.status]}
          </span>
          {category && (
            <span className="inline-flex items-center gap-1.5 text-ink-soft">
              <FolderOpen size={14} /> {category.name}
            </span>
          )}
          <span className="inline-flex items-center gap-1.5 text-ink-soft">
            <Calendar size={14} /> {formatFullUz(note.createdAt)}
          </span>
        </div>

        {note.tags && note.tags.length > 0 && (
          <div className="flex items-center gap-2 mt-3 flex-wrap">
            <Tag size={14} className="text-ink-soft" />
            {note.tags.map((tag) => (
              <span key={tag} className="inline-flex items-center bg-card border border-line rounded-full px-2.5 py-0.5 text-xs font-medium">
                #{tag}
              </span>
            ))}
          </div>
        )}

        {note.nextReviewDate && (
          <div className="mt-3 text-sm text-ink-soft">
            <Calendar size={14} className="inline mr-1" />
            Keyingi takrorlash: <strong>{dueLabel(note.nextReviewDate)}</strong> ({formatFullUz(note.nextReviewDate)})
          </div>
        )}
      </div>

      <div className="card">
        {note.content ? (
          <div 
            ref={contentRef}
            className="prose prose-sm max-w-none note-content"
          />
        ) : (
          <p className="text-ink-soft italic">Bu yozuvda kontent yo'q.</p>
        )}
      </div>

      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="card text-center">
          <div className="text-xs text-ink-soft mb-1">Yaratilgan</div>
          <div className="font-semibold text-sm">{formatFullUz(note.createdAt)}</div>
        </div>
        <div className="card text-center">
          <div className="text-xs text-ink-soft mb-1">Yangilangan</div>
          <div className="font-semibold text-sm">{formatFullUz(note.updatedAt)}</div>
        </div>
        {note.lastReviewedAt && (
          <div className="card text-center">
            <div className="text-xs text-ink-soft mb-1">Oxirgi takror</div>
            <div className="font-semibold text-sm">{formatFullUz(note.lastReviewedAt)}</div>
          </div>
        )}
      </div>
    </div>
  );
}
