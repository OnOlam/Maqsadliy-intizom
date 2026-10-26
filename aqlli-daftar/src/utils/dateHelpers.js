// Oylar nomlari (to'g'ridan-to'g'ri shu yerda)
const MONTHS_UZ = [
  'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
  'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr'
];

// Takrorlash intervallari (kunlarda)
export const REVIEW_INTERVALS = [1, 3, 7, 14, 30, 90, 180];

/**
 * Bugungi sanani YYYY-MM-DD formatida qaytaradi
 */
export function todayStr() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Sanaga kun qo'shadi va YYYY-MM-DD formatida qaytaradi
 */
export function addDays(dateStr, days) {
  const date = new Date(dateStr);
  date.setDate(date.getDate() + days);
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Ikki sana orasidagi kunlar farqini qaytaradi
 */
export function daysDiff(dateStr) {
  const target = new Date(dateStr);
  const today = new Date(todayStr());
  
  target.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  
  const diffTime = target - today;
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}

/**
 * Sanani chiroyli ko'rinishda qaytaradi: "22-iyul"
 */
export function formatUz(dateStr) {
  const date = new Date(dateStr);
  const day = date.getDate();
  const month = MONTHS_UZ[date.getMonth()];
  return `${day}-${month}`;
}

/**
 * Sana uchun nisbiy yorliq qaytaradi
 */
export function dueLabel(dateStr) {
  if (!dateStr) return '';
  const diff = daysDiff(dateStr);
  if (diff === 0) return 'Bugun';
  if (diff === -1) return 'Kecha';
  if (diff === 1) return 'Ertaga';
  if (diff < 0) return `${Math.abs(diff)} kun kechikdi`;
  if (diff <= 7) return `${diff} kundan keyin`;
  return formatUz(dateStr);
}

/**
 * To'liq sana formati: "22-iyul, 2026"
 */
export function formatFullUz(dateStr) {
  const date = new Date(dateStr);
  const day = date.getDate();
  const month = MONTHS_UZ[date.getMonth()];
  const year = date.getFullYear();
  return `${day}-${month}, ${year}`;
}
