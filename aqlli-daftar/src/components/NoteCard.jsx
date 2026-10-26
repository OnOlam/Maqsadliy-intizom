import { Link } from 'react-router-dom';
import { Calendar, Tag, FolderOpen, Edit2, Trash2 } from 'lucide-react';
import { formatUz } from '../utils/dateHelpers';
import { NOTE_STATUS_LABEL, NOTE_STATUS_COLOR } from '../utils/constants';

export default function NoteCard({ note, onDelete }) {
  const statusColor = NOTE_STATUS_COLOR[note.status] || 'ink';

  const colorClasses = {
    sage: 'bg-sage-bg text-sage border-sage/30',
    gold: 'bg-gold-bg text-gold border-gold/30',
    lavender: 'bg-lavender-bg text-lavender border-lavender/30',
    rose: 'bg-rose-bg text-rose border-rose/30',
    ink: 'bg-ink/5 text-ink border-ink/10',
  };

  return (
    <div className="card hover:border-ink/30 transition-all group">
      {/* Asosiy qism: Bosilganda KO'RISH sahifasiga o'tadi */}
      <Link to={`/notes/${note.id}/view`} className="block">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-serif font-semibold text-lg text-ink group-hover:text-sage transition-colors line-clamp-2">
            {note.title}
          </h3>
          <span className={`text-xs px-2 py-1 rounded-full font-semibold whitespace-nowrap ${colorClasses[statusColor]}`}>
            {NOTE_STATUS_LABEL[note.status]}
          </span>
        </div>

        {note.excerpt && (
          <p className="text-sm text-ink-soft line-clamp-2 mb-3">
            {note.excerpt}
          </p>
        )}

        <div className="flex items-center gap-3 text-xs text-ink-soft flex-wrap">
          {note.categoryId && (
            <span className="flex items-center gap-1">
              <FolderOpen size={12} />
              {note.categoryId}
            </span>
          )}
          
          {note.nextReviewDate && (
            <span className="flex items-center gap-1">
              <Calendar size={12} />
              {formatUz(note.nextReviewDate)}
            </span>
          )}

          {note.tags && note.tags.length > 0 && (
            <span className="flex items-center gap-1">
              <Tag size={12} />
              {note.tags.slice(0, 2).join(', ')}
              {note.tags.length > 2 && '...'}
            </span>
          )}
        </div>
      </Link>

      {/* Pastki qism: Tahrirlash va O'chirish tugmalari */}
      <div className="flex items-center justify-end gap-2 mt-4 pt-3 border-t border-line">
        <Link 
          to={`/notes/${note.id}/edit`} 
          className="p-2 rounded-lg hover:bg-line/40 text-ink-soft hover:text-ink transition-colors"
          title="Tahrirlash"
        >
          <Edit2 size={16} />
        </Link>
        
        <button 
          onClick={() => onDelete(note.id)} 
          className="p-2 rounded-lg hover:bg-rose-bg text-ink-soft hover:text-rose transition-colors"
          title="O'chirish"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
}
