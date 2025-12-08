import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function LoginPage({ onLogin, loading, error }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-900 via-slate-900 to-blue-800 text-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-12">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="leading-tight">
              <h1 className="text-2xl font-semibold">CA Document Manager</h1>
            </div>
          </div>
          <div className="hidden items-center gap-3 text-sm font-medium text-sky-50/80 sm:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-300 animate-pulse" />
            Secure Autodesk sign-in
          </div>
        </header>

        <div className="grid gap-10 lg:grid-cols-2 lg:items-center">

          <Card className="border-white/15 bg-white/10 text-white shadow-xl shadow-slate-900/30 backdrop-blur-lg">
            <CardContent className="space-y-6 p-8">
              <div>
                <p className="text-sm uppercase tracking-[0.14em] text-sky-100/80">Autodesk Sign-in</p>
                <h3 className="text-2xl font-semibold">Login to continue</h3>
              </div>

              <div className="space-y-3">
                <p className="text-xs text-sky-100/70">
                  You&apos;ll be redirected to Autodesk to approve the connection.
                </p>
              </div>

              {error ? (
                <div className="rounded-lg border border-rose-200/50 bg-rose-50/10 px-4 py-3 text-sm text-rose-50">
                  {error}
                </div>
              ) : null}

              <Button
                size="lg"
                className="w-full rounded-xl bg-white text-slate-900 hover:bg-slate-100"
                onClick={onLogin}
                disabled={loading}
              >
                {loading ? "Connecting…" : "Continue with Autodesk"}
              </Button>

              <div className="flex items-center justify-between text-xs text-sky-100/70">
                <span>Secure OAuth 2.0 flow</span>
                <span>Token stored locally</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
