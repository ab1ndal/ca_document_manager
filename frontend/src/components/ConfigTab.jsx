import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { 
  GripVertical, 
  Save, 
  RotateCcw, 
  ChevronDown, 
  ChevronRight,
  Info
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const INCREMENTS = ["INC 1", "INC 2", "INC 3", "INC 4", "INC 5", "INC 6", "Custom Search"];
const DEFAULT_FIELDS = [
  { key: "customIdentifier", label: "RFI Number", order: 1, enabled: true, type: "string" },
  { key: "title", label: "Title", order: 2, enabled: true, type: "string" },
  { key: "question", label: "Question", order: 3, enabled: true, type: "string" },
  { key: "status", label: "Status", order: 4, enabled: true, type: "string" },
  { key: "createdAt", label: "Created At", order: 5, enabled: true, type: "datetime" },
  { key: "dueDate", label: "Due Date", order: 6, enabled: true, type: "datetime" }
];

export default function ConfigTab({ onSave, onCancel }) {
  const [selectedIncrement, setSelectedIncrement] = useState("Custom Search");
  const [allAttributes, setAllAttributes] = useState([]);
  const [configs, setConfigs] = useState({});
  const [currentConfig, setCurrentConfig] = useState({
    searchTerm: "",
    fields: DEFAULT_FIELDS
  });
  const [expandedCategories, setExpandedCategories] = useState({
    core: true,
    dates: false,
    people: false,
    workflow: false,
    attachments: false,
    responses: false,
    customAttributes: true
  });
  const [loading, setLoading] = useState(true);
  const [draggedIndex, setDraggedIndex] = useState(null);
  
  useEffect(() => {
    loadConfiguration();
  }, []);

  useEffect(() => {
    // Load config for selected increment
    if (configs[selectedIncrement]) {
      setCurrentConfig(configs[selectedIncrement]);
    } else {
      setCurrentConfig({
        searchTerm: "",
        fields: DEFAULT_FIELDS
      });
    }
  }, [selectedIncrement, configs]);

  const loadConfiguration = async () => {
    setLoading(true);
    try {
      const sessionId = localStorage.getItem("session_id");
      
      // Load custom attributes from API
      const attrsRes = await fetch(`${API_BASE}/api/rfis/attributes`, {
        headers: { "X-Session-Id": sessionId }
      });

      const attrsData = await attrsRes.json();
      const attributes = Array.isArray(attrsData) ? attrsData : (attrsData.attributes || []);
      setAllAttributes(attributes);
      
      // Load all increment configs
      const configRes = await fetch(`${API_BASE}/api/config/increments`, {
        headers: { "X-Session-Id": sessionId }
      });

      if (configRes.ok) {
        const savedConfigs = await configRes.json();
        setConfigs(savedConfigs || {});
      }
    } catch (err) {
      console.error("Failed to load configuration:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const handleToggleField = (fieldKey) => {
    setCurrentConfig(prev => ({
      ...prev,
      fields: prev.fields.map(f => 
        f.key === fieldKey ? { ...f, enabled: !f.enabled } : f
      )
    }));
  };

  const handleAddField = (attribute) => {
    const maxOrder = Math.max(...currentConfig.fields.map(f => f.order), 0);
    const newField = {
      key: attribute.key,
      label: attribute.label,
      enabled: true,
      order: maxOrder + 1,
      type: attribute.type
    };
    
    setCurrentConfig(prev => ({
      ...prev,
      fields: [...prev.fields, newField]
    }));
  };

  const handleRemoveField = (fieldKey) => {
    setCurrentConfig(prev => ({
      ...prev,
      fields: prev.fields.filter(f => f.key !== fieldKey)
    }));
  };

  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newFields = [...currentConfig.fields];
    const draggedItem = newFields[draggedIndex];
    newFields.splice(draggedIndex, 1);
    newFields.splice(index, 0, draggedItem);
    
    // Update order property
    const reorderedFields = newFields.map((field, idx) => ({
      ...field,
      order: idx + 1
    }));
    
    setCurrentConfig(prev => ({ ...prev, fields: reorderedFields }));
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const handleSearchTermChange = (value) => {
    setCurrentConfig(prev => ({
      ...prev,
      searchTerm: value
    }));
  };

  const handleSave = async () => {
    try {
      const sessionId = localStorage.getItem("session_id");
      
      // Update configs with current increment
      const updatedConfigs = {
        ...configs,
        [selectedIncrement]: currentConfig
      };
      
      const res = await fetch(`${API_BASE}/api/config/increments`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-Session-Id": sessionId 
        },
        body: JSON.stringify({ configs: updatedConfigs })
      });

      if (res.ok) {
        setConfigs(updatedConfigs);
        onSave(updatedConfigs);
      }
    } catch (err) {
      console.error("Failed to save configuration:", err);
    }
  };

  const handleReset = () => {
    setCurrentConfig({
      searchTerm: "",
      fields: DEFAULT_FIELDS
    });
  };

  // Group attributes by category
  const groupedAttributes = allAttributes.reduce((acc, attr) => {
    const category = attr.category || 'other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(attr);
    return acc;
  }, {});

  // Get available attributes (not already in fields)
  const selectedFieldKeys = new Set(currentConfig.fields.map(f => f.key));
  const availableByCategory = Object.entries(groupedAttributes).reduce((acc, [category, attrs]) => {
    const available = attrs.filter(attr => !selectedFieldKeys.has(attr.key));
    if (available.length > 0) {
      acc[category] = available;
    }
    return acc;
  }, {});

  const categoryLabels = {
    core: "Core Fields",
    dates: "Date Fields",
    people: "People Fields",
    workflow: "Workflow Fields",
    attachments: "Attachments",
    responses: "Responses",
    customAttributes: "Custom Attributes",
    other: "Other"
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-500">Loading configuration...</p>
        </div>
      </div>
    );
  }

 return (
    <div className="flex h-full flex-col gap-6 p-6 bg-slate-50">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Table Configuration</h1>
          <p className="text-sm text-slate-500 mt-1">
            Configure fields and search logic for each increment
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Label className="text-sm font-medium text-slate-700">Increment:</Label>
          <Select value={selectedIncrement} onValueChange={setSelectedIncrement}>
            <SelectTrigger className="w-48 bg-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {INCREMENTS.map(inc => (
                <SelectItem key={inc} value={inc}>{inc}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Search Term Section */}
      <Card className="border-blue-200 bg-blue-50/50">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <CardTitle className="text-base">Search Logic</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <Input
            placeholder='Example: "Foundation" OR ("Structural" AND NOT ("MEP"))'
            value={currentConfig.searchTerm}
            onChange={(e) => handleSearchTermChange(e.target.value)}
            className="bg-white font-mono text-sm"
          />
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="flex flex-1 gap-6 min-h-0">
        {/* Selected Fields - Left Panel */}
        <Card className="flex-1 flex flex-col border-slate-200 bg-white shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">Selected Fields ({currentConfig.fields.length})</CardTitle>
            <p className="text-sm text-slate-500">
              Drag to reorder • Uncheck to hide
            </p>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-2">
            {currentConfig.fields.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <p>No fields selected</p>
                <p className="text-xs mt-1">Add fields from the right panel</p>
              </div>
            ) : (
              currentConfig.fields.map((field, index) => (
                <div
                  key={field.key}
                  draggable
                  onDragStart={() => handleDragStart(index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragEnd={handleDragEnd}
                  className={`group flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 transition-all hover:border-blue-300 hover:shadow-md ${
                    draggedIndex === index ? "opacity-50 scale-95" : ""
                  }`}
                >
                  <GripVertical className="h-5 w-5 cursor-grab text-slate-400 group-hover:text-blue-600" />
                  
                  <Checkbox
                    checked={field.enabled}
                    onCheckedChange={() => handleToggleField(field.key)}
                  />
                  
                  <div className="flex-1">
                    <span className="ml-2 text-xs text-slate-400">
                      #{field.order} - {field.label}
                    </span>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveField(field.key)}
                    className="opacity-0 group-hover:opacity-100 text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                  >
                    Remove
                  </Button>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Available Attributes - Right Panel */}
        <Card className="w-96 flex flex-col border-slate-200 bg-white shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">Available Attributes</CardTitle>
            <p className="text-sm text-slate-500">
              Click to add to selected fields
            </p>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-2">
            {Object.keys(availableByCategory).length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <p>All attributes added</p>
              </div>
            ) : (
              Object.entries(availableByCategory).map(([category, attrs]) => (
                <Collapsible
                  key={category}
                  open={expandedCategories[category]}
                  onOpenChange={() => toggleCategory(category)}
                >
                  <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200">
                    <span>{categoryLabels[category] || category}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-normal text-slate-500">
                        {attrs.length}
                      </span>
                      {expandedCategories[category] ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </div>
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-2 space-y-1">
                    {attrs.map((attr) => (
                      <button
                        key={attr.key}
                        onClick={() => handleAddField(attr)}
                        className="w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-left text-sm text-slate-700 transition-all hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
                      >
                        <div className="font-medium">{attr.label}</div>
                      </button>
                    ))}
                  </CollapsibleContent>
                </Collapsible>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200">
        <div className="text-sm text-slate-500">
          Configuration for: <span className="font-semibold text-slate-700">{selectedIncrement}</span>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave} className="gap-2 bg-blue-600 hover:bg-blue-700">
            <Save className="h-4 w-4" />
            Save Configuration
          </Button>
        </div>
      </div>
    </div>
  );
}
