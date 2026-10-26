import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Check, X, RotateCcw, Sparkles, Calendar } from 'lucide-react';
import { getAllNotes, updateNote } from '../db/database';
import { todayStr, addDays, REVIEW_INTERVALS, formatUz, dueLabel } from '../utils/dateHelpers';

export default function ReviewPage() {
  const navigate = useNavigate();
  const [dueNotes, setDueNotes] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDueNotes();
  }, []);

  async function loadDueNotes() {
    try {
      const allNotes = await getAllNotes();
      const today = todayStr();
      
      // Faqat takrorlash sanasi kelgan yoki o'tib ketgan yozuvlarni olamiz
      const due = allNotes.filter(n => 
        n.nextReviewDate && n.nextReviewDate <= today && !n.mastered
      );
      
      setDueNotes(due);
    } catch (error) {
      console.error("Takrorlash yozuvlarini yuklashda xato:", error);
    } finally {
      setLoading(false);
    }
  }

  function handleRating(rating) {
    const note = dueNotes[currentIndex];
    if (!note) return;

    let nextStage = note.reviewStage || 0;
    let nextReviewDate = null;
    let mastered = false;

    if (rating === 'forgot') {
      nextStage = 0;
      nextReviewDate = addDays(todayStr(), REVIEW_INTERVALS[0]);
    } else if (rating === 'hard') {
      nextStage = Math.max(0, nextStage - 1);
      nextReviewDate = addDays(todayStr(), REVIEW_INTERVALS[nextStage]);
    } else if (rating === 'good') {
      nextStage = nextStage + 1;
      if (nextStage >= REVIEW_INTERVALS.length) {
        mastered = true;
      } else {
        nextReviewDate = addDays(todayStr(), REVIEW_INTERVALS[nextStage]);
      }
    } else if (rating === 'easy') {
      nextStage = Math.min(nextStage + 2, REVIEW_INTERVALS.length - 1);
      if (nextStage >= REVIEW_INTERVALS.length - 1) {
        mastered = true;
      } else {
        nextReviewDate = addDays(todayStr(), REVIEW_INTERVALS[nextStage]);
      }
    }

    updateNote(note.id, {
      reviewStage: nextStage,
      nextReviewDate,
      mastered,
      lastReviewedAt: todayStr(),
    });

    setShowAnswer(false);
    if (currentIndex < dueNotes.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setDueNotes([]);
    }
  }

  if (loading) {
    return (
      <div className="card text-center py-12">
        <p className="text-ink-soft">Yuklanmoqda...</p>
      </div>
    );
  }

  if (dueNotes.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="w-16 h-16 bg-sage-bg rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Sparkles size={28} className="text-sage" />
        </div>
        <h3 className="font-serif font-semibold text-lg mb-2">
          Zo'r! Hammasi takrorlangan 🎉
        </h3>
        <p className="text-sm text-ink-soft mb-4">
          Hozircha takrorlash kerak bo'lgan yozuvlar yo'q.
        </p>
        <button onClick={() => navigate('/notes')} className="btn-primary">
          Yozuvlarga qaytish
        </button>
      </div>
    );
  }

  const currentNote = dueNotes[currentIndex];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Progress */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-ink-soft">
            {currentIndex + 1} / {dueNotes.length}
          </span>
          <span className="text-sm text-ink-soft">
            Qolgan: {dueNotes.length - currentIndex - 1}
          </span>
        </div>
        <div className="w-full bg-line rounded-full h-2">
          <div
            className="bg-sage h-2 rounded-full transition-all"
            style={{ width: `${((currentIndex + 1) / dueNotes.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Flashcard */}
      <div className="card min-h-[400px] flex flex-col">
        <div className="mb-4">
          <div className="text-xs text-ink-soft mb-1">Savol:</div>
          <h2 className="font-serif font-semibold text-2xl">
            {currentNote.title}
          </h2>
          {currentNote.nextReviewDate && (
            <div className="flex items-center gap-1 text-xs text-ink-soft mt-2">
              <Calendar size={12} />
              Rejalashtirilgan: {dueLabel(currentNote.nextReviewDate)}
            </div>
          )}
        </div>

        <div className="flex-1 flex items-center justify-center">
          {showAnswer ? (
            <div className="w-full overflow-y-auto max-h-[300px]">
              <div className="text-xs text-ink-soft mb-2">Javob:</div>
              <div 
                className="prose prose-sm max-w-none note-content"
                dangerouslySetInnerHTML={{ __html: currentNote.content || 'Javob yo\'q' }}
              />
            </div>
          ) : (
            <button
              onClick={() => setShowAnswer(true)}
              className="btn-primary text-lg px-8 py-4"
            >
              <Brain size={20} />
              Javobni ko'rsatish
            </button>
          )}
        </div>

        {showAnswer && (
          <div className="mt-6 pt-6 border-t border-line">
            <div className="text-sm font-semibold text-ink-soft mb-3 text-center">
              Qanchalik eslab qoldingiz?
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <button onClick={() => handleRating('forgot')} className="btn-secondary border-rose/30 text-rose hover:bg-rose-bg">
                <X size={16} /> Unutdim
              </button>
              <button onClick={() => handleRating('hard')} className="btn-secondary border-gold/30 text-gold hover:bg-gold-bg">
                <RotateCcw size={16} /> Qiynaldim
              </button>
              <button onClick={() => handleRating('good')} className="btn-secondary border-sage/30 text-sage hover:bg-sage-bg">
                <Check size={16} /> Yaxshi
              </button>
              <button onClick={() => handleRating('easy')} className="btn-primary bg-sage">
                <Sparkles size={16} /> Oson
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
