import Dexie from 'dexie';

const db = new Dexie('aqlli_daftar');

db.version(2).stores({
  notes: 'id, title, content, excerpt, status, categoryId, tags, reviewMode, reviewStage, nextReviewDate, createdAt, updatedAt, lastReviewedAt, hotiraId',
  categories: 'id, name, color, parentId, hotiraId',
  reviewSessions: 'id, noteId, rating, timestamp, nextReviewDate, hotiraId',
  hotiras: 'id, name, createdAt, updatedAt',
});

export default db;

function getActiveHotiraId() {
  return localStorage.getItem('active_hotira_id') || null;
}

export async function getAllNotes() {
  const hotiraId = getActiveHotiraId();
  if (!hotiraId) return [];
  return await db.notes.where('hotiraId').equals(hotiraId).toArray();
}

export async function getNoteById(id) {
  const hotiraId = getActiveHotiraId();
  const note = await db.notes.get(id);
  if (note && note.hotiraId === hotiraId) {
    return note;
  }
  return null;
}

export async function addNote(note) {
  const hotiraId = getActiveHotiraId();
  if (!hotiraId) throw new Error("Faol hotira yo'q!");
  const now = new Date().toISOString();
  return await db.notes.add({
    ...note,
    id: `note-${Date.now()}`,
    hotiraId,
    createdAt: now,
    updatedAt: now,
  });
}

export async function updateNote(id, updates) {
  const hotiraId = getActiveHotiraId();
  const note = await db.notes.get(id);
  if (!note || note.hotiraId !== hotiraId) {
    throw new Error("Bu yozuvni tahrirlashga ruxsat yo'q!");
  }
  return await db.notes.update(id, {
    ...updates,
    updatedAt: new Date().toISOString(),
  });
}

export async function deleteNote(id) {
  const hotiraId = getActiveHotiraId();
  const note = await db.notes.get(id);
  if (!note || note.hotiraId !== hotiraId) {
    throw new Error("Bu yozuvni o'chirishga ruxsat yo'q!");
  }
  return await db.notes.delete(id);
}

export async function getAllCategories() {
  const hotiraId = getActiveHotiraId();
  if (!hotiraId) return [];
  return await db.categories.where('hotiraId').equals(hotiraId).toArray();
}

export async function addCategory(category) {
  const hotiraId = getActiveHotiraId();
  if (!hotiraId) throw new Error("Faol hotira yo'q!");
  return await db.categories.add({
    ...category,
    hotiraId,
  });
}

export async function updateCategory(id, updates) {
  const hotiraId = getActiveHotiraId();
  const cat = await db.categories.get(id);
  if (!cat || cat.hotiraId !== hotiraId) {
    throw new Error("Bu kategoriyani tahrirlashga ruxsat yo'q!");
  }
  return await db.categories.update(id, updates);
}

export async function deleteCategory(id) {
  const hotiraId = getActiveHotiraId();
  const cat = await db.categories.get(id);
  if (!cat || cat.hotiraId !== hotiraId) {
    throw new Error("Bu kategoriyani o'chirishga ruxsat yo'q!");
  }
  return await db.categories.delete(id);
}

export async function getNotesByCategory(categoryId) {
  const hotiraId = getActiveHotiraId();
  return await db.notes.where({
    categoryId: categoryId,
    hotiraId: hotiraId
  }).toArray();
}

export async function getDueNotes() {
  const hotiraId = getActiveHotiraId();
  const today = new Date().toISOString().slice(0, 10);
  return await db.notes.where({
    hotiraId: hotiraId
  }).filter(note => note.nextReviewDate && note.nextReviewDate <= today).toArray();
}
