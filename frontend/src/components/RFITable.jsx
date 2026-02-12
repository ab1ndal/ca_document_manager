import React, { useState, useMemo } from 'react';
import { AllCommunityModule, ModuleRegistry, themeQuartz } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';

ModuleRegistry.registerModules([AllCommunityModule]);

const RFITable = ({ data, fields }) => {

  const enabledFields = fields.filter(f => f.enabled);
  console.log(enabledFields);

  const columns = enabledFields.map(field => ({
    accessorKey: field.key,
    header: field.label,
    cell: ({ row }) => {
      const value = row.original[field.key];
      // Format value based on field type
      if (field.key.includes('Date') || field.includes('At')) {
        return value ? new Date(value).toLocaleDateString() : '-';
      }
      return value || '-';
    }
  }));
  
  // Row colors
  const getRowStyle = (params) => {
    const status = (params.data.status || "").toLowerCase();
    if (['open'].includes(status)){
        return {background:'#ecfdf5'}
    }
    if (['openrev1', 'openrev2'].includes(status)){
        return {background: '#fffbeb'}
    }
  }

  const [colDefs] = useState([
    { 
        field: "customIdentifier", 
        headerName: "RFI#", 
        width: 80, 
        filter: true, 
        pinned: 'left',
        cellClass: "font-bold text-slate-700" 
    },
    { 
        field: "title", 
        headerName: "Title", 
        flex: 2, 
        minWidth: 300, // Fixed typo (was minwidth)
        filter: true,
        cellStyle : {textAlign: 'left'}
        // Removed textAlign: center (defaults to Left)
    },
    { 
        field: "question", 
        headerName: "Question", 
        flex: 3, 
        minWidth: 500, // Fixed typo (was minwidth)
        filter: true,
        cellStyle : {textAlign: 'left'} 
        // Removed textAlign: center (defaults to Left)
    },
    { 
        field: "createdAt", 
        headerName: "Created", 
        width: 110, 
        valueFormatter: (p) => p.value ? new Date(p.value).toLocaleDateString() : '-' 
    },
    { 
        field: "dueDate", 
        headerName: "Due (per ACC)", 
        width: 140, 
        cellStyle: params => {
            if (!params.value) return null;
            const isOverdue = new Date(params.value) < new Date();
            return isOverdue ? { color: '#ef4444', fontWeight: '600' } : null;
        }, 
        valueFormatter: (p) => p.value ? new Date(p.value).toLocaleDateString() : '-' 
    },
    { 
        field: "attachmentsCount", 
        headerName: "Attachments", 
        width: 120, 
        cellStyle: { textAlign: 'center' } 
    },
    { 
      headerName: "Latest Response", 
      flex: 3,
      minWidth: 500, 
      valueGetter: (params) => {
        const res = params.data.responses;
        if (res && res.length > 0) {
            return res[0].text; 
        }
        return "";
      },
      cellStyle : {textAlign: 'left'},
      // Removed textAlign: center (defaults to Left)
    },
    { 
      field: "status", 
      headerName: "Status", 
      width: 150,
      valueFormatter: (p) => p.value,
      cellClass: "font-medium uppercase text-xs tracking-tight"
    }
  ]);

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
        />
      </div>
    </div>
  );
};

export default RFITable;