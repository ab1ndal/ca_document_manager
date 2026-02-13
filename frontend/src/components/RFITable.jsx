import React, { useMemo, useState } from 'react';
import { AllCommunityModule, ModuleRegistry, themeQuartz } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { Button } from "@/components/ui/button";

ModuleRegistry.registerModules([AllCommunityModule]);

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const RFITable = ({ data, fields, userMap, onGridReadyApi }) => {

  const handleGridReady = (params) => {
    onGridReadyApi?.(params.api);
  };

  const enabledFields = useMemo(() => {
  if (!Array.isArray(fields)) return [];
  return fields
    .filter((f) => f?.enabled)
    .slice()
    .sort((a, b) => Number(a?.order ?? 0) - Number(b?.order ?? 0));
}, [fields]);
  
  // Row colors
  const getRowStyle = (params) => {
    const status = (params.data.status || "").toLowerCase();
    if (!status) return null;
    if (status == "open"){
        return {background:'#ecfdf5'}
    }
    if (status === 'openrev1' || status === 'openrev2'){
        return {background: '#fffbeb'}
    }
    return null;
  }

  const formatValue = (value, field) => {
    if (value === undefined || value === null || value === '') {
      return '-';
    }

    const t = String(field?.type || 'string').toLowerCase();

    if (t === 'date' || t === 'datetime') {
      const d = new Date(value);
      if (Number.isNaN(d.getTime())) return String(value);
      return d.toLocaleDateString();
    }
    
    if (t === 'userid') return userMap[value] || `ID: ${value}`;
    if (t === 'number' || t === 'int') return Number(value);
    if (t === 'boolean') return value ? 'Yes' : 'No';
    return String(value);
  }

  const DownloadCell = (props) => {
    const { value } = props;
    const [loading, setLoading] = useState(false);

    if (!value) return <span>-</span>;

    const handleDownload = async () => {
      try {
        setLoading(true);
        const sessionId = localStorage.getItem("session_id");

        // Backend should return { url: "https://signed..." }
        const res = await fetch(`${API_BASE}/api/acc/signed-download`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Session-Id": sessionId,
          },
          body: JSON.stringify({
            storageUrn: value,
            // optional: displayName if you have it in row data
          }),
        });

        if (!res.ok) return;

        const data = await res.json();
        if (data?.url) {
          window.open(data.url, "_blank", "noopener,noreferrer");
        }
      } finally {
        setLoading(false);
      }
  };

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={handleDownload}
      disabled={loading}
    >
      {loading ? "Preparing..." : "Download"}
    </Button>
  );
};


  const ResponsesCell = (props) => {
    const { value, context } = props;

    const [expanded, setExpanded] = useState(false);

    if (!Array.isArray(value) || value.length === 0) return <span>-</span>;

    const toTime = (v) => {
      const d = new Date(v);
      return Number.isNaN(d.getTime()) ? 0 : d.getTime();
    };

    const bestTime = (obj) => Math.max(toTime(obj?.updatedAt), toTime(obj?.createdAt));

    const sorted = [...value].sort((a, b) => bestTime(b) - bestTime(a));

    const maxShown = expanded ? sorted.length : 2;
    const shown = sorted.slice(0, maxShown);

    const formatLine = (item) => {
      const timeRaw = item.updatedAt || item.createdAt;
      const time = timeRaw ? new Date(timeRaw).toLocaleDateString() : '';
      const createdBy = item.createdBy || '';
      const name = userMap[createdBy] || createdBy;
      const status = item.status || '';
      const text = item.text || '';

      return `${time ? `[${time}] ` : ''}${status ? `(${status}) ` : ''}${name ? `${name}: ` : ''}\n${text}`.trim();
    };

    return (
      <div style={{ whiteSpace: "pre-wrap", lineHeight: "1.4" }}>
        {shown.map((item, idx) => (
          <div key={idx} style={{ marginBottom: 8 }}>
            {formatLine(item)}
          </div>
        ))}

        {sorted.length > 2 && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            style={{
              fontSize: 12,
              color: "#2563eb",
              textDecoration: "underline",
              background: "transparent",
              border: "none",
              padding: 0,
              cursor: "pointer"
            }}
          >
            {expanded ? "Show less" : `Show ${sorted.length - 2} more`}
          </button>
        )}
      </div>
    );
  };


  const colDefs = useMemo(() => {
    return enabledFields.map((field) => {
      const key = field.key;
      const t = String(field?.type || "string").toLowerCase();

      const col = {
        field: key,
        headerName: field.label ?? key,
        filter: true,
        sortable: true,
        resizable: true,
        wrapText: true,
        autoHeight: true,
        flex: 1,
        minWidth: 140,
        cellStyle: { textAlign: "left" }
      };

      if (key === "question") {
        col.flex = 3;
        col.minWidth = 500;
      }

      if (key === "title") {
        col.flex = 2;
        col.minWidth = 300;
      }

      if (t === "array[object]") {
        col.cellRenderer = ResponsesCell;
        col.valueGetter = (p) => p.data?.[key]; // ensures renderer gets the array
        col.flex = 3;
        col.minWidth = 500;
        return col;
      }

      if (key === "virtualFolderUrn") {
        col.cellRenderer = DownloadCell;
        col.valueGetter = (p) => p.data?.[key];
        col.minWidth = 160;
        col.flex = 0;
        return col;
      }

      col.valueFormatter = (p) => formatValue(p.value, field);
      return col;
    });
  }, [enabledFields]);


  const rowSelection = useMemo(() => { 
    return { mode: 'singleRow' };
  }, []);

  // Default Column Definitions
  const defaultColDef = useMemo(() => ({
    sortable: true,
    resizable: true,
    filter: true,
    wrapText: true,
    autoHeight: true,
    headerClass: "justify-center", // <--- Centers the Header Text
    cellStyle: { wordBreak: 'normal', lineHeight: '1.6', paddingTop: '12px', paddingBottom: '12px', textAlign:'left', whiteSpace:'pre-wrap' } 
  }), []);

  // Inline styles for the Legend Dots (Bypasses Tailwind issues)
  const legendDotStyle = {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    display: 'inline-block',
    marginRight: '8px',
    flexShrink: 0 // Prevents dot from squishing
  };
  // Container for each legend item (Dot + Text)
  const legendItemStyle = {
    display: 'flex',
    alignItems: 'center',
    marginRight: '24px' // Space between legend groups
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-slate-400">
        No data to display
      </div>
    );
  }

  


  return (
    <div className="flex flex-col h-full gap-3">
      
      {/* 3. Legend Section */}
      <div className="flex flex-wrap items-center text-xs px-2 pt-2 border-b border-slate-100 pb-2 shrink-0">
        <span className="font-bold text-slate-700 uppercase tracking-wider" style={{ marginRight: '16px' }}>
          Legend:
        </span>
        
        {/* Item 1: Open */}
        <div style={legendItemStyle}>
          <span style={{...legendDotStyle, background: '#ecfdf5', border: '1px solid #6ee7b7'}}></span>
          <span className="text-slate-600">Open / New</span>
        </div>

        {/* Item 2: Revision */}
        <div style={legendItemStyle}>
          <span style={{...legendDotStyle, background: '#fffbeb', border: '1px solid #fcd34d'}}></span>
          <span className="text-slate-600">Revision Requested</span>
        </div>
      </div>
    
      {/* FIX: Changed from height:'100%' to className="flex-1". 
         This allows the grid to fill remaining space without pushing the Legend off-screen.
      */}
      <div className="h-full w-full overflow-hidden">
        <AgGridReact
          rowData={data}
          columnDefs={colDefs}
          defaultColDef={defaultColDef}
          enableCellTextSelection={true}
          ensureDomOrder={true}
          pagination={true}
          paginationPageSize={20}
          theme={themeQuartz}
          rowSelection={rowSelection}
          getRowStyle={getRowStyle}
          onGridReady={handleGridReady}
        />
      </div>
    </div>
  );
};

export default RFITable;