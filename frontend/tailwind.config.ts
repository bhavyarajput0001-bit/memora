import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Design system from mockup
        memora: {
          bg: "#000020",
          sidebar: "#07172a",
          content: "#0a1b30",
          card: "#0d1f38",
          border: "#1a2d4a",
          accent: "#0060e0",
          accentLight: "#2860a3",
          text: "#cad6e6",
          textMuted: "#6080a0",
          textBright: "#ffffff",
          success: "#10b981",
          warning: "#f59e0b",
          error: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        memora: "10px",
        memoraLg: "14px",
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
      },
    },
  },
  plugins: [],
};

export default config;
