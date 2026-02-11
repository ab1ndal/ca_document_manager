import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ChevronLeft, ChevronRight, Settings } from "lucide-react";
import FiltersPanel from "@/components/filters/FiltersPanel";
import RFITable from "@/components/RFITable";
import ExportButton from "@/components/ExportButton";
import ConfigTab from "@/components/ConfigTab";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const DEFAULT_INCREMENT = "Custom Search";

const getDefaultIncrementConfig = () => ({
  searchTerm: "",
  fields: [
    { key: "customIdentifier", label: "RFI Number", order: 1, enabled: true },
    { key: "title", label: "Title", order: 2, enabled: true },
    { key: "question", label: "Question", order: 3, enabled: true },
    { key: "status", label: "Status", order: 4, enabled: true },
    { key: "createdAt", label: "Created At", order: 5, enabled: true },
    { key: "dueDate", label: "Due Date", order: 6, enabled: true }
  ]
});


export default function MainPage({
  isLoggedIn,
  onLogin,
  onLogout,
  loginInProgress,
  onAuthFailure
}) {
  const [results, setResults] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showConfig, setShowConfig] = useState(false);
  const [tableFields, setTableFields] = useState([]);
  const [allConfigs, setAllConfigs] = useState({});
  const [activeConfig, setActiveConfig] = useState(getDefaultIncrementConfig());
  const [filters, setFilters] = useState({
    searchText: "",
    updatedAfter: "",
    assignee: "NYA Team",
    limit: 200,
    increment: DEFAULT_INCREMENT
  });

  // Force light mode + soft background
  useEffect(() => {
    document.documentElement.classList.remove("dark");
    document.documentElement.style.backgroundColor = "#f7f9fc";
    loadTableConfig();
    return () => {
      document.documentElement.style.backgroundColor = "";
    };
  }, []);

  const loadTableConfig = async () => {
    try{
      // Set Session ID
      const sessionId = localStorage.getItem("session_id");
      // Get all configs
      const configRes = await fetch(`${API_BASE}/api/config/increments`, {
        headers: { "X-Session-Id": sessionId }
      });
      if (!configRes.ok) throw new Error("Backend API call failed");
      const data = await configRes.json();
      setAllConfigs(data || {});
    } catch (err) {
      console.error("Failed to load table config:", err);
    }
  };

  useEffect(() => {
    const inc = filters.increment || DEFAULT_INCREMENT;
    const cfg = allConfigs[inc] || getDefaultIncrementConfig();

    setActiveConfig(cfg);

    // Populate searchText initially from config searchTerm
    setFilters((prev) => ({
      ...prev,
      increment: inc,
      searchText: cfg.searchTerm || ""
    }));
    console.log("Active config:", cfg);
    console.log("Filters:", filters);
    setTableFields(cfg.fields || []);
  }, [filters.increment, allConfigs]);

  const handleConfigSave = () => {
    setShowConfig(false);
  };

  const handleSearch = async () => {
    try {
      const sessionId = localStorage.getItem("session_id");
      const fieldIds = (activeConfig.fields || [])
          .filter((f) => f.enabled)
          .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
          .map((f) => f.key);

      console.log("Field IDs:", fieldIds);
      const res = await fetch(`${API_BASE}/api/rfis`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-Id": sessionId },
        body: JSON.stringify({ ...filters, fields: fieldIds })
      });

      if (res.status === 401 || res.status === 403) {
        onAuthFailure?.();
        return;
      }

      if (!res.ok) {
        throw new Error("Unable to fetch RFIs.");
      }

      const data = await res.json();
      console.log("Response data:", data);
      setResults(data.items || []);
    } catch (err) {
      console.error(err);
    }
  };

  if (showConfig) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white via-slate-50 to-sky-50 text-slate-900">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">
          <header className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white/80 px-6 py-4 shadow-sm backdrop-blur">
            <div className="flex items-center gap-3 leading-tight">
              <h1 className="text-xl font-semibold tracking-tight">Table Configuration</h1>
            </div>
            <Button variant="outline" onClick={() => setShowConfig(false)}>
              Back to Main
            </Button>
          </header>
          <div className="h-[calc(100vh-9rem)] relative">
            <ConfigTab 
              onSave={handleConfigSave}
              onCancel={() => setShowConfig(false)}
            />
          </div>
        </div>
      </div>
    );
  }


  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-slate-50 to-sky-50 text-slate-900">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-6">

        {/* TOP RIBBON */}
        <header className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white/80 px-6 py-4 shadow-sm backdrop-blur">
          <div className="flex items-center gap-3 leading-tight">
              <h1 className="text-xl font-semibold tracking-tight">CA Document Manager</h1>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => setShowConfig(true)}>
              <Settings className="mr-2 h-4 w-4" />
              Configure Table
            </Button>
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm shadow-inner">
              <span className={`h-2.5 w-2.5 rounded-full ${isLoggedIn ? "bg-emerald-500" : "bg-slate-300"}`} />
              <span className="font-medium">{isLoggedIn ? "Connected" : "Not connected"}</span>
            </div>

            {!isLoggedIn ? (
              <Button onClick={onLogin} disabled={loginInProgress} className="shadow-sm">
                {loginInProgress ? "Signing in..." : "Sign In"}
              </Button>
            ) : (
              <Button variant="outline" onClick={onLogout} className="shadow-sm">
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
          <main className="flex-1 min-w-0">
            <Card className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
              <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.08em] text-slate-400">Overview</p>
                  <CardTitle className="text-xl">RFI Results ({results.length})</CardTitle>
                </div>

                <div className="flex items-center gap-2">
                  <Button variant="outline" onClick={handleSearch} className="shadow-sm">
                    Refresh
                  </Button>
                  <ExportButton data={results} />
                </div>
              </CardHeader>

              <CardContent className="flex-1 p-0 overflow-hidden"> 
                 {/* 4. Render the Table if we have data, otherwise show placeholder */}
                 {results.length > 0 ? (
                    <div className="h-full w-full">
                       <RFITable data={results} fields={tableFields} />
                    </div>
                 ) : (
                    <div className="m-6 flex h-[calc(100%-3rem)] flex-col gap-4 rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-6 py-10 text-center text-sm text-slate-500 justify-center items-center">
                      <p className="text-base font-medium text-slate-700">RFIs will appear here</p>
                      <p className="text-sm text-slate-500">Run a search or refresh to pull the latest results.</p>
                    </div>
                 )}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </div>
  );
}
