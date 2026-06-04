export const Toast = ({ message, tone = 'green' }: { message: string; tone?: 'green' | 'red' }) => {
  if (!message) return null;
  const color = tone === 'green' ? 'border-emerald-300/30 text-emerald-200' : 'border-red-300/30 text-red-200';
  return <div className={`rounded-lg border bg-white/5 px-4 py-3 text-sm ${color}`}>{message}</div>;
};
