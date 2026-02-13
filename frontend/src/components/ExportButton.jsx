// src/components/ExportButton.jsx
import React from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import ExcelJS from "exceljs";

const ExportButton = ({ data, fields, userMap }) => {
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
      const name = userMap?.[createdBy] || createdBy;
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

    if (t === "userid") return userMap?.[value] || String(value);

    if (t === "boolean") return value ? "Yes" : "No";

    if (t === "number" || t === "int") return String(Number(value));

    if (t === "array[object]") return formatResponsesForExport(value);

    return String(value);
  };

  const estimateWidth = (header, rows, key, fieldType) => {
    let maxLen = String(header || "").length;
    const sample = rows.slice(0, 50);
    for (const r of sample) {
      const v = formatCellForExport(r?.[key], fieldType);
      const firstLine = String(v).split("\n")[0];
      maxLen = Math.max(maxLen, firstLine.length);
    }
    // clamp
    return Math.min(Math.max(maxLen + 2, 12), 60);
  };

  const handleExport = async () => {
    if (!Array.isArray(data) || data.length === 0) return;

    const enabledFields = Array.isArray(fields)
      ? fields
          .filter((f) => f?.enabled)
          .slice()
          .sort((a, b) => Number(a?.order ?? 0) - Number(b?.order ?? 0))
      : [];

    if (enabledFields.length === 0) return;

    const headers = enabledFields.map((f) => f.label ?? f.key);

    const wb = new ExcelJS.Workbook();
    wb.creator = "CA Document Manager";
    wb.created = new Date();

    const ws = wb.addWorksheet("RFI Export", {
      views: [{ state: "frozen", ySplit: 1 }],
    });

    // Define columns with widths
    ws.columns = enabledFields.map((f, idx) => ({
      header: headers[idx],
      key: f.key,
      width: estimateWidth(headers[idx], data, f.key, f.type),
      style: { alignment: { wrapText: true, vertical: "top" } },
    }));

    // Header styling
    const headerRow = ws.getRow(1);
    headerRow.font = { bold: true };
    headerRow.alignment = { vertical: "middle" };
    headerRow.height = 20;

    // Add rows
    for (const row of data) {
      const values = {};
      for (const f of enabledFields) {
        values[f.key] = formatCellForExport(row?.[f.key], f.type);
      }
      ws.addRow(values);
    }

    // Make all data rows wrap + top align
    ws.eachRow((row, rowNumber) => {
      row.eachCell((cell) => {
        cell.alignment = { wrapText: true, vertical: "top" };
      });
      // give multi-line cells some breathing room
      if (rowNumber > 1) row.height = 18;
    });

    // Light header bottom border
    headerRow.eachCell((cell) => {
      cell.border = {
        bottom: { style: "thin", color: { argb: "FFE2E8F0" } },
      };
      cell.fill = {
        type: "pattern",
        pattern: "solid",
        fgColor: { argb: "FFF8FAFC" },
      };
    });

    const now = new Date();
    const datePart = now.toISOString().slice(0, 10);
    const timePart = now.toTimeString().slice(0, 5).replace(":", "-");
    const filename = `RFI_Export_${datePart}_${timePart}.xlsx`;

    const buffer = await wb.xlsx.writeBuffer();

    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Button
      variant="secondary"
      className="shadow-sm gap-2"
      onClick={handleExport}
      disabled={!data || data.length === 0}
    >
      <Download className="h-4 w-4" />
      Export Excel
    </Button>
  );
};

export default ExportButton;
