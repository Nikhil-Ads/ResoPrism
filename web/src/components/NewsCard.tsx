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
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="group relative h-full">
      <Card className="glare-hover group rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 via-slate-900/60 to-slate-950/80 hover:border-teal-500/40 hover:shadow-2xl hover:shadow-teal-500/20 transition-all hover:scale-105 transform relative overflow-hidden h-full flex flex-col">
        {/* Liquid morphing shape background */}
        <div className="absolute inset-0 bg-gradient-to-br from-teal-400/0 via-cyan-300/0 to-teal-300/0 group-hover:from-teal-400/10 group-hover:via-cyan-300/10 group-hover:to-teal-300/10 transition-all blur-xl liquid-shape" />
        <div className="absolute -inset-2 bg-gradient-to-br from-teal-400/20 via-cyan-300/20 to-teal-300/20 blur-3xl opacity-0 group-hover:opacity-60 transition-opacity -z-10 liquid-shape" />

        <div className="relative z-10 flex flex-col h-full">
          <CardHeader>
            <div className="flex items-start justify-between gap-2 mb-2">
              <CardTitle className="text-lg leading-tight text-slate-100 group-hover:text-teal-300 transition-colors flex-1">
                {news.title}
              </CardTitle>
              {news.badge && (
                <Badge 
                  variant="secondary" 
                  className="shrink-0 bg-teal-500/20 text-teal-300 border-teal-500/30"
                >
                  {news.badge}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium px-2 py-1 bg-primary/20 text-teal-300 rounded border border-teal-500/30">
                Score: {(news.score * 100).toFixed(0)}%
              </span>
            </div>
          </CardHeader>

          <CardContent className="flex-1 space-y-3">
            {/* Outlet */}
            {news.meta.outlet && (
              <div className="flex items-center gap-2 text-sm">
                <Newspaper className="h-4 w-4 text-cyan-400 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Source: </span>
                  <span className="text-slate-400">{news.meta.outlet}</span>
                </div>
              </div>
            )}

            {/* Published Date */}
            {news.meta.published_date && (
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-blue-400 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Published: </span>
                  <span className="text-slate-400">{formatDate(news.meta.published_date)}</span>
                </div>
              </div>
            )}

            {/* Description if available */}
            {news.meta.description && (
              <div className="text-sm text-slate-400 line-clamp-3">
                {news.meta.description as string}
              </div>
            )}
          </CardContent>

          <CardFooter className="text-xs text-slate-500 border-t border-slate-800/50 pt-3">
            <div className="flex items-center justify-between w-full">
              {news.meta.source && (
                <span>Source: {news.meta.source}</span>
              )}
              {news.meta.url && (
                <Link
                  href={news.meta.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-400 hover:text-teal-300 transition-colors hover:underline flex items-center gap-1"
                >
                  Read article
                  <ExternalLink className="h-3 w-3" />
                </Link>
              )}
            </div>
          </CardFooter>
        </div>
      </Card>
    </div>
  );
}
