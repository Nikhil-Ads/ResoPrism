"use client";

export function Footer() {
  return (
    <footer className="relative border-t border-slate-800/50 bg-slate-950/80 backdrop-blur-xl px-6 py-8 z-10">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-center gap-4">
        <p className="text-sm text-slate-500">
          © {new Date().getFullYear()} MongoResearch. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
