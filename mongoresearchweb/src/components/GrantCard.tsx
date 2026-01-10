import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { GrantCard as GrantCardType } from "@/types/research";
import { Calendar, DollarSign, Building2 } from "lucide-react";

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
          <CardTitle className="text-lg leading-tight">{grant.title}</CardTitle>
          {grant.badge && (
            <Badge variant="secondary" className="shrink-0">
              {grant.badge}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
          <span className="text-xs font-medium px-2 py-1 bg-primary/10 text-primary rounded">
            Score: {(grant.score * 100).toFixed(0)}%
          </span>
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-3">
        {grant.meta.sponsor && (
          <div className="flex items-center gap-2 text-sm">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{grant.meta.sponsor}</span>
          </div>
        )}
        {grant.meta.amount_max && (
          <div className="flex items-center gap-2 text-sm">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              Up to {formatCurrency(grant.meta.amount_max)}
            </span>
          </div>
        )}
        {grant.meta.close_date && (
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              Closes: {formatDate(grant.meta.close_date)}
            </span>
          </div>
        )}
      </CardContent>
      {grant.meta.source && (
        <CardFooter className="text-xs text-muted-foreground">
          Source: {grant.meta.source}
        </CardFooter>
      )}
    </Card>
  );
}
