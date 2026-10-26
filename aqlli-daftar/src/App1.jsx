import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import NotesPage from './pages/NotesPage';
import NoteEditorPage from './pages/NoteEditorPage';
import CategoriesPage from './pages/CategoriesPage';
import ReviewPage from './pages/ReviewPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Bosh sahifa - default */}
        <Route index element={<HomePage />} />
        
        {/* Barcha yozuvlar */}
        <Route path="notes" element={<NotesPage />} />
        
        {/* Yangi yozuv yaratish */}
        <Route path="notes/new" element={<NoteEditorPage />} />
        
        {/* Yozuvni tahrirlash */}
        <Route path="notes/:id/edit" element={<NoteEditorPage />} />
        
        {/* Kategoriyalar */}
        <Route path="categories" element={<CategoriesPage />} />
        
        {/* Takrorlash (flashcard) */}
        <Route path="review" element={<ReviewPage />} />
        
        {/* Noto'g'ri manzil - bosh sahifaga qaytarish */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
