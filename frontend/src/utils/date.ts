export const parseUTCDate = (dateStr?: string | null): Date | null => {
  if (!dateStr) return null;
  let s = String(dateStr).trim();
  if (!s) return null;
  // If no timezone offset exists (no Z, no +, no - after index 10)
  if (!s.endsWith('Z') && !s.includes('+') && !s.slice(10).includes('-')) {
    s = s.replace(' ', 'T') + 'Z';
  }
  const d = new Date(s);
  return isNaN(d.getTime()) ? null : d;
};

export const formatDateTime = (dateStr?: string | null): string => {
  const d = parseUTCDate(dateStr);
  return d ? d.toLocaleString() : '—';
};

export const formatTimeOnly = (dateStr?: string | null): string => {
  const d = parseUTCDate(dateStr);
  return d ? d.toLocaleTimeString() : '—';
};

export const formatDateOnly = (dateStr?: string | null): string => {
  const d = parseUTCDate(dateStr);
  return d ? d.toLocaleDateString() : '—';
};
