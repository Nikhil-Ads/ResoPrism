import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { PaperCard as PaperCardType } from "@/types/research";
import { Calendar, Users } from "lucide-react";

interface PaperCardProps {
  paper: PaperCardType;
}

export function PaperCard({ paper }: PaperCardProps) {
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg leading-tight">{paper.title}</CardTitle>
          {paper.badge && (
            <Badge variant="secondary" className="shrink-0">
              {paper.badge}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
          <span className="text-xs font-medium px-2 py-1 bg-primary/10 text-primary rounded">
            Score: {(paper.score * 100).toFixed(0)}%
          </span>
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-3">
        {paper.meta.authors && paper.meta.authors.length > 0 && (
          <div className="flex items-start gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground mt-0.5" />
            <div className="flex-1">
              <span className="text-muted-foreground">
                {paper.meta.authors.slice(0, 3).join(", ")}
                {paper.meta.authors.length > 3 && " et al."}
              </span>
            </div>
          </div>
        )}
        {paper.meta.published_date && (
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              Published: {formatDate(paper.meta.published_date)}
            </span>
          </div>
        )}
      </CardContent>
      {paper.meta.source && (
        <CardFooter className="text-xs text-muted-foreground">
          Source: {paper.meta.source}
        </CardFooter>
      )}
    </Card>
  );
}
