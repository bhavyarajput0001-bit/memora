"use client";

import { useEffect, useRef, useState } from "react";
import { Search, ZoomIn, ZoomOut, Maximize, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as d3 from "d3";

interface GraphNode {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

const TYPE_CONFIG: Record<string, { color: string; glow: string }> = {
  person: { color: "#10b981", glow: "rgba(16, 185, 129, 0.4)" },
  project: { color: "#06b6d4", glow: "rgba(6, 182, 212, 0.4)" },
  topic: { color: "#8b5cf6", glow: "rgba(139, 92, 246, 0.4)" },
  event: { color: "#f59e0b", glow: "rgba(245, 158, 11, 0.4)" },
  date: { color: "#ef4444", glow: "rgba(239, 68, 68, 0.4)" },
  fact: { color: "#ec4899", glow: "rgba(236, 72, 153, 0.4)" },
  source: { color: "#6366f1", glow: "rgba(99, 102, 241, 0.4)" },
};

export default function GraphPage() {
  const svgRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [links, setLinks] = useState<GraphLink[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const simulationRef = useRef<any>(null);

  // Load data from backend
  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/memory/graph");
        const data = await response.json();
        
        const graphNodes: GraphNode[] = [];
        const graphLinks: GraphLink[] = [];
        
        data.entities?.forEach((entity: any) => {
          graphNodes.push({
            id: `entity_${entity.id}`,
            label: entity.name,
            type: "person",
          });
        });
        
        data.projects?.forEach((project: any) => {
          graphNodes.push({
            id: `project_${project.id}`,
            label: project.name,
            type: "project",
          });
        });
        
        data.facts?.forEach((fact: any) => {
          const factId = `fact_${fact.id}`;
          graphNodes.push({
            id: factId,
            label: fact.subject || fact.predicate || "Fact",
            type: "fact",
          });
          
          if (fact.subject) {
            graphLinks.push({
              source: `entity_${fact.subject.toLowerCase().replace(/\s+/g, "_")}`,
              target: factId,
              type: "relates to",
            });
          }
        });
        
        if (graphNodes.length === 0) {
          const demoNodes: GraphNode[] = [
            { id: "atlas", label: "Project Atlas", type: "project" },
            { id: "rahul", label: "Rahul Verma", type: "person" },
            { id: "priya", label: "Priya Patel", type: "person" },
            { id: "karan", label: "Karan Mehta", type: "person" },
            { id: "aditi", label: "Aditi Sharma", type: "person" },
            { id: "backend", label: "Backend Migration", type: "topic" },
            { id: "demo", label: "Demo Prep", type: "event" },
            { id: "sep26", label: "Sep 26", type: "date" },
            { id: "conflict", label: "Deadline Conflict", type: "topic" },
            { id: "vendor", label: "Vendor Delay", type: "topic" },
          ];
          
          const demoLinks: GraphLink[] = [
            { source: "rahul", target: "atlas", type: "works on" },
            { source: "priya", target: "atlas", type: "works on" },
            { source: "karan", target: "atlas", type: "works on" },
            { source: "aditi", target: "atlas", type: "leads" },
            { source: "atlas", target: "backend", type: "has" },
            { source: "atlas", target: "demo", type: "has" },
            { source: "demo", target: "sep26", type: "on" },
            { source: "demo", target: "conflict", type: "blocked by" },
            { source: "conflict", target: "vendor", type: "caused by" },
          ];
          
          setNodes(demoNodes);
          setLinks(demoLinks);
        } else {
          setNodes(graphNodes);
          setLinks(graphLinks);
        }
      } catch (error) {
        console.error("Failed to load graph data:", error);
      }
    };
    
    loadData();
  }, []);

  // D3 Force Simulation
  useEffect(() => {
    if (nodes.length === 0 || !svgRef.current) return;

    const width = containerRef.current?.clientWidth || 800;
    const height = containerRef.current?.clientHeight || 600;

    // Create a mutable copy for d3 simulation
    const simNodes = nodes.map(n => ({ ...n }));
    const simLinks = links.map(l => ({ ...l }));

    const simulation = d3.forceSimulation(simNodes as any)
      .force("link", d3.forceLink(simLinks as any).id((d: any) => d.id).distance(120))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(50))
      .alphaDecay(0.02);

    simulationRef.current = simulation;

    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height]);

    svg.selectAll("*").remove();

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.2, 4])
      .on("zoom", (event: any) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom as any);

    const g = svg.append("g");

    // Draw links
    const link = g.append("g")
      .selectAll("line")
      .data(simLinks)
      .join("line")
      .attr("stroke", "#ffffff15")
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "4 2");

    // Draw link labels
    const linkLabel = g.append("g")
      .selectAll("text")
      .data(simLinks)
      .join("text")
      .attr("font-size", 9)
      .attr("fill", "#94a3b8")
      .attr("text-anchor", "middle")
      .attr("dy", -5)
      .text((d: any) => d.type);

    // Draw nodes
    const node = g.append("g")
      .selectAll("g")
      .data(simNodes)
      .join("g");

    // Add drag behavior
    const drag = d3.drag<any, any>()
      .on("start", (event: any, d: any) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x ?? 0;
        d.fy = d.y ?? 0;
      })
      .on("drag", (event: any, d: any) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on("end", (event: any, d: any) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });

    node.call(drag);

    // Node circles
    node.append("circle")
      .attr("r", (d: GraphNode) => d.type === "project" ? 28 : d.type === "person" ? 24 : 18)
      .attr("fill", (d: GraphNode) => `${TYPE_CONFIG[d.type]?.color || "#06b6d4"}20`)
      .attr("stroke", (d: GraphNode) => TYPE_CONFIG[d.type]?.color || "#06b6d4")
      .attr("stroke-width", 2)
      .attr("filter", "url(#glow)")
      .style("cursor", "pointer")
      .on("click", (event: any, d: GraphNode) => {
        event.stopPropagation();
        setSelectedNode(d);
      });

    // Node labels
    node.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", (d: GraphNode) => d.type === "project" ? 45 : 35)
      .attr("fill", "#e2e8f0")
      .attr("font-size", 11)
      .attr("font-weight", 500)
      .text((d: GraphNode) => d.label);

    // Simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      linkLabel
        .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
        .attr("y", (d: any) => (d.source.y + d.target.y) / 2);

      node.attr("transform", (d: GraphNode) => `translate(${d.x}, ${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [nodes, links]);

  // Apply search filter
  const filteredNodes = searchQuery
    ? nodes.filter(n => n.label.toLowerCase().includes(searchQuery.toLowerCase()))
    : nodes;

  const filteredLinks = searchQuery
    ? links.filter(l => {
        const sourceNode = nodes.find(n => n.id === l.source);
        const targetNode = nodes.find(n => n.id === l.target);
        return sourceNode?.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
               targetNode?.label.toLowerCase().includes(searchQuery.toLowerCase());
      })
    : links;

  return (
    <div className="h-full flex">
      {/* Graph Container */}
      <div ref={containerRef} className="flex-1 glass-card relative overflow-hidden">
        {/* Background grid */}
        <div className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px'
          }}
        />
        
        {/* Search bar */}
        <div className="absolute top-4 left-4 z-10">
          <div className="flex items-center gap-2 bg-[#0a0f1e]/90 backdrop-blur-xl border border-white/10 rounded-xl px-4 py-2.5">
            <Search size={16} className="text-slate-400" />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent text-sm text-slate-200 placeholder-slate-500 outline-none w-48"
            />
          </div>
        </div>

        {/* Zoom controls */}
        <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
          <button
            onClick={() => {
              if (svgRef.current) {
                d3.select(svgRef.current).transition().duration(300).call((selection: any, transform: any) => {
                  selection.call(d3.zoom().transform, d3.zoomIdentity.translate(400, 300).scale(1));
                });
              }
            }}
            className="p-2.5 bg-[#0a0f1e]/90 backdrop-blur-xl border border-white/10 rounded-xl text-slate-400 hover:text-slate-200 transition-all"
          >
            <Maximize size={16} />
          </button>
          <button
            onClick={() => {
              if (svgRef.current) {
                d3.select(svgRef.current).transition().duration(300).call((selection: any, k: number) => {
                  selection.call(d3.zoom().scaleBy, 1.5);
                });
              }
            }}
            className="p-2.5 bg-[#0a0f1e]/90 backdrop-blur-xl border border-white/10 rounded-xl text-slate-400 hover:text-slate-200 transition-all"
          >
            <ZoomIn size={16} />
          </button>
          <button
            onClick={() => {
              if (svgRef.current) {
                d3.select(svgRef.current).transition().duration(300).call((selection: any, k: number) => {
                  selection.call(d3.zoom().scaleBy, 0.67);
                });
              }
            }}
            className="p-2.5 bg-[#0a0f1e]/90 backdrop-blur-xl border border-white/10 rounded-xl text-slate-400 hover:text-slate-200 transition-all"
          >
            <ZoomOut size={16} />
          </button>
        </div>

        {/* SVG Canvas */}
        <svg ref={svgRef} className="w-full h-full">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
        </svg>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-[#0a0f1e]/90 backdrop-blur-xl border border-white/10 rounded-xl p-4">
          <div className="text-xs text-slate-500 mb-3 font-semibold uppercase tracking-wider">Node Types</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(TYPE_CONFIG).map(([type, config]) => (
              <div key={type} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: config.color, boxShadow: `0 0 8px ${config.glow}` }} />
                <span className="text-xs text-slate-400 capitalize">{type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="absolute bottom-4 right-4 bg-[#0a0f1e]/90 backdrop-blur-xl border border-white/10 rounded-xl p-4">
          <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Network</div>
          <div className="text-sm text-slate-300">
            <span className="text-cyan-400 font-semibold">{nodes.length}</span> nodes · <span className="text-cyan-400 font-semibold">{links.length}</span> connections
          </div>
        </div>
      </div>

      {/* Node Details Panel */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            className="w-80 glass-card p-5 flex flex-col"
          >
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-semibold text-white text-lg">{selectedNode.label}</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X size={16} className="text-slate-400" />
              </button>
            </div>

            <div className="flex items-center gap-2 mb-4">
              <span
                className="px-2.5 py-1 rounded-lg text-xs font-medium border"
                style={{
                  backgroundColor: `${TYPE_CONFIG[selectedNode.type]?.color}15`,
                  borderColor: `${TYPE_CONFIG[selectedNode.type]?.color}30`,
                  color: TYPE_CONFIG[selectedNode.type]?.color,
                }}
              >
                {selectedNode.type}
              </span>
            </div>

            <div className="space-y-4 flex-1 overflow-y-auto">
              <div>
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Connections</div>
                <div className="space-y-2">
                  {links
                    .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                    .map((link, i) => {
                      const otherId = link.source === selectedNode.id ? link.target : link.source;
                      const otherNode = nodes.find(n => n.id === otherId);
                      if (!otherNode) return null;
                      return (
                        <div
                          key={i}
                          className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 cursor-pointer transition-colors p-2 rounded-lg hover:bg-white/5"
                          onClick={() => setSelectedNode(otherNode)}
                        >
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: TYPE_CONFIG[otherNode.type]?.color }}
                          />
                          <span className="flex-1">{otherNode.label}</span>
                          <span className="text-xs text-slate-500">{link.type}</span>
                        </div>
                      );
                    })}
                  {links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id).length === 0 && (
                    <div className="text-sm text-slate-500 italic">No connections</div>
                  )}
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Related Memories</div>
                <div className="space-y-2">
                  <div className="text-sm text-slate-300 bg-white/5 rounded-lg p-3">
                    Project discussion and planning sessions
                  </div>
                  <div className="text-sm text-slate-300 bg-white/5 rounded-lg p-3">
                    Key decisions and action items
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-white/5 space-y-2">
              <button className="w-full px-3 py-2.5 bg-cyan-500/15 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-colors border border-cyan-500/20">
                View in Timeline
              </button>
              <button className="w-full px-3 py-2.5 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-sm font-medium hover:text-slate-200 hover:border-white/20 transition-all">
                Inspect Evidence
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}