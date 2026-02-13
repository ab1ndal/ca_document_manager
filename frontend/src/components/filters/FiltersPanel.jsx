import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";

const INCREMENTS = ["INC 1", "INC 2", "INC 3", "INC 4", "INC 5", "INC 6", "Custom Search"];

function FiltersPanel({ filters, setFilters, search, loadingResults }) {
  return (
    <div className="flex flex-col gap-5">
      <div className="space-y-2">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">Increment</p>
        <Select
          value={filters.increment ?? "Custom Search"}
          onValueChange={(v) => setFilters((p) => ({ ...p, increment: v }))}
        >
          <SelectTrigger className="bg-white/90">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {INCREMENTS.map((inc) => (
              <SelectItem key={inc} value={inc}>
                {inc}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">Search</p>
        <Input
          placeholder="Search RFIs"
          className="bg-white/90"
          value={filters.searchText}
          onChange={(e) =>
            setFilters((p) => ({ ...p, searchText: e.target.value }))
          }
        />
      </div>

      <div className="space-y-2">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">Updated After (PT)</p>
        <Input
          type="datetime-local"
          className="bg-white/90"
          value={filters.updatedAfter || ""}
          onChange={(e) =>
            setFilters((p) => ({ ...p, updatedAfter: e.target.value }))
          }
        />
      </div>

      <div className="space-y-2">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">Assignee</p>
        <Select
          value={filters.assignee ?? "NYA Team"}
          onValueChange={(v) => setFilters((p) => ({ ...p, assignee: v }))}
        >
          <SelectTrigger className="bg-white/90">
            <SelectValue placeholder="Assignee" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="NYA Team">NYA Team</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button className="w-full shadow-sm" onClick={search} disabled={loadingResults}>
        {loadingResults ? "Searching..." : "Search RFIs"}
      </Button>
    </div>
  );
}

export default FiltersPanel;
