import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const API_BASE = "http://localhost:8000"

function MainPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginInProgress, setLoginInProgress] = useState(false);

  const handleLogin = async () => {
    try{
        setLoginInProgress(true);
    const res = await fetch(`${API_BASE}/api/login`, {
        method: "POST"
      });

      if (!res.ok) {
        console.error("Login request failed");
        return;
      }

      // After backend finishes login, confirm status
      const statusRes = await fetch(`${API_BASE}/api/auth/status`);
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setIsLoggedIn(Boolean(statusData.logged_in));
      }
    } catch (err) {
      console.error("Login error", err);
    } finally {
      setLoginInProgress(false);
    }
  };

    useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/status`);
        if (!res.ok) return;
        const data = await res.json();
        setIsLoggedIn(Boolean(data.logged_in));
      } catch (err) {
        console.error("Auth status check failed", err);
      }
    };

    checkStatus();
  }, []);

return (
    <div className="app-container bg-gray-100">
      
      {/* Header */}
      <header className="app-header">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">
            CA Document Manager
          </h1>
          <p className="text-gray-600 text-sm">
            Autodesk Construction Cloud RFI Dashboard
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span
              className={`w-3 h-3 rounded-full ${
                isLoggedIn ? "bg-emerald-500" : "bg-gray-400"
              }`}
            />
            <span className="text-sm text-gray-700">
              {isLoggedIn ? "Connected to ACC" : "Not connected"}
            </span>
          </div>

          <Button
            onClick={handleLogin}
            disabled={isLoggedIn || loginInProgress}
            className="px-4"
          >
            {isLoggedIn
              ? "Signed in"
              : loginInProgress
              ? "Signing in..."
              : "Sign in"}
          </Button>
        </div>
      </header>

      <Separator />

      {/* Main content */}
      <main className="app-main-grid">
        {/* Filters panel */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="card-body-text">
              Search terms, project selection and date or time filters will be added here.
            </p>
          </CardContent>
        </Card>

        {/* Results panel */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">RFIs</CardTitle>
            <Button variant="secondary" disabled>
              Export to Excel
            </Button>
          </CardHeader>

          <CardContent>
            <div className="rounded-md border border-dashed border-gray-300 h-48 flex items-center justify-center text-gray-500">
              RFIs will appear here with AG Grid once connected.
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

export default MainPage;
