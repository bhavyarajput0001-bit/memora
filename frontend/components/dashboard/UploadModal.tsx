"use client";

import { useState, useRef, useEffect } from "react";
import { X, Upload, FileText, Image, Mail, Calendar as CalendarIcon, FileText as NotesFile, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";

type UploadType = "pdf" | "screenshot" | "email" | "calendar" | "notes";

interface UploadProps {
  isOpen: boolean;
  type: UploadType | null;
  onClose: () => void;
  onUploadComplete: () => void;
}

interface UploadState {
  files: File[];
  uploading: boolean;
  uploaded: boolean;
  error: string | null;
}

const UPLOAD_CONFIG: Record<UploadType, { title: string; description: string; accepted: string; icon: any }> = {
  pdf: { title: "Upload PDF", description: "Add PDF documents to build your memory", accepted: ".pdf", icon: FileText },
  screenshot: { title: "Upload Screenshot", description: "Add images and screenshots to your memory", accepted: "image/*", icon: Image },
  email: { title: "Connect Email", description: "Connect your Gmail or Outlook to index emails", accepted: "", icon: Mail },
  calendar: { title: "Connect Calendar", description: "Sync Google Calendar or Apple Calendar events", accepted: "", icon: CalendarIcon },
  notes: { title: "Connect Notes", description: "Connect Google Keep, Apple Notes, or Notion", accepted: "", icon: NotesFile },
};

export default function UploadModal({ isOpen, type, onClose, onUploadComplete }: UploadProps) {
  const [state, setState] = useState<UploadState>({ files: [], uploading: false, uploaded: false, error: null });
  const [apiKey, setApiKey] = useState("");
  const [connected, setConnected] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setState({ files: [], uploading: false, uploaded: false, error: null });
      setApiKey("");
      setConnected(false);
    }
  }, [isOpen, type]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setState(prev => ({ ...prev, files }));
  };

  const handleUpload = async () => {
    if (state.files.length === 0) return;
    
    setState(prev => ({ ...prev, uploading: true, error: null }));
    
    try {
      const promises = state.files.map(file => 
        api.ingestFile(file, { type: type || "document" })
      );
      
      const results = await Promise.all(promises);
      const allSuccess = results.every(r => r.success);
      
      if (allSuccess) {
        setState(prev => ({ ...prev, uploading: false, uploaded: true }));
        setTimeout(() => {
          onUploadComplete();
          onClose();
        }, 1500);
      } else {
        setState(prev => ({ ...prev, uploading: false, error: "Some files failed to upload" }));
      }
    } catch (error) {
      setState(prev => ({ ...prev, uploading: false, error: "Upload failed. Please try again." }));
    }
  };

  const handleConnect = async () => {
    setState(prev => ({ ...prev, uploading: true, error: null }));
    
    // Simulate connection
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setState(prev => ({ ...prev, uploading: false, uploaded: true }));
    setConnected(true);
    
    setTimeout(() => {
      onUploadComplete();
      onClose();
    }, 1500);
  };

  const config = type ? UPLOAD_CONFIG[type] : null;
  const Icon = config?.icon || Upload;

  return (
    <AnimatePresence>
      {isOpen && type && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/70 backdrop-blur-md z-[60]"
          />
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed glass-card modal z-[70]"
            style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 'min(90vw, 28rem)' }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-5 border-b border-white/5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/20 flex items-center justify-center">
                  <Icon size={20} className="text-cyan-400" />
                </div>
                <div>
                  <h2 className="font-semibold text-white text-lg">{config?.title}</h2>
                  <p className="text-xs text-slate-500">{config?.description}</p>
                </div>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-xl transition-all">
                <X size={18} className="text-slate-400" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {type === "pdf" || type === "screenshot" ? (
                /* File Upload View */
                <div className="space-y-4">
                  {!state.uploaded ? (
                    <>
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-white/10 rounded-2xl p-8 text-center cursor-pointer hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all group"
                      >
                        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                          <Upload size={28} className="text-slate-400 group-hover:text-cyan-400 transition-colors" />
                        </div>
                        <p className="text-slate-300 font-medium mb-1">
                          {state.files.length > 0 
                            ? `${state.files.length} file${state.files.length > 1 ? 's' : ''} selected`
                            : "Click to upload"
                          }
                        </p>
                        <p className="text-xs text-slate-500">
                          {type === "pdf" ? "PDF files up to 50MB" : "Images up to 20MB"}
                        </p>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept={config?.accepted}
                          multiple
                          onChange={handleFileSelect}
                          className="hidden"
                        />
                      </div>

                      {state.files.length > 0 && (
                        <div className="space-y-2">
                          {state.files.map((file, i) => (
                            <div key={i} className="flex items-center gap-3 p-3 bg-white/5 rounded-xl border border-white/5">
                              <div className="w-8 h-8 rounded-lg bg-cyan-500/15 border border-cyan-500/20 flex items-center justify-center">
                                <Icon size={14} className="text-cyan-400" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm text-slate-200 truncate">{file.name}</p>
                                <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                              </div>
                              <button
                                onClick={() => setState(prev => ({
                                  ...prev,
                                  files: prev.files.filter((_, idx) => idx !== i)
                                }))}
                                className="p-1.5 hover:bg-white/10 rounded-lg transition-all"
                              >
                                <X size={14} className="text-slate-500" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}

                      {state.error && (
                        <div className="flex items-center gap-2 text-rose-400 text-sm bg-rose-500/10 border border-rose-500/20 rounded-xl px-4 py-3">
                          <AlertCircle size={16} />
                          {state.error}
                        </div>
                      )}

                      <button
                        onClick={handleUpload}
                        disabled={state.files.length === 0 || state.uploading}
                        className="w-full px-4 py-3 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl font-medium hover:bg-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {state.uploading ? (
                          <>
                            <Loader2 size={16} className="animate-spin" />
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Upload size={16} />
                            Upload {state.files.length > 0 ? `${state.files.length} files` : ""}
                          </>
                        )}
                      </button>
                    </>
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                        <CheckCircle size={32} className="text-emerald-400" />
                      </div>
                      <p className="text-slate-200 font-medium mb-1">Upload Complete!</p>
                      <p className="text-sm text-slate-500">Your {type} has been processed and added to memory</p>
                    </div>
                  )}
                </div>
              ) : (
                /* Connection View for Email/Calendar/Notes */
                <div className="space-y-4">
                  {!connected ? (
                    <>
                      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/20 flex items-center justify-center">
                            <Icon size={20} className="text-cyan-400" />
                          </div>
                          <div>
                            <p className="text-slate-200 font-medium">Connect your {type}</p>
                            <p className="text-xs text-slate-500">Enter your API key to connect</p>
                          </div>
                        </div>
                        
                        <div className="space-y-3">
                          <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder={`Enter ${type} API key...`}
                            className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
                          />
                          
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            <CheckCircle size={12} className="text-emerald-500" />
                            <span>Securely encrypted connection</span>
                          </div>
                        </div>
                      </div>

                      {state.error && (
                        <div className="flex items-center gap-2 text-rose-400 text-sm bg-rose-500/10 border border-rose-500/20 rounded-xl px-4 py-3">
                          <AlertCircle size={16} />
                          {state.error}
                        </div>
                      )}

                      <button
                        onClick={handleConnect}
                        disabled={!apiKey || state.uploading}
                        className="w-full px-4 py-3 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl font-medium hover:bg-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {state.uploading ? (
                          <>
                            <Loader2 size={16} className="animate-spin" />
                            Connecting...
                          </>
                        ) : (
                          <>
                            <CheckCircle size={16} />
                            Connect {type.charAt(0).toUpperCase() + type.slice(1)}
                          </>
                        )}
                      </button>

                      <p className="text-xs text-slate-600 text-center">
                        Your API key is stored securely and never shared
                      </p>
                    </>
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                        <CheckCircle size={32} className="text-emerald-400" />
                      </div>
                      <p className="text-slate-200 font-medium mb-1">Connected Successfully!</p>
                      <p className="text-sm text-slate-500">Your {type} is now syncing with MEMORA</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}