import db from '../db/database';

export async function getAllHotiras() {
  try {
    const hotiras = await db.hotiras.toArray();
    return hotiras.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  } catch (error) {
    console.error("Hotiralar yuklanmadi:", error);
    return [];
  }
}

export async function createHotira(name) {
  // ⭐ 3.2 TUZATISH: bo'shliqlarni tozalash va tekshirish
  const cleanName = (name || '').trim();
  if (!cleanName) {
    throw new Error("Hotira nomi bo'sh bo'lishi mumkin emas!");
  }

  const newHotira = {
    id: `hotira-${Date.now()}`,
    name: cleanName,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  await db.hotiras.add(newHotira);
  return newHotira;
}

export async function deleteHotira(id) {
  // Kaskadli tozalash: avval ma'lumotlar, keyin hotira
  await db.notes.where('hotiraId').equals(id).delete();
  await db.categories.where('hotiraId').equals(id).delete();
  await db.reviewSessions.where('hotiraId').equals(id).delete();
  await db.hotiras.delete(id);

  // Agar o'chirilgan hotira faol bo'lsa, localStorage ni tozalash
  const activeId = localStorage.getItem('active_hotira_id');
  if (activeId === id) {
    localStorage.removeItem('active_hotira_id');
    window.dispatchEvent(new Event('hotiraChanged'));
  }
}

// ⭐ 2.4 TUZATISH: o'zbekcha harflarni to'g'ri qayta ishlash
function makeSafeFilename(name) {
  return name
    .trim()
    .replace(/['ʼ`]/g, '')                              // apostroflarni olib tashlash (o', g')
    .replace(/[^a-zA-Z0-9а-яА-Яўғҳқчшўё]/gi, '-')       // ruxsat etilmagan belgilarni chiziqchaga
    .replace(/-+/g, '-')                                 // takroriy chiziqchalarni bittaga
    .replace(/^-|-$/g, '')                               // bosh/oxiridagi chiziqchani olish
    || 'hotira';                                          // bo'sh qolsa zaxira nom
}

export async function exportHotira(id) {
  const hotira = await db.hotiras.get(id);
  if (!hotira) throw new Error("Hotira topilmadi");

  const notes = await db.notes.where('hotiraId').equals(id).toArray();
  const categories = await db.categories.where('hotiraId').equals(id).toArray();
  const reviewSessions = await db.reviewSessions.where('hotiraId').equals(id).toArray();

  const data = {
    version: '1.0',
    hotiraId: id,
    hotiraName: hotira.name,
    notes,
    categories,
    reviewSessions,
    exportDate: new Date().toISOString(),
  };

  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  // ⭐ Endi o'zbekcha nomlar to'g'ri chiqadi!
  const filename = `aqlli-daftar-${makeSafeFilename(hotira.name)}-${Date.now()}.aqlli`;

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function importHotira(file) {
  try {
    const text = await file.text();
    const data = JSON.parse(text);

    if (!data.hotiraId || !data.hotiraName) {
      throw new Error("Noto'g'ri fayl formati");
    }

    const newHotira = await createHotira(data.hotiraName);
    const newHotiraId = newHotira.id;

    if (data.notes && data.notes.length > 0) {
      const notesWithNewId = data.notes.map(note => ({
        ...note,
        id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        hotiraId: newHotiraId,
      }));
      await db.notes.bulkAdd(notesWithNewId);
    }

    if (data.categories && data.categories.length > 0) {
      const catsWithNewId = data.categories.map(cat => ({
        ...cat,
        id: `cat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        hotiraId: newHotiraId,
      }));
      await db.categories.bulkAdd(catsWithNewId);
    }

    if (data.reviewSessions && data.reviewSessions.length > 0) {
      const sessionsWithNewId = data.reviewSessions.map(session => ({
        ...session,
        id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        hotiraId: newHotiraId,
      }));
      await db.reviewSessions.bulkAdd(sessionsWithNewId);
    }

    localStorage.setItem('active_hotira_id', newHotiraId);
    window.dispatchEvent(new Event('hotiraChanged'));

    return { success: true, hotiraId: newHotiraId };
  } catch (error) {
    console.error("Import xatosi:", error);
    throw new Error("Hotira import qilinmadi: " + error.message);
  }
}
