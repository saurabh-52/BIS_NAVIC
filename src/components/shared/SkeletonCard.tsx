export default function SkeletonCard({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`bg-card rounded-2xl p-6 border border-border ${className}`}>
      <div className="skeleton h-5 w-2/3 mb-4" />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton h-3 mb-3" style={{ width: `${85 - i * 15}%` }} />
      ))}
    </div>
  );
}
