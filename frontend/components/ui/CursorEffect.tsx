"use client";

import { useEffect, useRef } from "react";

export default function CursorEffect() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const pointsRef = useRef<{ x: number; y: number; originX: number; originY: number }[]>([]);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initPoints();
    };

    const initPoints = () => {
      pointsRef.current = [];
      const spacing = 50;
      for (let x = 0; x < canvas.width; x += spacing) {
        for (let y = 0; y < canvas.height; y += spacing) {
          pointsRef.current.push({ x, y, originX: x, originY: y });
        }
      }
    };

    resize();
    window.addEventListener("resize", resize);

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };

    window.addEventListener("mousemove", handleMouseMove);

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const { x, y } = mouseRef.current;
      const influenceRadius = 150;

      pointsRef.current.forEach((point) => {
        const dx = point.x - x;
        const dy = point.y - y;
        const dist = Math.hypot(dx, dy);

        if (dist < influenceRadius) {
          const force = (influenceRadius - dist) / influenceRadius;
          const angle = Math.atan2(dy, dx);
          const pushX = Math.cos(angle) * force * 30;
          const pushY = Math.sin(angle) * force * 30;

          point.x = point.originX - pushX;
          point.y = point.originY - pushY;

          // Draw connection to cursor
          ctx.beginPath();
          ctx.moveTo(point.x, point.y);
          ctx.lineTo(x, y);
          ctx.strokeStyle = `rgba(6, 182, 212, ${force * 0.3})`;
          ctx.lineWidth = force * 2;
          ctx.stroke();
        } else {
          // Return to origin
          point.x += (point.originX - point.x) * 0.1;
          point.y += (point.originY - point.y) * 0.1;
        }

        // Draw point
        const brightness = dist < influenceRadius ? 
          0.5 + (1 - dist / influenceRadius) * 0.5 : 0.2;
        
        ctx.beginPath();
        ctx.arc(point.x, point.y, dist < influenceRadius ? 3 : 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6, 182, 212, ${brightness})`;
        ctx.fill();
      });

      rafRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-50"
    />
  );
}
