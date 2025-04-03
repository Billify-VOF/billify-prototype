import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { SearchItemResult } from './types';

interface SearchResultItemProps {
  item: SearchItemResult;
  onClick: () => void;
}

export default function SearchResultItem({ item }: SearchResultItemProps) {
  const { name, description } = item;
  return (
    <Card className="max-h-26 m-2 rounded-lg border border-gray-200 bg-white shadow-sm transition hover:shadow-lg">
      <CardHeader>
        <h2 className="text-lg font-semibold text-gray-900">{name}</h2>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600">{description}</p>
      </CardContent>
    </Card>
  );
}
