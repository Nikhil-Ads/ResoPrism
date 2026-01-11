"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { ErrorAlert } from "@/components/ErrorAlert";
import { ResearchCard } from "@/components/ResearchCard";
import { MindMap } from "@/components/MindMap";
import { Badge } from "@/components/ui/badge";
import { fetchInbox, generateMindMap } from "@/lib/api";
import type { ResearchResponse, MindMapResponse } from "@/types/research";
import { Search, ArrowLeft, X, LayoutGrid, Network, Sparkles } from "lucide-react";

type ViewMode = "grid" | "mindmap";

export default function DemoPage() {
  const [query, setQuery] = useState("ml healthcare funding");
  const [intent, setIntent] = useState<"grants" | "papers" | "news" | "all">("all");
  const [data, setData] = useState<ResearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  
  // Mind map state
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [mindMapData, setMindMapData] = useState<MindMapResponse | null>(null);
  const [mindMapLoading, setMindMapLoading] = useState(false);
  const [mindMapError, setMindMapError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setHasSearched(true);
      setMindMapData(null);
      setMindMapError(null);
      const result = await fetchInbox(query.trim(), intent);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch results");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMindMap = async () => {
    if (!data) return;
    
    try {
      setMindMapLoading(true);
      setMindMapError(null);
      setViewMode("mindmap");
      
      const result = await generateMindMap({
        grants: data.grants,
        papers: data.papers,
        news: data.news,
        user_query: data.user_query,
      });
      
      setMindMapData(result);
    } catch (err) {
      setMindMapError(err instanceof Error ? err.message : "Failed to generate mind map");
    } finally {
      setMindMapLoading(false);
    }
  };

  const handleClear = () => {
    setQuery("");
    setIntent("all");
    setData(null);
    setError(null);
    setHasSearched(false);
    setViewMode("grid");
    setMindMapData(null);
    setMindMapError(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Research Inbox Demo</h1>
            <p className="mt-2 text-muted-foreground">
              Search for grants, papers, and news using our multi-agent system
            </p>
          </div>
          <Button asChild variant="outline">
            <Link href="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Link>
          </Button>
        </div>

        {/* Search Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Search Research Data</CardTitle>
            <CardDescription>
              Enter a query and select the type of research you want to find
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4 sm:flex-row">
              <div className="flex-1">
                <Input
                  placeholder="Enter your search query (e.g., 'ml healthcare funding')"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full"
                />
              </div>
              <div className="w-full sm:w-48">
                <Select value={intent} onValueChange={(value: typeof intent) => setIntent(value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select intent" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sources</SelectItem>
                    <SelectItem value="grants">Grants Only</SelectItem>
                    <SelectItem value="papers">Papers Only</SelectItem>
                    <SelectItem value="news">News Only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleSearch} disabled={loading} className="flex-1 sm:flex-initial">
                  <Search className="mr-2 h-4 w-4" />
                  {loading ? "Searching..." : "Search"}
                </Button>
                {hasSearched && (
                  <Button onClick={handleClear} variant="outline" size="icon">
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <div className="mb-8">
            <ErrorAlert message={error} />
          </div>
        )}

        {/* Loading State */}
        {loading && <LoadingSkeleton />}

        {/* Results Display */}
        {!loading && data && (
          <div className="space-y-8">
            {/* Results Summary & View Toggle */}
            <div className="flex flex-wrap items-center gap-4">
              <div>
                <h2 className="text-2xl font-semibold">Results</h2>
                <p className="text-sm text-muted-foreground">
                  Query: &quot;{data.user_query}&quot; | Intent: {data.intent || "all"}
                </p>
              </div>
              <div className="ml-auto flex flex-wrap items-center gap-3">
                {/* Result counts */}
                <div className="flex flex-wrap gap-2">
                  {data.grants.length > 0 && (
                    <Badge variant="secondary">
                      {data.grants.length} Grant{data.grants.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                  {data.papers.length > 0 && (
                    <Badge variant="secondary">
                      {data.papers.length} Paper{data.papers.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                  {data.news.length > 0 && (
                    <Badge variant="secondary">
                      {data.news.length} News Item{data.news.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                </div>
                
                {/* View Mode Toggle */}
                <div className="flex items-center gap-1 rounded-lg border bg-muted p-1">
                  <Button
                    variant={viewMode === "grid" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setViewMode("grid")}
                    className="h-8 px-3"
                  >
                    <LayoutGrid className="mr-1.5 h-4 w-4" />
                    Grid
                  </Button>
                  <Button
                    variant={viewMode === "mindmap" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => {
                      if (!mindMapData && !mindMapLoading) {
                        handleGenerateMindMap();
                      } else {
                        setViewMode("mindmap");
                      }
                    }}
                    className="h-8 px-3"
                    disabled={mindMapLoading}
                  >
                    <Network className="mr-1.5 h-4 w-4" />
                    Mind Map
                    {!mindMapData && !mindMapLoading && (
                      <Sparkles className="ml-1 h-3 w-3 text-yellow-500" />
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* Errors from API */}
            {data.errors && data.errors.length > 0 && (
              <ErrorAlert
                title="API Errors"
                message={data.errors.join(", ")}
              />
            )}

            {/* Mind Map View */}
            {viewMode === "mindmap" && (
              <MindMap
                markdown={mindMapData?.markdown || ""}
                loading={mindMapLoading}
                error={mindMapError}
                onRefresh={handleGenerateMindMap}
              />
            )}

            {/* Mind Map Themes */}
            {viewMode === "mindmap" && mindMapData && mindMapData.themes.length > 0 && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Sparkles className="h-5 w-5 text-yellow-500" />
                    Identified Themes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {mindMapData.themes.map((theme, index) => (
                      <Badge 
                        key={index} 
                        variant="outline"
                        className="bg-gradient-to-r from-teal-500/10 to-cyan-500/10 border-teal-500/30 text-teal-700 dark:text-teal-300"
                      >
                        {theme}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Grid View - Ranked Inbox Cards */}
            {viewMode === "grid" && data.inbox_cards && data.inbox_cards.length > 0 && (
              <div>
                <h3 className="mb-4 text-xl font-semibold">
                  Ranked Results ({data.inbox_cards.length})
                </h3>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {data.inbox_cards.map((card) => (
                    <ResearchCard key={card.id} card={card} />
                  ))}
                </div>
              </div>
            )}

            {/* Grid View - Empty State */}
            {viewMode === "grid" && (!data.inbox_cards || data.inbox_cards.length === 0) && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <p className="text-lg text-muted-foreground">No results found</p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Try a different search query or intent
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Separate Sections by Type (if not showing ranked) */}
            {viewMode === "grid" && data.inbox_cards.length === 0 && (
              <>
                {data.grants.length > 0 && (
                  <div>
                    <h3 className="mb-4 text-xl font-semibold">Grants</h3>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {data.grants.map((grant) => (
                        <ResearchCard key={grant.id} card={grant} />
                      ))}
                    </div>
                  </div>
                )}

                {data.papers.length > 0 && (
                  <div>
                    <h3 className="mb-4 text-xl font-semibold">Papers</h3>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {data.papers.map((paper) => (
                        <ResearchCard key={paper.id} card={paper} />
                      ))}
                    </div>
                  </div>
                )}

                {data.news.length > 0 && (
                  <div>
                    <h3 className="mb-4 text-xl font-semibold">News</h3>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {data.news.map((news) => (
                        <ResearchCard key={news.id} card={news} />
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Empty State */}
        {!loading && !hasSearched && !error && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Search className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="text-lg font-medium">Start a search to see results</p>
              <p className="mt-2 text-sm text-muted-foreground">
                Enter a query above and click Search to get started
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
