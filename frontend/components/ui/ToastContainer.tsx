"use client";

import { useMemo } from "react";
import { AlertTriangle, CheckCircle, X } from "lucide-react";
import { useErrorContext, useToasts } from "@/lib/error-context";

const SeverityIcon: Record<"info" | "warning" | "error" | "success", JSX.Element> =
{
  info: <CheckCircle className="text-cyan-400" size={14} />,
  success: <CheckCircle className="text-emerald-400" size={14} />,
  warning: <AlertTriangle className="text-amber-400" size={14} />,
  error: <AlertTriangle className="text-rose-400" size={14} />,
};

interface Props {
  /** Whether to show a separator/divider above */
  divider?: boolean;
}

/**
 * ToastContainer displays notification toasts at the bottom-right corner.
 * Consumes both toasts list (via useToasts) and action handlers (via useErrorContext).
 *
 * Place this component near the root of your app (inside ErrorProvider).
 */
export const ToastContainer = ({ divider }: Props = {}) => {
  const toasts = useToasts();
  const { dismissToast } = useErrorContext();

  // Bail early if no toasts
  if (toasts.length === 0) return null;

  // Deterministic ordering: oldest first
  const sorted = useMemo(
    () =>
      [...toasts].sort(
        (a, b) => Number(a.id.split("-")[2]) - Number(b.id.split("-")[2])
      ),
    [toasts]
  );

  return (
    <>
      {divider && (
        <hr
          className="my-4 border-t border-white/5 w-[300px] self-end"
          aria-hidden="true"
        />
      )}
      <div
        className="fixed bottom-6 right-6 z-[1000] flex flex-col gap-3 w-[320px]"
        pointer-events="auto"
      >
        {sorted.map((toast) => {
          const autoDismiss =
            toast.duration === false ? null : toast.duration ?? 5000;

          return (
            <div
              key={toast.id}
              className={`
                relative p-4 rounded-xl shadow-lg
                ${
                  toast.severity === "error"
                    ? "bg-rose-500/10 border border-rose-500/20 text-rose-400"
                    : toast.severity === "warning"
                    ? "bg-amber-500/10 border border-amber-500/20 text-amber-400"
                    : toast.severity === "success"
                    ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                    : "bg-cyan-500/10 border border-cyan-500/20 text-cyan-400"
                }
                animate-in fade-up
                z-1000
              `}
              role="alert"
              aria-live="polite"
            >
              <div className="flex items-start gap-2.5">
                {/* Icon */}
                <div
                  className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-white/10"
                >
                  {SeverityIcon[toast.severity]}
                </div>

                {/* Title + description */}
                <div className="flex-1 min-w-0 space-y-0.5">
                  <p
                    className="font-medium text-sm whitespace-nowrap truncate"
                    title={toast.title}
                  >
                    {toast.title}
                  </p>
                  {toast.description && (
                    <p className="text-xs text-slate-400 line-clamp-2">
                      {toast.description}
                    </p>
                  )}
                </div>

                {/* Optional action button */}
                {toast.action && (
                  <button
                    onClick={toast.action.onClick}
                    className="mt-1 mr-auto text-xs font-medium text-cyan-400 hover:underline transition-colors"
                    aria-label={`${toast.title} action`}
                  >
                    {toast.action.label}
                  </button>
                )}

                {/* Close (X) button */}
                <button
                  onClick={() => dismissToast(toast.id)}
                  className="absolute right-2 top-2 rounded-full p-1 opacity-50 hover:bg-white/10 transition-colors"
                  aria-label="Dismiss"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
};