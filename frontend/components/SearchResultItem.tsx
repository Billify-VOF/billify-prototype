import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { SearchItemResult } from "./types";

interface SearchResultItemProps {
  item: SearchItemResult
  onClick: () => void;
}

export default function SearchResultItem({ item }: SearchResultItemProps) {
  const { name, description } = item
  return (
    <Card className="m-2 border border-gray-200 shadow-sm hover:shadow-lg transition rounded-lg bg-white max-h-26">
      <CardHeader>
        <h2 className="text-lg font-semibold text-gray-900">{name}</h2>
      </CardHeader>
      <CardContent>
        <p className="text-gray-600 text-sm">{description}</p>
      </CardContent>
    </Card>
  );
}