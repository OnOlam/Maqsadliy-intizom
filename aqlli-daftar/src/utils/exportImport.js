import db, { getAllNotes, getAllCategories } from '../db/database';
import DOMPurify from 'dompurify';

/**
 * Faqat JORIY FAOL hotiradagi yozuv va kategoriyalarni .json sifatida eksport qilish
 */
export async function exportAllData() {
  try {
    const activeHotiraId = localStorage.getItem('active_hotira_id');
    if (!activeHotiraId) {
      return { success: false, error: "Avval 'Hotira' bo'limidan hotira tanlang yoki yarating!" };
    }

    // getAllNotes va getAllCategories allaqachon faqat joriy hotirani qaytaradi
    const notes = await getAllNotes();
    const categories = await getAllCategories();

    const data = {
      version: '1.0',
      type: 'notes-only',
      exportDate: new Date().toISOString(),
      notes,
      categories,
    };

    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const date = new Date().toISOString().slice(0, 10);
    const filename = `aqlli-daftar-yozuvlar-${date}.json`;

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return { success: true, count: notes.length };
  } catch (error) {
    console.error("Eksport xatosi:", error);
    return { success: false, error: error.message };
  }
}

/**
 * .json fayldan yozuvlarni JORIY FAOL hotiraga import qilish (XSS himoyasi bilan)
 */
export async function importData(file) {
  try {
    const activeHotiraId = localStorage.getItem('active_hotira_id');
    if (!activeHotiraId) {
      return { success: false, error: "Avval 'Hotira' bo'limidan hotira tanlang yoki yarating!" };
    }

    const text = await file.text();
    const data = JSON.parse(text);

    if (!data.notes || !Array.isArray(data.notes)) {
      return { success: false, error: "Noto'g'ri fayl formati!" };
    }

    // 1. Kategoriyalarni import qilish + eski id -> yangi id xaritasi
    const categoryIdMap = {};

    if (data.categories && Array.isArray(data.categories)) {
      for (const cat of data.categories) {
        const newId = `cat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        categoryIdMap[cat.id] = newId;
        await db.categories.add({
          id: newId,
          name: DOMPurify.sanitize(cat.name || ''),
          color: cat.color || 'ink',
          parentId: null, // vaqtincha, pastda to'g'irlaymiz
          hotiraId: activeHotiraId,
        });
      }
      // Ota-bola bog'lanishini to'g'irlash
      for (const cat of data.categories) {
        if (cat.parentId && categoryIdMap[cat.parentId]) {
          await db.categories.update(categoryIdMap[cat.id], {
            parentId: categoryIdMap[cat.parentId],
          });
        }
      }
    }

    // 2. Yozuvlarni import qilish (yangi id + joriy hotiraId + to'g'ri categoryId)
    let importedCount = 0;
    for (const note of data.notes) {
      const newId = `note-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      await db.notes.add({
        id: newId,
        title: DOMPurify.sanitize(note.title || ''),
        content: DOMPurify.sanitize(note.content || '', {
          USE_PROFILES: { html: true },
          ADD_TAGS: ['pre', 'code'],
          ADD_ATTR: ['class'],
        }),
        excerpt: DOMPurify.sanitize(note.excerpt || ''),
        status: note.status || 'learning',
        categoryId: note.categoryId ? (categoryIdMap[note.categoryId] || null) : null,
        tags: Array.isArray(note.tags) ? note.tags : [],
        reviewMode: note.reviewMode || 'none',
        reviewStage: note.reviewStage || 0,
        nextReviewDate: note.nextReviewDate || null,
        lastReviewedAt: note.lastReviewedAt || null,
        hotiraId: activeHotiraId,
        createdAt: note.createdAt || new Date().toISOString(),
        updatedAt: note.updatedAt || new Date().toISOString(),
      });
      importedCount++;
    }

    return { success: true, count: importedCount };
  } catch (error) {
    console.error("Import xatosi:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Bitta yozuvni Markdown formatida eksport qilish
 */
export function exportNoteAsMarkdown(note) {
  let md = '';

  md += `# ${note.title}\n\n`;
  md += `**Holat:** ${note.status}\n`;
  if (note.categoryId) md += `**Kategoriya:** ${note.categoryId}\n`;
  if (note.tags && note.tags.length > 0) {
    md += `**Teglar:** ${note.tags.map(t => `#${t}`).join(', ')}\n`;
  }
  md += `**Sana:** ${note.createdAt ? note.createdAt.slice(0, 10) : 'Noma\'lum'}\n`;
  md += `\n---\n\n`;

  if (note.content) {
    let content = note.content;
    content = content.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
    content = content.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
    content = content.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
    content = content.replace(/<strong>(.*?)<\/strong>/gi, '**$1**');
    content = content.replace(/<b>(.*?)<\/b>/gi, '**$1**');
    content = content.replace(/<em>(.*?)<\/em>/gi, '*$1*');
    content = content.replace(/<i>(.*?)<\/i>/gi, '*$1*');
    content = content.replace(/<code>(.*?)<\/code>/gi, '`$1`');
    content = content.replace(/<pre><code>(.*?)<\/code><\/pre>/gi, '```\n$1\n```\n');
    content = content.replace(/<li>(.*?)<\/li>/gi, '- $1\n');
    content = content.replace(/<blockquote>(.*?)<\/blockquote>/gi, '> $1\n');
    content = content.replace(/<p>(.*?)<\/p>/gi, '$1\n\n');
    content = content.replace(/<[^>]+>/g, '');
    content = content.replace(/&amp;/g, '&');
    content = content.replace(/&lt;/g, '<');
    content = content.replace(/&gt;/g, '>');
    content = content.replace(/&quot;/g, '"');
    md += content;
  }

  return md;
}

/**
 * Bitta yozuvni .md fayl sifatida yuklab olish
 */
export function downloadNoteAsMarkdown(note) {
  const md = exportNoteAsMarkdown(note);
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const filename = `${note.title.replace(/[^a-zA-Zа-яА-Я0-9\s]/g, '').trim().replace(/\s+/g, '-')}.md`;

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * JORIY FAOL hotiradagi barcha ma'lumotlarni o'chirish (boshqa hotiralarga tegmaydi!)
 */
export async function clearAllData() {
  const activeHotiraId = localStorage.getItem('active_hotira_id');
  if (!activeHotiraId) return;
  await db.notes.where('hotiraId').equals(activeHotiraId).delete();
  await db.categories.where('hotiraId').equals(activeHotiraId).delete();
  await db.reviewSessions.where('hotiraId').equals(activeHotiraId).delete();
}
