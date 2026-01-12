import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { GrantCard as GrantCardType } from "@/types/research";
import { Calendar, DollarSign, Building2, FileText, CheckCircle2, Clock } from "lucide-react";

interface GrantCardProps {
  grant: GrantCardType;
}

export function GrantCard({ grant }: GrantCardProps) {
  const formatCurrency = (amount?: number) => {
    if (!amount) return null;
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return null;
    try {
      // Handle MM/DD/YYYY format from grants.gov
      if (dateStr.includes("/")) {
        const [month, day, year] = dateStr.split("/");
        return new Date(`${year}-${month}-${day}`).toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      }
      // Handle ISO format
      return new Date(dateStr).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const getDaysUntilClose = (dateStr?: string): number | null => {
    if (!dateStr) return null;
    try {
      let closeDate: Date;
      if (dateStr.includes("/")) {
        const [month, day, year] = dateStr.split("/");
        closeDate = new Date(`${year}-${month}-${day}`);
      } else {
        closeDate = new Date(dateStr);
      }
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      closeDate.setHours(0, 0, 0, 0);
      const diffTime = closeDate.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays;
    } catch {
      return null;
    }
  };

  const daysUntilClose = getDaysUntilClose(grant.meta.close_date);
  const oppStatus = grant.meta.opp_status as string | undefined;

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
                {grant.title}
              </CardTitle>
              {grant.badge && (
                <Badge 
                  variant="secondary" 
                  className="shrink-0 bg-teal-500/20 text-teal-300 border-teal-500/30"
                >
                  {grant.badge}
                </Badge>
              )}
            </div>
            
            {/* Score and Status */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-medium px-2 py-1 bg-primary/20 text-teal-300 rounded border border-teal-500/30">
                Score: {(grant.score * 100).toFixed(0)}%
              </span>
              {oppStatus && (
                <Badge 
                  variant="outline" 
                  className="text-xs border-slate-700 text-slate-400"
                >
                  {oppStatus === "posted" ? (
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3 text-green-400" />
                      Posted
                    </span>
                  ) : oppStatus === "forecasted" ? (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-yellow-400" />
                      Forecasted
                    </span>
                  ) : (
                    oppStatus
                  )}
                </Badge>
              )}
            </div>
          </CardHeader>

          <CardContent className="flex-1 space-y-3">
            {/* Sponsor/Agency */}
            {grant.meta.sponsor && (
              <div className="flex items-start gap-2 text-sm">
                <Building2 className="h-4 w-4 text-teal-400 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Sponsor:</span>
                  <span className="text-slate-400 ml-1">{grant.meta.sponsor}</span>
                  {grant.meta.agency_code && (
                    <span className="text-slate-500 ml-1">({grant.meta.agency_code as string})</span>
                  )}
                </div>
              </div>
            )}

            {/* Opportunity Number */}
            {grant.meta.opp_number && (
              <div className="flex items-start gap-2 text-sm">
                <FileText className="h-4 w-4 text-cyan-400 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Opportunity #:</span>
                  <span className="text-slate-400 ml-1 font-mono text-xs">{grant.meta.opp_number as string}</span>
                </div>
              </div>
            )}

            {/* Funding Amount */}
            {grant.meta.amount_max && (
              <div className="flex items-center gap-2 text-sm">
                <DollarSign className="h-4 w-4 text-green-400 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Maximum Amount:</span>
                  <span className="text-green-400 font-semibold ml-1">
                    {formatCurrency(grant.meta.amount_max)}
                  </span>
                </div>
              </div>
            )}

            {/* Post Date */}
            {grant.meta.post_date && (
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-blue-400 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Posted:</span>
                  <span className="text-slate-400 ml-1">{formatDate(grant.meta.post_date as string)}</span>
                </div>
              </div>
            )}

            {/* Close Date with countdown */}
            {grant.meta.close_date && (
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-orange-400 shrink-0" />
                <div className="flex-1">
                  <span className="text-slate-300 font-medium">Closes:</span>
                  <span className="text-slate-400 ml-1">{formatDate(grant.meta.close_date)}</span>
                  {daysUntilClose !== null && (
                    <span className={`ml-2 text-xs px-2 py-0.5 rounded ${
                      daysUntilClose < 0
                        ? "bg-red-500/20 text-red-400 border border-red-500/30"
                        : daysUntilClose <= 30
                        ? "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                        : "bg-slate-700/50 text-slate-400 border border-slate-600/30"
                    }`}>
                      {daysUntilClose < 0
                        ? "Closed"
                        : daysUntilClose === 0
                        ? "Today"
                        : daysUntilClose === 1
                        ? "1 day left"
                        : `${daysUntilClose} days left`}
                    </span>
                  )}
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="text-xs text-slate-500 border-t border-slate-800/50 pt-3">
            <div className="flex items-center justify-between w-full">
              {grant.meta.source && (
                <span>Source: {grant.meta.source}</span>
              )}
              {grant.meta.opp_number && grant.meta.source === "grants.gov" && (
                <a
                  href={`https://www.grants.gov/web/grants/view-opportunity.html?oppId=${grant.meta.opp_number}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-400 hover:text-teal-300 transition-colors hover:underline"
                >
                  View on Grants.gov →
                </a>
              )}
            </div>
          </CardFooter>
        </div>
      </Card>
    </div>
  );
}
