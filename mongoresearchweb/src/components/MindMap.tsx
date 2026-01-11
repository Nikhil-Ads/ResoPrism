"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  Download, 
  RefreshCw,
  Loader2,
  AlertCircle,
  Network
} from "lucide-react";

// Custom styles for markmap to ensure text visibility on dark backgrounds
const markmapStyles = `
  /* Global text styling for dark theme */
  text {
    fill: #f1f5f9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }
  
  /* Root node (central topic) - larger and bolder */
  g[data-depth="0"] text {
    font-size: 15px !important;
    font-weight: 700 !important;
    fill: #ffffff !important;
  }
  
  /* Theme nodes - slightly larger */
  g[data-depth="1"] text {
    font-size: 14px !important;
    font-weight: 600 !important;
    fill: #f8fafc !important;
  }
  
  /* Category nodes (Grants, Papers, News) */
  g[data-depth="2"] text {
    font-size: 13px !important;
    font-weight: 600 !important;
    fill: #e2e8f0 !important;
  }
  
  /* Leaf nodes - item details */
  g[data-depth="3"] text,
  g[data-depth="4"] text,
  g[data-depth="5"] text {
    font-size: 12px !important;
    font-weight: 500 !important;
    fill: #cbd5e1 !important;
  }
  
  /* Link/line styling */
  path.markmap-link {
    stroke-width: 2 !important;
    opacity: 0.8;
  }
  
  /* Circle nodes (expand/collapse) */
  circle {
    stroke-width: 2 !important;
  }
  
  /* Foreign object content (for HTML in nodes) */
  foreignObject {
    color: #f1f5f9 !important;
  }
  
  foreignObject * {
    color: inherit !important;
  }
`;

interface MindMapProps {
  markdown: string;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  className?: string;
}

export function MindMap({ 
  markdown, 
  loading = false, 
  error = null,
  onRefresh,
  className = ""
}: MindMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const markmapRef = useRef<unknown>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize and render markmap
  const renderMindMap = useCallback(async () => {
    if (!markdown || !svgRef.current) return;
    
    try {
      // Dynamic import to avoid SSR issues
      const { Transformer } = await import("markmap-lib");
      const { Markmap } = await import("markmap-view");
      
      const transformer = new Transformer();
      const { root } = transformer.transform(markdown);
      
      // Clear previous content
      svgRef.current.innerHTML = "";
      
      // Create markmap instance with enhanced styling for dark theme
      const mm = Markmap.create(svgRef.current, {
        autoFit: true,
        duration: 500,
        maxWidth: 280,
        color: (node: { state?: { depth?: number } }) => {
          const depth = node.state?.depth || 0;
          // Brighter, more vibrant colors for dark background
          const colors = [
            "#2dd4bf", // teal-400 - root (brightest)
            "#22d3ee", // cyan-400 - level 1
            "#38bdf8", // sky-400 - level 2
            "#818cf8", // indigo-400 - level 3
            "#a78bfa", // violet-400 - level 4
            "#c084fc", // purple-400 - level 5+
          ];
          return colors[Math.min(depth, colors.length - 1)];
        },
        paddingX: 20,
        spacingVertical: 8,
        spacingHorizontal: 100,
      }, root);
      
      // Apply custom styles for text visibility
      const styleElement = document.createElement('style');
      styleElement.textContent = markmapStyles;
      svgRef.current.prepend(styleElement);
      
      markmapRef.current = mm;
      setIsInitialized(true);
      
      // Fit to view after a short delay
      setTimeout(() => {
        if (mm && typeof mm.fit === 'function') {
          mm.fit();
        }
      }, 100);
      
    } catch (err) {
      console.error("Error rendering mindmap:", err);
    }
  }, [markdown]);

  useEffect(() => {
    renderMindMap();
  }, [renderMindMap]);

  // Handle fullscreen toggle
  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  // Handle zoom
  const handleZoom = (direction: "in" | "out") => {
    const mm = markmapRef.current as { rescale?: (scale: number) => void };
    if (mm && typeof mm.rescale === 'function') {
      const scale = direction === "in" ? 1.25 : 0.8;
      mm.rescale(scale);
    }
  };

  // Handle fit to view
  const handleFit = () => {
    const mm = markmapRef.current as { fit?: () => void };
    if (mm && typeof mm.fit === 'function') {
      mm.fit();
    }
  };

  // Handle download as SVG
  const handleDownload = () => {
    if (!svgRef.current) return;
    
    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const blob = new Blob([svgData], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = "mindmap.svg";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Loading state
  if (loading) {
    return (
      <Card className={`${className}`}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Network className="h-5 w-5 text-teal-500" />
            Mind Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-[500px] bg-slate-50 dark:bg-slate-900 rounded-lg">
            <Loader2 className="h-12 w-12 text-teal-500 animate-spin mb-4" />
            <p className="text-muted-foreground">Analyzing research results...</p>
            <p className="text-sm text-muted-foreground mt-1">Finding themes and connections</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card className={`${className}`}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Network className="h-5 w-5 text-teal-500" />
            Mind Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-[500px] bg-slate-50 dark:bg-slate-900 rounded-lg">
            <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
            <p className="text-red-500 font-medium">Failed to generate mind map</p>
            <p className="text-sm text-muted-foreground mt-1 text-center max-w-md">{error}</p>
            {onRefresh && (
              <Button onClick={onRefresh} variant="outline" className="mt-4">
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Empty state
  if (!markdown) {
    return (
      <Card className={`${className}`}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Network className="h-5 w-5 text-teal-500" />
            Mind Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-[500px] bg-slate-50 dark:bg-slate-900 rounded-lg">
            <Network className="h-12 w-12 text-slate-400 mb-4" />
            <p className="text-muted-foreground">No data to visualize</p>
            <p className="text-sm text-muted-foreground mt-1">Search for research to generate a mind map</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${className}`} ref={containerRef}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Network className="h-5 w-5 text-teal-500" />
          Research Mind Map
        </CardTitle>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleZoom("in")}
            title="Zoom In"
            disabled={!isInitialized}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleZoom("out")}
            title="Zoom Out"
            disabled={!isInitialized}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleFit}
            title="Fit to View"
            disabled={!isInitialized}
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDownload}
            title="Download SVG"
            disabled={!isInitialized}
          >
            <Download className="h-4 w-4" />
          </Button>
          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onRefresh}
              title="Refresh"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div 
          className="mindmap-container w-full h-[600px] rounded-b-lg overflow-hidden"
          style={{ 
            position: 'relative',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
          }}
        >
          {/* Subtle grid pattern overlay */}
          <div 
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `radial-gradient(circle at 1px 1px, #94a3b8 1px, transparent 0)`,
              backgroundSize: '24px 24px',
            }}
          />
          <svg 
            ref={svgRef} 
            className="w-full h-full relative z-10"
            style={{
              width: '100%',
              height: '100%',
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
}

export default MindMap;
