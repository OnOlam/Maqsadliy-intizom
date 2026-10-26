import { NavLink } from 'react-router-dom';
import { Home, FileText, FolderOpen, Brain, Settings, Database, Menu } from 'lucide-react';

const navItems = [
  { to: '/', icon: Home, label: 'Bosh sahifa' },
  { to: '/notes', icon: FileText, label: 'Yozuvlar' },
  { to: '/categories', icon: FolderOpen, label: 'Kategoriyalar' },
  { to: '/review', icon: Brain, label: 'Takrorlash' },
  { to: '/hotira', icon: Database, label: 'Hotira' },
  { to: '/settings', icon: Settings, label: 'Sozlamalar' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-card border-r border-line h-full p-4 flex flex-col">
      <div className="mb-8">
        <h1 className="font-serif font-bold text-xl text-ink">Aqlli Daftar</h1>
        <p className="text-xs text-ink-soft">Bilimlar bazasi</p>
      </div>

      <nav className="space-y-2 flex-1">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                isActive
                  ? 'bg-ink text-cream'
                  : 'text-ink-soft hover:bg-line/30'
              }`
            }
          >
            <item.icon size={20} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
