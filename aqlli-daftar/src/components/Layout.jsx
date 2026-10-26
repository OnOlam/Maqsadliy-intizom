import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      {/* Chap tomon - Sidebar (faqat katta ekranlarda) */}
      <aside className="hidden md:block w-64 bg-card border-r border-line">
        <Sidebar />
      </aside>

      {/* O'ng tomon - Asosiy kontent */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
