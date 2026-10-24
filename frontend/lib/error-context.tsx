"use client";

import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
} from "react";

// ============================================================
// Types and definitions
// ============================================================

export type ErrorSeverity = "info" | "warning" | "error" | "success";

export interface ErrorToast {
  id: string;
  severity: ErrorSeverity;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  duration?: number | false;
}

export interface ErrorContextValue {
  // Show a toast notification
  showToast: (toast: Omit<ErrorToast, "id">) => void;
  // Dismiss a specific toast
  dismissToast: (id: string) => void;
  // Clear all toasts
  clearToasts: () => void;
}

// Internal context value extends public one with toasts array
interface InternalErrorContextValue extends ErrorContextValue {
  toasts: ErrorToast[];
}

// ============================================================
// Context + Provider
// ============================================================

const ErrorContext = createContext<ErrorContextValue | null>(null);
const InternalErrorContext = createContext<InternalErrorContextValue | null>(null);

export const ErrorProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<ErrorToast[]>([]);

  // Generate a unique, monotonically increasing ID
  const [counter, setCounter] = useState(0);
  const generateId = () => {
    setCounter((c) => c + 1);
    return `toast-${Date.now()}-${counter}`;
  };

  const addToast = (toast: Omit<ErrorToast, "id">) => {
    const id = generateId();
    setToasts((prev) => [...prev, { id, ...toast }] as ErrorToast[]);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const clearToasts = () => setToasts([]);

  const publicValue: ErrorContextValue = { showToast: addToast, dismissToast, clearToasts };

  const internalValue: InternalErrorContextValue = {
    ...publicValue,
    toasts,
  };

  return (
    <ErrorContext.Provider value={publicValue}>
      <InternalErrorContext.Provider value={internalValue}>
        {children}
      </InternalErrorContext.Provider>
    </ErrorContext.Provider>
  );
};

// Public hook for components to show/ dismiss toasts
export const useErrorContext = (): ErrorContextValue => {
  const ctx = useContext(ErrorContext);
  if (!ctx) {
    throw new Error("useErrorContext must be used within an ErrorProvider");
  }
  return ctx;
};

// Internal hook for the ToastContainer to read the toasts list
export const useToasts = (): ErrorToast[] => {
  const ctx = useContext(InternalErrorContext);
  if (!ctx) {
    throw new Error("useToasts must be used within an ErrorProvider");
  }
  return ctx.toasts;
};

// ============================================================
// ErrorBoundary — catches React render errors
// ============================================================

interface ErrorBoundaryProps {
  fallback?: ReactNode;
  onReset?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: unknown;
}

// Note: Using class component for ErrorBoundary as it's the standard way
// to catch render errors. In future, could consider react-error-boundary
// package or custom hook solution.
export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: unknown): ErrorBoundaryState {
    return { hasError: true, error };
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) this.props.onReset();
  };

  componentDidCatch(error: unknown, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center h-full p-6 text-center">
          <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
            <svg
              className="w-8 h-8 text-rose-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v4m0 4h.01m-6.74-7.74l-.01.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-white mb-2">
            Something went wrong
          </h2>
          <p className="text-slate-400 text-sm mb-4 max-w-md">
            {this.state.error instanceof Error
              ? this.state.error.message
              : "An unexpected rendering error occurred."}
          </p>
          <button
            onClick={this.handleReset}
            className="px-4 py-2 bg-cyan-500/15 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all border border-cyan-500/20"
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ============================================================
// useApiWithToast — convenience hook for API calls
// ============================================================

export interface ApiResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export const useApiWithToast = () => {
  const { showToast } = useErrorContext();

  const execute = async <T,>(
    promise: Promise<T>,
    options: {
      errorTitle?: string;
      successMessage?: string;
      silent?: boolean;
    } = {}
  ): Promise<ApiResult<T>> => {
    try {
      const data = await promise;
      if (options.successMessage) {
        showToast({
          severity: "success",
          title: "Success",
          description: options.successMessage,
        });
      }
      return { success: true, data };
    } catch (error: any) {
      const message =
        error?.message || error?.error || "An unexpected error occurred";

      if (!options.silent) {
        showToast({
          severity: "error",
          title: options.errorTitle ?? "Request Failed",
          description: message,
          duration: 8000,
        });
      }

      return { success: false, error: message };
    }
  };

  return { execute };
};