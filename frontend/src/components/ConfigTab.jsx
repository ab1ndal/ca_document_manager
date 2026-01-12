import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { GripVertical, Save, RotateCcw } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const DEFAULT_FIELDS = [
  { id: "customIdentifier", label: "RFI Number", enabled: true },
  { id: "title", label: "Title", enabled: true },
  { id: "question", label: "Question", enabled: true },
  { id: "status", label: "Status", enabled: true },
  { id: "createdAt", label: "Created Date", enabled: true },
  { id: "dueDate", label: "Due Date", enabled: true },
  { id: "attachmentsCount", label: "Attachments", enabled: true }
];

export default function ConfigTab({ onSave, onCancel }) {
  const [fields, setFields] = useState([]);
  const [customAttributes, setCustomAttributes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draggedIndex, setDraggedIndex] = useState(null);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    setLoading(true);
    try {
      const sessionId = localStorage.getItem("session_id");
      
      // Load custom attributes from API
      const attrsRes = await fetch(`${API_BASE}/api/rfis/attributes`, {
        headers: { "X-Session-Id": sessionId }
      });

      console.log(attrsRes)
      
      if (attrsRes.ok) {
        const attrsData = await attrsRes.json();
        setCustomAttributes(attrsData.attributes || []);
      }

      // Load saved configuration
      const configRes = await fetch(`${API_BASE}/api/config/fields`, {
        headers: { "X-Session-Id": sessionId }
      });

      if (configRes.ok) {
        const config = await configRes.json();
        setFields(config.fields || DEFAULT_FIELDS);
      } else {
        setFields(DEFAULT_FIELDS);
      }
    } catch (err) {
      console.error("Failed to load configuration:", err);
      setFields(DEFAULT_FIELDS);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (fieldId) => {
    setFields(fields.map(f => 
      f.id === fieldId ? { ...f, enabled: !f.enabled } : f
    ));
  };

  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newFields = [...fields];
    const draggedItem = newFields[draggedIndex];
    newFields.splice(draggedIndex, 1);
    newFields.splice(index, 0, draggedItem);
    
    setFields(newFields);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const handleAddCustomAttribute = (attr) => {
    const newField = {
      id: `custom_${attr.id}`,
      label: attr.name,
      enabled: true,
      isCustom: true,
      customAttributeId: attr.id
    };
    setFields([...fields, newField]);
  };

  const handleRemoveField = (fieldId) => {
    setFields(fields.filter(f => f.id !== fieldId));
  };

  const handleSave = async () => {
    try {
      const sessionId = localStorage.getItem("session_id");
      const res = await fetch(`${API_BASE}/api/config/fields`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-Session-Id": sessionId 
        },
        body: JSON.stringify({ fields })
      });

      if (res.ok) {
        onSave(fields);
      }
    } catch (err) {
      console.error("Failed to save configuration:", err);
    }
  };

  const handleReset = () => {
    setFields(DEFAULT_FIELDS);
  };

  const availableCustomAttrs = customAttributes.filter(attr => 
    !fields.some(f => f.customAttributeId === attr.id)
  );

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-slate-500">Loading configuration...</p>
      </div>
    );
  }

  return (
    <div className="flex h-full gap-4">
      {/* Selected Fields - Left Panel */}
      <Card className="flex-1 rounded-2xl border border-slate-200 bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Table Fields Configuration</CardTitle>
          <p className="text-sm text-slate-500">
            Drag to reorder • Click checkbox to show/hide
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {fields.map((field, index) => (
            <div
              key={field.id}
              draggable
              onDragStart={() => handleDragStart(index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragEnd={handleDragEnd}
              className={`flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 transition-all hover:border-slate-300 hover:shadow-sm ${
                draggedIndex === index ? "opacity-50" : ""
              }`}
            >
              <GripVertical className="h-5 w-5 cursor-grab text-slate-400" />
              
              <Checkbox
                checked={field.enabled}
                onCheckedChange={() => handleToggle(field.id)}
              />
              
              <span className="flex-1 text-sm font-medium text-slate-700">
                {field.label}
                {field.isCustom && (
                  <span className="ml-2 text-xs text-slate-500">(Custom)</span>
                )}
              </span>

              {field.isCustom && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveField(field.id)}
                  className="text-rose-600 hover:text-rose-700"
                >
                  Remove
                </Button>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Available Custom Attributes - Right Panel */}
      <Card className="w-80 rounded-2xl border border-slate-200 bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Available Custom Attributes</CardTitle>
          <p className="text-sm text-slate-500">
            Click to add to table
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {availableCustomAttrs.length === 0 ? (
            <p className="text-center text-sm text-slate-500 py-4">
              No additional custom attributes available
            </p>
          ) : (
            availableCustomAttrs.map((attr) => (
              <button
                key={attr.id}
                onClick={() => handleAddCustomAttribute(attr)}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm font-medium text-slate-700 transition-all hover:border-blue-300 hover:bg-blue-50"
              >
                {attr.name}
              </button>
            ))
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="absolute bottom-6 right-6 flex gap-3">
        <Button variant="outline" onClick={handleReset}>
          <RotateCcw className="mr-2 h-4 w-4" />
          Reset to Default
        </Button>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button onClick={handleSave}>
          <Save className="mr-2 h-4 w-4" />
          Save Configuration
        </Button>
      </div>
    </div>
  );
}