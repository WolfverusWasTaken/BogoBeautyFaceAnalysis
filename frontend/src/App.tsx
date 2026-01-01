import { useState } from "react";
import { Header } from "./components/Header";
import { Camera } from "./components/Camera";
import { Results } from "./components/Results";
import { analyzeFace } from "./api";
import type { ParsedResult } from "./api";
import "./App.css";

function App() {
  const [result, setResult] = useState<ParsedResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"camera" | "results">("camera");

  const handleCapture = async (blob: Blob) => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const analysisResult = await analyzeFace(blob);
      setResult(analysisResult);
      // Auto-switch to results on mobile after analysis
      setActiveTab("results");
    } catch (err) {
      console.error("Analysis error:", err);
      setError(
        err instanceof Error ? err.message : "Failed to analyze. Is the backend running?"
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <Header logoSrc="/assets/BB-Icon.jpg" />

      {/* Mobile Tab Navigation */}
      <div className="lg:hidden flex mx-4 mb-2 bg-[var(--card)] rounded-lg border border-[var(--border)] overflow-hidden">
        <button
          onClick={() => setActiveTab("camera")}
          className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === "camera"
              ? "bg-[var(--accent)] text-white"
              : "text-[var(--muted)] hover:text-[var(--text)]"
            }`}
        >
          Camera
        </button>
        <button
          onClick={() => setActiveTab("results")}
          className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === "results"
              ? "bg-[var(--accent)] text-white"
              : "text-[var(--muted)] hover:text-[var(--text)]"
            }`}
        >
          Results {result && "•"}
        </button>
      </div>

      {/* Desktop: Side by side | Mobile: Tabbed */}
      <main className="flex-1 min-h-0 px-4 pb-3">
        {/* Desktop Layout */}
        <div className="hidden lg:grid lg:grid-cols-2 gap-4 h-full">
          {/* Camera Section */}
          <section className="glass-card p-4 flex flex-col min-h-0">
            <h2 className="text-base font-semibold mb-2">Camera</h2>
            <div className="flex-1 min-h-0">
              <Camera onCapture={handleCapture} isAnalyzing={isAnalyzing} />
            </div>
          </section>

          {/* Results Section */}
          <section className="glass-card p-4 flex flex-col min-h-0 overflow-auto">
            <h2 className="text-base font-semibold mb-2">Analysis Results</h2>
            {error && (
              <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm mb-2">
                {error}
              </div>
            )}
            {!result && !error && (
              <div className="flex-1 flex items-center justify-center text-[var(--muted)]">
                <p className="text-sm">Capture your photo to see recommendations</p>
              </div>
            )}
            {result && <Results result={result} />}
          </section>
        </div>

        {/* Mobile Layout - Tabbed */}
        <div className="lg:hidden h-full">
          {activeTab === "camera" && (
            <section className="glass-card p-4 flex flex-col h-full">
              <Camera onCapture={handleCapture} isAnalyzing={isAnalyzing} />
            </section>
          )}

          {activeTab === "results" && (
            <section className="glass-card p-4 flex flex-col h-full overflow-auto">
              {error && (
                <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm mb-2">
                  {error}
                </div>
              )}
              {!result && !error && (
                <div className="flex-1 flex items-center justify-center text-[var(--muted)]">
                  <div className="text-center">
                    <p className="text-sm">No analysis yet</p>
                    <button
                      onClick={() => setActiveTab("camera")}
                      className="mt-2 text-[var(--accent)] text-sm underline"
                    >
                      Go to Camera
                    </button>
                  </div>
                </div>
              )}
              {result && <Results result={result} />}
            </section>
          )}
        </div>
      </main>

      {/* Footer - hidden on mobile */}
      <footer className="hidden sm:block text-center text-[var(--muted)] text-xs py-2 px-4 border-t border-[var(--border)]">
        Summer Micro Design Challenge 2025 — <span className="italic">Alexi George</span>
      </footer>
    </div>
  );
}

export default App;
