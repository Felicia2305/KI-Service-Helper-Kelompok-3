import { CheckCircle2, XCircle } from 'lucide-react';
import { Badge } from '../ui/Badge';

export const SignatureBadge = ({ valid }: { valid?: boolean }) => {
  if (valid === undefined) return <Badge tone="slate">Belum diverifikasi</Badge>;
  return valid
    ? <Badge tone="green"><CheckCircle2 size={14} /> Signature valid</Badge>
    : <Badge tone="red"><XCircle size={14} /> Signature invalid</Badge>;
};
