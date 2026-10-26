import { useContext } from 'react';
import { ThemeContext } from '../context/ThemeContext';
import { Moon, Sun } from 'lucide-react';
import { useLocation, Link } from 'react-router-dom';
import { Plus, Menu, Search } from 'lucide-react';
import { useState } from 'react';
import Sidebar from './Sidebar';

const PAGE_TITLES = {
  '/': 'Bosh sahifa',
  '/notes': 'Yozuvlar',
  '/notes/new': 'Yangi yozuv',
  '/categories': 'Kategoriyalar',
  '/review': 'Takrorlash',
  '/settings': 'Sozlamalar',
};

export default function Header() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const location = useLocation();
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  // Yozuv tahrirlash sahifasi uchun maxsus sarlavha
  const isEditPage = location.pathname.match(/^\/notes\/.+\/edit$/);
  const title = isEditPage ? 'Yozuvni tahrirlash' : (PAGE_TITLES[location.pathname] || 'Aqlli Daftar');

  // Yangi yozuv tugmasi faqat "Yozuvlar" sahifasida ko'rinadi
  const showAddButton = location.pathname === '/notes';

  return (
    <>
      <header className="bg-cream border-b border-line sticky top-0 z-30">
        <div className="flex items-center justify-between px-4 md:px-6 py-3">
          {/* Chap tomon */}
          <div className="flex items-center gap-3">
            {/* Mobil menyu tugmasi (faqat kichik ekranlarda) */}
            <button
              onClick={() => setShowMobileMenu(true)}
              className="md:hidden p-2 rounded-lg hover:bg-line/40"
            >
              <Menu size={20} />
            </button>
            
            <h2 className="font-serif font-semibold text-xl md:text-2xl">
              {title}
            </h2>
          </div>

          {/* O'ng tomon */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-line/40 text-ink-soft hover:text-ink transition-colors"
              title={theme === 'light' ? 'Qorong\'u rejim' : 'Yorug\' rejim'}
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>
            {showAddButton && (
              <Link to="/notes/new" className="btn-primary">
                <Plus size={16} />
                <span className="hidden sm:inline">Yangi</span>
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Mobil menyu (overlay) */}
      {showMobileMenu && (
        <div 
          className="fixed inset-0 bg-ink/30 z-40 md:hidden"
          onClick={() => setShowMobileMenu(false)}
        >
          <div 
            className="w-64 h-full bg-card"
            onClick={(e) => e.stopPropagation()}
          >
            <Sidebar />
          </div>
        </div>
      )}
    </>
  );
}
