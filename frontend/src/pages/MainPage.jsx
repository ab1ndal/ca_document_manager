import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ChevronLeft, ChevronRight } from "lucide-react";
import FiltersPanel from "@/components/filters/FiltersPanel";

const API_BASE = "http://localhost:8000";

export default function MainPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginInProgress, setLoginInProgress] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);

  const [filters, setFilters] = useState({
    searchText: "",
    updatedAfter: "",
    assignee: "NYA Team",
    limit: 100
  });

  // Force light mode + soft background
  useEffect(() => {
    document.documentElement.classList.remove("dark");
    document.documentElement.style.backgroundColor = "#f7f9fc";
    return () => {
      document.documentElement.style.backgroundColor = "";
    };
  }, []);

  const handleLogin = async () => {
    try {
      setLoginInProgress(true);
      const res = await fetch(`${API_BASE}/api/login`, { method: "POST" });
      if (res.ok) {
        const statusRes = await fetch(`${API_BASE}/api/auth/status`);
        const statusData = await statusRes.json();
        setIsLoggedIn(Boolean(statusData.logged_in));
      }
    } finally {
      setLoginInProgress(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("aps_token");
    setIsLoggedIn(false);
  };

  const handleSearch = async () => {
    const res = await fetch(`${API_BASE}/api/rfis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filters)
    });
    const data = await res.json();
    console.log(data);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-slate-50 to-sky-50 text-slate-900">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">

        {/* TOP RIBBON */}
        <header className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white/80 px-6 py-4 shadow-sm backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-200 via-sky-200 to-indigo-200 text-base font-semibold text-slate-800 shadow-inner">
              CA
            </div>
            <div className="leading-tight">
              <h1 className="text-xl font-semibold tracking-tight">CA Document Manager</h1>
              <p className="text-sm text-slate-500">ACC RFI Dashboard</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm shadow-inner">
              <span className={`h-2.5 w-2.5 rounded-full ${isLoggedIn ? "bg-emerald-500" : "bg-slate-300"}`} />
              <span className="font-medium">{isLoggedIn ? "Connected" : "Not connected"}</span>
            </div>

            {!isLoggedIn ? (
              <Button onClick={handleLogin} disabled={loginInProgress} className="shadow-sm">
                {loginInProgress ? "Signing in..." : "Sign In"}
              </Button>
            ) : (
              <Button variant="outline" onClick={handleLogout} className="shadow-sm">
                Logout
              </Button>
            )}
          </div>
        </header>

        {/* MAIN LAYOUT */}
        <div className="flex h-[calc(100vh-9rem)] gap-4">

          {/* FILTERS */}
          <aside
            className={`relative shrink-0 transition-[width] duration-300 ease-out ${
              showSidebar ? "basis-[15%] min-w-[220px] max-w-[280px]" : "w-12"
            }`}
          >
            <div className="absolute -right-3 top-4 z-10">
              <Button
                variant="secondary"
                size="icon"
                className="rounded-full shadow-md"
                onClick={() => setShowSidebar((prev) => !prev)}
              >
                {showSidebar ? <ChevronLeft /> : <ChevronRight />}
              </Button>
            </div>

            {showSidebar ? (
              <div className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-700">Filters</p>
                  <p className="text-xs text-slate-500">Refine RFI results</p>
                </div>
                <div className="flex-1 overflow-y-auto p-4">
                  <FiltersPanel
                    filters={filters}
                    setFilters={setFilters}
                    onApply={handleSearch}
                  />
                </div>
              </div>
            ) : (
              <div className="h-full rounded-2xl border border-slate-200 bg-white shadow-sm" />
            )}
          </aside>

          {/* RESULTS */}
          <main className="flex-1">
            <Card className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
              <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.08em] text-slate-400">Overview</p>
                  <CardTitle className="text-xl">RFI Results</CardTitle>
                </div>

                <div className="flex items-center gap-2">
                  <Button variant="outline" onClick={handleSearch} className="shadow-sm">
                    Refresh
                  </Button>
                  <Button variant="secondary" className="shadow-sm">Export</Button>
                </div>
              </CardHeader>

              <CardContent className="flex-1">
                <div className="flex h-full flex-col gap-4 rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-6 py-10 text-center text-sm text-slate-500">
                  <p className="text-base font-medium text-slate-700">RFIs will appear on the right pane</p>
                  <p className="text-sm text-slate-500">Run a search or refresh to pull the latest results.</p>
                </div>
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </div>
  );
}
