// src/components/ExportButton.jsx
import React from 'react';
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

const ExportButton = ({ data }) => {

  const handleExport = () => {
    if (!data || data.length === 0) {
      console.warn("No data to export");
      return;
    }

    // 1. Define Headers
    const headers = ["RFI #", "Title", "Question", "Status", "Created", "Due Date", "Latest Response"];

    // 2. Convert Data to CSV Rows
    const rows = data.map(item => {
      const safeText = (txt) => `"${(txt || "").replace(/"/g, '""')}"`; 
      const formatDate = (d) => d ? new Date(d).toLocaleDateString() : "";
      const getResponse = (r) => (r && r.length > 0) ? r[0].text : "";

      return [
        safeText(item.customIdentifier),
        safeText(item.title),
        safeText(item.question),
        safeText(item.status),
        safeText(formatDate(item.createdAt)),
        safeText(formatDate(item.dueDate)),
        safeText(getResponse(item.responses))
      ].join(",");
    });

    // 3. Combine and Download
    const csvBody = [headers.join(","), ...rows].join("\n");
    // Add BOM for Excel
    const csvContent = "\uFEFF" + csvBody;

    // Creates format: "RFI_Export_2025-12-09_13-45.csv"
    const now = new Date();
    const datePart = now.toISOString().slice(0, 10); // YYYY-MM-DD
    const timePart = now.toTimeString().slice(0, 5).replace(':', '-'); // HH-MM
    const filename = `RFI_Export_${datePart}_${timePart}.csv`;

    if (window.pywebview) {
        // DESKTOP MODE: Send data to Python
        // pywebview injects the 'pywebview' object automatically
        window.pywebview.api.save_file(csvContent, filename)
            .then(success => {
                if(success) console.log("File saved successfully via Python bridge");
            })
            .catch(err => console.error("Bridge Error:", err));
    } else {
        // BROWSER MODE: Standard Download
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
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