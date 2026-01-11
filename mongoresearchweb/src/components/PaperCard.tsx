import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { PaperCard as PaperCardType } from "@/types/research";
import { Calendar, Users, FileText, ExternalLink } from "lucide-react";
import Link from "next/link";

interface PaperCardProps {
  paper: PaperCardType;
}

export function PaperCard({ paper }: PaperCardProps) {
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
                {paper.title}
              </CardTitle>
              {paper.badge && (
                <Badge 
                  variant="secondary" 
                  className="shrink-0 bg-teal-500/20 text-teal-300 border-teal-500/30"
                >
                  {paper.badge}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium px-2 py-1 bg-primary/20 text-teal-300 rounded border border-teal-500/30">
                Score: {(paper.score * 100).toFixed(0)}%
              </span>
            </div>
          </CardHeader>

          <CardContent className="flex-1 space-y-3">
            {/* Authors */}
            {paper.meta.authors && paper.meta.authors.length > 0 && (
              <div className="flex items-start gap-2 text-sm">
                <Users className="h-4 w-4 text-cyan-400 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Authors: </span>
                  <span className="text-slate-400">
                    {paper.meta.authors.slice(0, 3).join(", ")}
                    {paper.meta.authors.length > 3 && ` et al. (${paper.meta.authors.length} total)`}
                  </span>
                </div>
              </div>
            )}

            {/* Published Date */}
            {paper.meta.published_date && (
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-blue-400 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Published: </span>
                  <span className="text-slate-400">{formatDate(paper.meta.published_date)}</span>
                </div>
              </div>
            )}

            {/* Additional metadata */}
            {paper.meta.doi && (
              <div className="flex items-start gap-2 text-sm">
                <FileText className="h-4 w-4 text-purple-400 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">DOI: </span>
                  <span className="text-slate-400 font-mono text-xs">{paper.meta.doi as string}</span>
                </div>
              </div>
            )}

            {paper.meta.journal && (
              <div className="flex items-start gap-2 text-sm">
                <FileText className="h-4 w-4 text-indigo-400 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Journal: </span>
                  <span className="text-slate-400">{paper.meta.journal as string}</span>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="text-xs text-slate-500 border-t border-slate-800/50 pt-3">
            <div className="flex items-center justify-between w-full">
              {paper.meta.source && (
                <span>Source: {paper.meta.source}</span>
              )}
              {paper.meta.url && (
                <Link
                  href={paper.meta.url as string}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-400 hover:text-teal-300 transition-colors hover:underline flex items-center gap-1"
                >
                  Read paper
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
