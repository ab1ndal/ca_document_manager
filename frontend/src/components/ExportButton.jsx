// src/components/ExportButton.jsx
import React from 'react';
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

const ExportButton = ({ data, fields, gridApi, userMap }) => {

  const toTime = (v) => {
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? 0 : d.getTime();
};

const bestTime = (obj) => Math.max(toTime(obj?.updatedAt), toTime(obj?.createdAt));

const formatResponsesForExport = (arr) => {
  if (!Array.isArray(arr) || arr.length === 0) return "-";
  const sorted = [...arr].sort((a, b) => bestTime(b) - bestTime(a));
  const lines = sorted.map((item) => {
    const timeRaw = item.updatedAt || item.createdAt;
    const time = timeRaw ? new Date(timeRaw).toLocaleDateString() : "";
    const createdBy = item.createdBy || "";
    const name = userMap[createdBy] || createdBy;
    const status = item.status || "";
    const text = item.text || "";
    return `${time ? `[${time}] ` : ""}${status ? `(${status}) ` : ""}${name ? `${name}: ` : ""}${text}`.trim();
  });
  return lines.join("\n\n");
};

const formatCellForExport = (value, fieldType) => {
  if (value === undefined || value === null || value === "") return "-";

  const t = String(fieldType || "string").toLowerCase();

  if (t === "date" || t === "datetime") {
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleDateString();
  }

  if (t === "userid") return userMap[value] || String(value);

  if (t === "boolean") return value ? "Yes" : "No";

  if (t === "number" || t === "int") return String(Number(value));

  if (t === "array[object]") return formatResponsesForExport(value);

  return String(value);
};

  const handleExport = () => {
  if (!data || data.length === 0) {
    console.warn("No data to export");
    return;
  }

  const now = new Date();
  const datePart = now.toISOString().slice(0, 10);
  const timePart = now.toTimeString().slice(0, 5).replace(":", "-");
  const filename = `RFI_Export_${datePart}_${timePart}.csv`;

  if (gridApi) {
    const enabledFields = Array.isArray(fields)
      ? fields.filter((f) => f?.enabled).slice().sort((a, b) => Number(a?.order ?? 0) - Number(b?.order ?? 0))
      : [];

    const typeByKey = {};
    for (const f of enabledFields) typeByKey[f.key] = f.type;

    gridApi.exportDataAsCsv({
      fileName: filename,
      prependContent: "\uFEFF",
      processHeaderCallback: (p) => p.column.getColDef().headerName || p.column.getColDef().field,
      processCellCallback: (p) => {
        const colDef = p.column.getColDef();
        const key = colDef.field;
        const fieldType = typeByKey[key];
        const raw = p.value;

        return formatCellForExport(raw, fieldType);
      }
    });

    return;
  }

  // Fallback: if gridApi not ready, you can keep your older manual export here if desired.
  console.warn("Grid not ready yet, cannot export formatted view.");
};


  return (
    <Button 
      variant="secondary" 
      className="shadow-sm gap-2"
      onClick={handleExport}
      disabled={!data || data.length === 0}
    >
      <Download className="h-4 w-4" />
      Export CSV
    </Button>
  );
};

export default ExportButton;