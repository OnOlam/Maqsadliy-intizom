export default function CategoryBadge({ name, color = 'ink', size = 'sm' }) {
  const colorClasses = {
    sage: 'bg-sage-bg text-sage',
    gold: 'bg-gold-bg text-gold',
    lavender: 'bg-lavender-bg text-lavender',
    rose: 'bg-rose-bg text-rose',
    ink: 'bg-ink/5 text-ink',
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
  };

  return (
    <span className={`inline-flex items-center rounded-full font-semibold ${colorClasses[color]} ${sizeClasses[size]}`}>
      {name}
    </span>
  );
}
