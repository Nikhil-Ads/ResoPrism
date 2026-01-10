import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { NewsCard as NewsCardType } from "@/types/research";
import { Calendar, Newspaper, ExternalLink } from "lucide-react";
import Link from "next/link";

interface NewsCardProps {
  news: NewsCardType;
}

export function NewsCard({ news }: NewsCardProps) {
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
          <CardTitle className="text-lg leading-tight">{news.title}</CardTitle>
          {news.badge && (
            <Badge variant="secondary" className="shrink-0">
              {news.badge}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
          <span className="text-xs font-medium px-2 py-1 bg-primary/10 text-primary rounded">
            Score: {(news.score * 100).toFixed(0)}%
          </span>
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-3">
        {news.meta.outlet && (
          <div className="flex items-center gap-2 text-sm">
            <Newspaper className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{news.meta.outlet}</span>
          </div>
        )}
        {news.meta.published_date && (
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              {formatDate(news.meta.published_date)}
            </span>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex items-center justify-between">
        {news.meta.source && (
          <span className="text-xs text-muted-foreground">
            Source: {news.meta.source}
          </span>
        )}
        {news.meta.url && (
          <Link
            href={news.meta.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-primary hover:underline"
          >
            Read more
            <ExternalLink className="h-3 w-3" />
          </Link>
        )}
      </CardFooter>
    </Card>
  );
}
