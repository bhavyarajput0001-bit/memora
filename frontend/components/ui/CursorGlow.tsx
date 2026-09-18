"use client";

import { useEffect, useState } from "react";

export default function CursorGlow() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    
    const updatePosition = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", updatePosition);
    return () => window.removeEventListener("mousemove", updatePosition);
  }, []);

  if (!isMounted) return null;

  return (
    <div 
      className="fixed pointer-events-none z-0 transition-all duration-150 ease-out"
      style={{
        left: position.x,
        top: position.y,
        transform: "translate(-50%, -50%)",
      }}
    >
      {/* Outer glow */}
      <div 
        className="absolute rounded-full"
        style={{
          width: "400px",
          height: "400px",
          left: "-200px",
          top: "-200px",
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, rgba(6, 182, 212, 0.05) 40%, transparent 70%)",
          filter: "blur(20px)",
        }}
      />
      {/* Inner glow */}
      <div 
        className="absolute rounded-full"
        style={{
          width: "200px",
          height: "200px",
          left: "-100px",
          top: "-100px",
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.2) 0%, rgba(6, 182, 212, 0.1) 50%, transparent 70%)",
          filter: "blur(10px)",
        }}
      />
      {/* Core glow */}
      <div 
        className="absolute rounded-full"
        style={{
          width: "80px",
          height: "80px",
          left: "-40px",
          top: "-40px",
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, rgba(6, 182, 212, 0.1) 60%, transparent 80%)",
          filter: "blur(5px)",
        }}
      />
    </div>
  );
}
