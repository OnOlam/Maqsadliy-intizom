// Yozuv holatlari
export const NOTE_STATUS = {
  PLANNED: 'planned',       // Rejalashtirilgan
  LEARNING: 'learning',     // O'rganilayotgan
  LEARNED: 'learned',       // O'zlashtirilgan
};

export const NOTE_STATUS_LABEL = {
  planned: 'Rejalashtirilgan',
  learning: "O'rganilayotgan",
  learned: "O'zlashtirilgan",
};

export const NOTE_STATUS_COLOR = {
  planned: 'lavender',
  learning: 'gold',
  learned: 'sage',
};

// Asosiy kategoriyalar (boshlang'ich)
export const DEFAULT_CATEGORIES = [
  {
    id: 'cat-frontend',
    name: 'Frontend',
    icon: 'Layout',
    color: 'sage',
    parentId: 'cat-dasturlash',
  },
  {
    id: 'cat-backend',
    name: 'Backend',
    icon: 'Server',
    color: 'gold',
    parentId: 'cat-dasturlash',
  },
  {
    id: 'cat-dasturlash',
    name: 'Dasturlash',
    icon: 'Code',
    color: 'ink',
    parentId: null,
  },
  {
    id: 'cat-cybersec',
    name: 'Kiberxavfsizlik',
    icon: 'Shield',
    color: 'rose',
    parentId: null,
  },
  {
    id: 'cat-english',
    name: 'English',
    icon: 'Languages',
    color: 'lavender',
    parentId: 'cat-tillar',
  },
  {
    id: 'cat-russian',
    name: 'Русский',
    icon: 'Languages',
    color: 'lavender',
    parentId: 'cat-tillar',
  },
  {
    id: 'cat-tillar',
    name: 'Tillar',
    icon: 'BookOpen',
    color: 'ink',
    parentId: null,
  },
];

// Takrorlash intervallari (kunlarda) — Spaced Repetition
export const REVIEW_INTERVALS = [1, 3, 7, 14, 30, 90, 180];

// Oylar (o'zbekcha)
export const MONTHS_UZ = [
  'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
  'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr'
];
