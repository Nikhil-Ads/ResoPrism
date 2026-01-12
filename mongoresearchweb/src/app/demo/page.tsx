"use client";

import { useState, useEffect } from "react";
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
import { ResearchCarousel } from "@/components/ResearchCarousel";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { fetchInbox, generateSummary, generateMindMap } from "@/lib/api";
import type { ResearchResponse } from "@/types/research";
import { USER_INFO, LAB_PROFILE } from "@/lib/labProfile";
import { Search, ArrowLeft, X, User, ExternalLink, Network } from "lucide-react";
import { MindMap } from "@/components/MindMap";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const [dashboardQuery] = useState("Musculoskeletal");
  const [dashboardData, setDashboardData] = useState<ResearchResponse | null>(null);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  
  // Summary states
  const [grantsSummary, setGrantsSummary] = useState<string | null>(null);
  const [papersSummary, setPapersSummary] = useState<string | null>(null);
  const [newsSummary, setNewsSummary] = useState<string | null>(null);
  const [summariesLoading, setSummariesLoading] = useState(true);
  const [summariesError, setSummariesError] = useState<string | null>(null);

  // Search states
  const [query, setQuery] = useState("");
  const [intent, setIntent] = useState<"grants" | "papers" | "news" | "all">("all");
  const [searchData, setSearchData] = useState<ResearchResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Mind map states
  const [showMindMap, setShowMindMap] = useState(false);
  const [mindMapMarkdown, setMindMapMarkdown] = useState<string>("");
  const [mindMapLoading, setMindMapLoading] = useState(false);
  const [mindMapError, setMindMapError] = useState<string | null>(null);

  // Load dashboard data on mount
  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setDashboardLoading(true);
        setDashboardError(null);
        setSummariesLoading(true);
        setSummariesError(null);

        // Fetch initial data for "Musculoskeletal"
        const result = await fetchInbox(dashboardQuery, "all");
        setDashboardData(result);

        // Generate summaries for each sector with lab profile
        const summaryPromises = [
          generateSummary(result.grants, "grants", LAB_PROFILE)
            .then(setGrantsSummary)
            .catch((err) => {
              console.error("Grants summary error:", err);
              setSummariesError(err instanceof Error ? err.message : "Failed to generate grants summary");
            }),
          generateSummary(result.papers, "papers", LAB_PROFILE)
            .then(setPapersSummary)
            .catch((err) => {
              console.error("Papers summary error:", err);
              setSummariesError(err instanceof Error ? err.message : "Failed to generate papers summary");
            }),
          generateSummary(result.news, "news", LAB_PROFILE)
            .then(setNewsSummary)
            .catch((err) => {
              console.error("News summary error:", err);
              setSummariesError(err instanceof Error ? err.message : "Failed to generate news summary");
            }),
        ];

        await Promise.all(summaryPromises);
      } catch (err) {
        setDashboardError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setDashboardLoading(false);
        setSummariesLoading(false);
      }
    };

    loadDashboard();
  }, [dashboardQuery]);

  const handleSearch = async () => {
    if (!query.trim()) {
      setSearchError("Please enter a search query");
      return;
    }

    try {
      setSearchLoading(true);
      setSearchError(null);
      setHasSearched(true);
      // Reset mind map state for new search
      setShowMindMap(false);
      setMindMapMarkdown("");
      setMindMapError(null);
      const result = await fetchInbox(query.trim(), intent);
      setSearchData(result);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : "Failed to fetch results");
      setSearchData(null);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClear = () => {
    setQuery("");
    setIntent("all");
    setSearchData(null);
    setSearchError(null);
    setHasSearched(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  // Generate mind map from current data
  const handleGenerateMindMap = async (data: ResearchResponse, queryText: string) => {
    try {
      setMindMapLoading(true);
      setMindMapError(null);
      
      const result = await generateMindMap(
        data.grants,
        data.papers,
        data.news,
        queryText,
        true // use AI
      );
      
      setMindMapMarkdown(result.markdown);
      setShowMindMap(true);
    } catch (err) {
      setMindMapError(err instanceof Error ? err.message : "Failed to generate mind map");
    } finally {
      setMindMapLoading(false);
    }
  };

  // Toggle mind map visibility (uses search results data)
  const handleToggleMindMap = () => {
    if (!showMindMap && searchData) {
      // Generate mind map if not already loaded
      if (!mindMapMarkdown && !mindMapLoading) {
        handleGenerateMindMap(searchData, searchData.user_query);
      } else {
        setShowMindMap(true);
      }
    } else {
      setShowMindMap(false);
    }
  };

  // Refresh mind map
  const handleRefreshMindMap = () => {
    if (searchData) {
      handleGenerateMindMap(searchData, searchData.user_query);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden">
      {/* Animated gradient background orbs */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div 
          className="absolute top-0 -left-1/4 w-[800px] h-[800px] bg-gradient-to-br from-teal-500/25 via-cyan-400/20 to-teal-400/25 rounded-full blur-3xl" 
          style={{ animation: 'pulse-slow 4s ease-in-out infinite' }}
        />
        <div 
          className="absolute top-1/3 -right-1/4 w-[700px] h-[700px] bg-gradient-to-br from-cyan-500/25 via-teal-400/20 to-cyan-400/25 rounded-full blur-3xl" 
          style={{ animation: 'pulse-slow-delay-1 5s ease-in-out infinite 1s' }}
        />
        <div 
          className="absolute bottom-0 left-1/3 w-[600px] h-[600px] bg-gradient-to-br from-teal-400/20 via-cyan-400/25 to-teal-300/20 rounded-full blur-3xl" 
          style={{ animation: 'pulse-slow-delay-2 6s ease-in-out infinite 2s' }}
        />
      </div>

      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-100">Research Dashboard</h1>
              <p className="mt-2 text-slate-400">
                Funding opportunities, research papers, and news relevant to your research lab
              </p>
            </div>
            <div className="flex items-center gap-4 flex-wrap">
              {/* User Account Section */}
              <div className="flex items-center gap-3 rounded-xl border border-slate-800/50 bg-slate-900/80 backdrop-blur-sm px-4 py-2">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-teal-400" />
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-slate-200">Signed in as {USER_INFO.name}</span>
                    <a
                      href={USER_INFO.lab_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-slate-400 hover:text-teal-400 transition-colors"
                    >
                      {USER_INFO.lab_name}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              </div>
              <Button asChild variant="outline" className="border-slate-700 bg-slate-900/80 hover:bg-slate-800/80 hover:border-teal-500/50">
                <Link href="/">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Home
                </Link>
              </Button>
            </div>
          </div>

          {/* Dashboard Error Display */}
          {dashboardError && (
            <div className="mb-8">
              <ErrorAlert message={dashboardError} />
            </div>
          )}

          {/* Grants Section */}
          <div className="mb-12">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-100 mb-4">Funding Opportunities</h2>
            
            {summariesLoading || dashboardLoading ? (
              <div className="space-y-4 mb-6">
                <Skeleton className="h-20 w-full bg-slate-800/50" />
                <Skeleton className="h-64 w-full bg-slate-800/50" />
              </div>
            ) : (
              <>
                {grantsSummary && (
                  <div className="rounded-xl border border-slate-800/50 bg-slate-900/60 backdrop-blur-sm p-6 mb-6">
                    <p className="text-base leading-relaxed text-slate-300 max-w-4xl">
                      {grantsSummary}
                    </p>
                  </div>
                )}
                {summariesError && (
                  <div className="mb-4">
                    <ErrorAlert message={summariesError} />
                  </div>
                )}
                {dashboardData && dashboardData.grants.length > 0 ? (
                  <ResearchCarousel items={dashboardData.grants} />
                ) : (
                  <p className="text-slate-400 py-8">No grants found.</p>
                )}
              </>
            )}
          </div>

          <Separator className="my-8 bg-slate-800/50" />

          {/* Papers Section */}
          <div className="mb-12">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-100 mb-4">Research Papers</h2>
            
            {summariesLoading || dashboardLoading ? (
              <div className="space-y-4 mb-6">
                <Skeleton className="h-20 w-full bg-slate-800/50" />
                <Skeleton className="h-64 w-full bg-slate-800/50" />
              </div>
            ) : (
              <>
                {papersSummary && (
                  <div className="rounded-xl border border-slate-800/50 bg-slate-900/60 backdrop-blur-sm p-6 mb-6">
                    <p className="text-base leading-relaxed text-slate-300 max-w-4xl">
                      {papersSummary}
                    </p>
                  </div>
                )}
                {dashboardData && dashboardData.papers.length > 0 ? (
                  <ResearchCarousel items={dashboardData.papers} />
                ) : (
                  <p className="text-slate-400 py-8">No papers found.</p>
                )}
              </>
            )}
          </div>

          <Separator className="my-8 bg-slate-800/50" />

          {/* News Section */}
          <div className="mb-12">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-100 mb-4">Latest News</h2>
            
            {summariesLoading || dashboardLoading ? (
              <div className="space-y-4 mb-6">
                <Skeleton className="h-20 w-full bg-slate-800/50" />
                <Skeleton className="h-64 w-full bg-slate-800/50" />
              </div>
            ) : (
              <>
                {newsSummary && (
                  <div className="rounded-xl border border-slate-800/50 bg-slate-900/60 backdrop-blur-sm p-6 mb-6">
                    <p className="text-base leading-relaxed text-slate-300 max-w-4xl">
                      {newsSummary}
                    </p>
                  </div>
                )}
                {dashboardData && dashboardData.news.length > 0 ? (
                  <ResearchCarousel items={dashboardData.news} />
                ) : (
                  <p className="text-slate-400 py-8">No news found.</p>
                )}
              </>
            )}
          </div>

          <Separator className="my-8 bg-slate-800/50" />

          {/* Search Section */}
          <div className="mb-8">
            <Card className="border-slate-800/50 bg-slate-900/60 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-slate-100">Search Research Data</CardTitle>
                <CardDescription className="text-slate-400">
                  Explore additional grants, papers, and news with custom queries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-4 sm:flex-row">
                  <div className="flex-1">
                    <Input
                      placeholder="Enter your search query (e.g., 'machine learning healthcare')"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="w-full bg-slate-800/50 border-slate-700 text-slate-100 placeholder:text-slate-500 focus:border-teal-500/50"
                    />
                  </div>
                  <div className="w-full sm:w-48">
                    <Select value={intent} onValueChange={(value: typeof intent) => setIntent(value)}>
                      <SelectTrigger className="bg-slate-800/50 border-slate-700 text-slate-100">
                        <SelectValue placeholder="Select intent" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="all">All Sources</SelectItem>
                        <SelectItem value="grants">Grants Only</SelectItem>
                        <SelectItem value="papers">Papers Only</SelectItem>
                        <SelectItem value="news">News Only</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      onClick={handleSearch} 
                      disabled={searchLoading} 
                      className="flex-1 sm:flex-initial bg-teal-500 hover:bg-teal-400 text-slate-950"
                    >
                      <Search className="mr-2 h-4 w-4" />
                      {searchLoading ? "Searching..." : "Search"}
                    </Button>
                    {hasSearched && (
                      <Button 
                        onClick={handleClear} 
                        variant="outline" 
                        size="icon"
                        className="border-slate-700 hover:bg-slate-800"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search Error Display */}
          {searchError && (
            <div className="mb-8">
              <ErrorAlert message={searchError} />
            </div>
          )}

          {/* Search Loading State */}
          {searchLoading && <LoadingSkeleton />}

          {/* Search Results Display */}
          {!searchLoading && searchData && (
            <div className="space-y-8">
              {/* Results Summary */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-4">
                  <div>
                    <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-100">Search Results</h2>
                    <p className="text-sm text-slate-400 mt-1">
                      Query: &quot;{searchData.user_query}&quot; | Intent: {searchData.intent || "all"}
                    </p>
                  </div>
                  {/* Mind Map Toggle Button */}
                  <Button
                    onClick={handleToggleMindMap}
                    variant={showMindMap ? "default" : "outline"}
                    disabled={mindMapLoading}
                    size="sm"
                    className={showMindMap 
                      ? "bg-teal-500 hover:bg-teal-400 text-slate-950" 
                      : "border-slate-700 bg-slate-900/80 hover:bg-slate-800/80 hover:border-teal-500/50"
                    }
                  >
                    <Network className="mr-2 h-4 w-4" />
                    {mindMapLoading ? "Generating..." : showMindMap ? "Hide Mind Map" : "Show Mind Map"}
                  </Button>
                </div>
                <div className="ml-auto flex flex-wrap gap-2">
                  {searchData.grants.length > 0 && (
                    <Badge variant="secondary" className="bg-teal-500/20 text-teal-300 border-teal-500/30">
                      {searchData.grants.length} Grant{searchData.grants.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                  {searchData.papers.length > 0 && (
                    <Badge variant="secondary" className="bg-cyan-500/20 text-cyan-300 border-cyan-500/30">
                      {searchData.papers.length} Paper{searchData.papers.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                  {searchData.news.length > 0 && (
                    <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
                      {searchData.news.length} News Item{searchData.news.length !== 1 ? "s" : ""}
                    </Badge>
                  )}
                </div>
              </div>

              {/* Mind Map Section */}
              {(showMindMap || mindMapLoading) && (
                <div className="mb-8">
                  <MindMap
                    markdown={mindMapMarkdown}
                    loading={mindMapLoading}
                    error={mindMapError}
                    onRefresh={handleRefreshMindMap}
                  />
                </div>
              )}

              {/* Errors from API */}
              {searchData.errors && searchData.errors.length > 0 && (
                <ErrorAlert
                  title="API Errors"
                  message={searchData.errors.join(", ")}
                />
              )}

              {/* Separate Sections by Type */}
              {searchData.grants.length > 0 && (
                <div>
                  <h3 className="mb-4 text-xl font-semibold text-slate-100">Grants</h3>
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {searchData.grants.map((grant) => (
                      <ResearchCard key={grant.id} card={grant} />
                    ))}
                  </div>
                </div>
              )}

              {searchData.papers.length > 0 && (
                <div>
                  <h3 className="mb-4 text-xl font-semibold text-slate-100">Papers</h3>
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {searchData.papers.map((paper) => (
                      <ResearchCard key={paper.id} card={paper} />
                    ))}
                  </div>
                </div>
              )}

              {searchData.news.length > 0 && (
                <div>
                  <h3 className="mb-4 text-xl font-semibold text-slate-100">News</h3>
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {searchData.news.map((newsItem) => (
                      <ResearchCard key={newsItem.id} card={newsItem} />
                    ))}
                  </div>
                </div>
              )}

              {/* No Results */}
              {searchData.grants.length === 0 && 
               searchData.papers.length === 0 && 
               searchData.news.length === 0 && (
                <Card className="border-slate-800/50 bg-slate-900/60 backdrop-blur-sm">
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <p className="text-lg text-slate-400">No results found</p>
                    <p className="mt-2 text-sm text-slate-500">
                      Try a different search query or intent
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Empty Search State */}
          {!searchLoading && !hasSearched && !searchError && (
            <Card className="border-slate-800/50 bg-slate-900/60 backdrop-blur-sm">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Search className="mb-4 h-12 w-12 text-slate-600" />
                <p className="text-lg font-medium text-slate-300">Ready to search</p>
                <p className="mt-2 text-sm text-slate-500">
                  Enter a query above to find additional research opportunities
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  );
}
