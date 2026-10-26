import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';
import { useCallback, useEffect } from 'react';

export default function RichTextEditor({ content, onChange }) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        underline: false,
        textAlign: false,
      }),
      CodeBlockLowlight.configure({
        lowlight: createLowlight(common),
      }),
      Underline,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-500 underline cursor-pointer',
        },
      }),
      Placeholder.configure({
        placeholder: 'Bu yerga batafsil ma\'lumot yozing...',
      }),
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  // Content o'zgarganda editor'ni yangilash
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content || '');
    }
  }, [content]);

  const setLink = useCallback(() => {
    const url = window.prompt('Havola URL sini kiriting:');
    if (url === null) return;
    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }
    editor.chain().focus().setLink({ href: url }).run();
  }, [editor]);

  if (!editor) {
    return <div className="p-4 text-center text-ink-soft">Yuklanmoqda...</div>;
  }

  return (
    <div className="border border-line rounded-xl overflow-hidden bg-card">
      {/* Toolbar - 1-qator */}
      <div className="flex items-center gap-1 p-2 border-b border-line flex-wrap toolbar-bg">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          title="Qalin (Ctrl+B)"
        >
          <strong>B</strong>
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          title="Kursiv (Ctrl+I)"
        >
          <em>I</em>
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          isActive={editor.isActive('underline')}
          title="Ta'kidlash (Ctrl+U)"
        >
          <u>U</u>
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleStrike().run()}
          isActive={editor.isActive('strike')}
          title="Chizilgan"
        >
          <s>S</s>
        </ToolbarButton>

        <div className="w-px h-5 bg-line mx-1" />

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCode().run()}
          isActive={editor.isActive('code')}
          title="Kod (Ctrl+E)"
        >
          {'</>'}
        </ToolbarButton>

        <div className="w-px h-5 bg-line mx-1" />

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          isActive={editor.isActive('heading', { level: 1 })}
          title="Sarlavha 1"
        >
          H1
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          isActive={editor.isActive('heading', { level: 2 })}
          title="Sarlavha 2"
        >
          H2
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          isActive={editor.isActive('heading', { level: 3 })}
          title="Sarlavha 3"
        >
          H3
        </ToolbarButton>
      </div>

      {/* Toolbar - 2-qator */}
      <div className="flex items-center gap-1 p-2 border-b border-line flex-wrap toolbar-bg">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive('bulletList')}
          title="Ro'yxat"
        >
          • List
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive('orderedList')}
          title="Raqamli ro'yxat"
        >
          1. List
        </ToolbarButton>

        <div className="w-px h-5 bg-line mx-1" />

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          isActive={editor.isActive('blockquote')}
          title="Iqtibos"
        >
          " Quote
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          isActive={editor.isActive('codeBlock')}
          title="Kod bloki"
        >
          {'{ }'}
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          isActive={false}
          title="Chiziq"
        >
          —
        </ToolbarButton>

        <div className="w-px h-5 bg-line mx-1" />

        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          isActive={editor.isActive({ textAlign: 'left' })}
          title="Chapga"
        >
          ⬅
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          isActive={editor.isActive({ textAlign: 'center' })}
          title="O'rtaga"
        >
          ⬆⬇
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          isActive={editor.isActive({ textAlign: 'right' })}
          title="O'ngga"
        >
          
        </ToolbarButton>

        <div className="w-px h-5 bg-line mx-1" />

        <ToolbarButton
          onClick={setLink}
          isActive={editor.isActive('link')}
          title="Havola"
        >
          
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          isActive={false}
          disabled={!editor.can().undo()}
          title="Ortga (Ctrl+Z)"
        >
          
        </ToolbarButton>

        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          isActive={false}
          disabled={!editor.can().redo()}
          title="Qaytarish (Ctrl+Y)"
        >
          ↷
        </ToolbarButton>
      </div>

      {/* Muharrir */}
      <EditorContent editor={editor} />

      {/* Stil */}
      <style>{`
        .ProseMirror {
          min-height: 300px;
          padding: 12px 16px;
          outline: none;
          font-family: inherit;
          background-color: var(--bg-card, #FFFCF6);
          color: var(--text-primary, #4A4032);
        }
        .ProseMirror p.is-editor-empty:first-child::before {
          content: attr(data-placeholder);
          float: left;
          color: var(--text-secondary, #93876F);
          pointer-events: none;
          height: 0;
        }
        .ProseMirror h1 {
          font-size: 2em;
          font-weight: bold;
          margin: 0.5em 0;
          color: var(--text-primary, #4A4032);
        }
        .ProseMirror h2 {
          font-size: 1.5em;
          font-weight: bold;
          margin: 0.5em 0;
          color: var(--text-primary, #4A4032);
        }
        .ProseMirror h3 {
          font-size: 1.25em;
          font-weight: bold;
          margin: 0.5em 0;
          color: var(--text-primary, #4A4032);
        }
        .ProseMirror ul {
          list-style-type: disc;
          padding-left: 1.5em;
          margin: 0.5em 0;
        }
        .ProseMirror ol {
          list-style-type: decimal;
          padding-left: 1.5em;
          margin: 0.5em 0;
        }
        .ProseMirror blockquote {
          border-left: 3px solid var(--border, #EADFC4);
          padding-left: 1em;
          margin: 0.5em 0;
          color: var(--text-secondary, #93876F);
        }
        .ProseMirror pre {
          background: #1e1e1e;
          color: #d4d4d4;
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          padding: 16px;
          border-radius: 8px;
          overflow-x: auto;
          margin: 0.5em 0;
          font-size: 0.9em;
          line-height: 1.5;
        }
        .ProseMirror pre code {
          background: transparent;
          color: inherit;
          padding: 0;
          font-size: inherit;
        }
        .ProseMirror code {
          background: rgba(125, 211, 160, 0.15);
          color: var(--text-primary, #4A4032);
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 0.9em;
        }
        .ProseMirror pre code {
          background: transparent;
          color: inherit;
          padding: 0;
        }
        .ProseMirror a {
          color: #3b82f6;
          text-decoration: underline;
          cursor: pointer;
        }
        .ProseMirror hr {
          border: none;
          border-top: 2px solid var(--border, #EADFC4);
          margin: 1em 0;
        }
        
        /* Syntax highlighting ranglari */
        .ProseMirror pre .hljs-keyword { color: #569cd6; }
        .ProseMirror pre .hljs-string { color: #ce9178; }
        .ProseMirror pre .hljs-number { color: #b5cea8; }
        .ProseMirror pre .hljs-comment { color: #6a9955; font-style: italic; }
        .ProseMirror pre .hljs-function { color: #dcdcaa; }
        .ProseMirror pre .hljs-variable { color: #9cdcfe; }
        .ProseMirror pre .hljs-built_in { color: #4ec9b0; }
        .ProseMirror pre .hljs-class { color: #4ec9b0; }
        .ProseMirror pre .hljs-title { color: #dcdcaa; }
        .ProseMirror pre .hljs-params { color: #9cdcfe; }
        .ProseMirror pre .hljs-attr { color: #9cdcfe; }
        .ProseMirror pre .hljs-tag { color: #569cd6; }
        .ProseMirror pre .hljs-name { color: #4ec9b0; }
        .ProseMirror pre .hljs-attribute { color: #9cdcfe; }
        .ProseMirror pre .hljs-selector-class { color: #d7ba7d; }
        .ProseMirror pre .hljs-selector-id { color: #d7ba7d; }
        .ProseMirror pre .hljs-regexp { color: #d16969; }
        .ProseMirror pre .hljs-literal { color: #569cd6; }
        .ProseMirror pre .hljs-meta { color: #9b9b9b; }
        
        /* Dark mode */
        [data-theme="dark"] .ProseMirror {
          background-color: #1e252d;
          color: #e6e8eb;
        }
        [data-theme="dark"] .ProseMirror p.is-editor-empty:first-child::before {
          color: #8b949e;
        }
        [data-theme="dark"] .ProseMirror h1,
        [data-theme="dark"] .ProseMirror h2,
        [data-theme="dark"] .ProseMirror h3 {
          color: #e6e8eb;
        }
        [data-theme="dark"] .ProseMirror blockquote {
          border-left-color: #2d333b;
          color: #8b949e;
        }
        [data-theme="dark"] .ProseMirror code {
          background: rgba(125, 211, 160, 0.15);
          color: #e6e8eb;
        }
        [data-theme="dark"] .ProseMirror a {
          color: #60a5fa;
        }
        [data-theme="dark"] .ProseMirror hr {
          border-top-color: #2d333b;
        }
        [data-theme="dark"] .ProseMirror pre {
          background: #1e1e1e;
          color: #d4d4d4;
        }
      `}</style>
    </div>
  );
}

function ToolbarButton({ onClick, isActive, title, disabled, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all duration-150 ${
        isActive
          ? 'bg-ink text-cream shadow-sm'
          : 'text-ink-soft hover:bg-line/40 hover:text-ink'
      } ${disabled ? 'opacity-30 cursor-not-allowed' : ''}`}
    >
      {children}
    </button>
  );
}
