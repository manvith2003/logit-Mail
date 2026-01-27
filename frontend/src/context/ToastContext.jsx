import React, { createContext, useContext, useState, useCallback, useRef } from 'react';

const ToastContext = createContext();

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) throw new Error("useToast must be used within a ToastProvider");
    return context;
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);
    const toastIdCounter = useRef(0);

    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter(t => t.id !== id));
    }, []);

    const showToast = useCallback((message, options = {}) => {
        const id = toastIdCounter.current++;
        const duration = options.duration || 4000;
        
        const newToast = {
            id,
            message,
            type: options.type || 'info', // info, success, error
            action: options.action, // { label: 'Undo', onClick: () => ... }
        };

        setToasts((prev) => [...prev, newToast]);

        setTimeout(() => {
            removeToast(id);
        }, duration);
    }, [removeToast]);

    return (
        <ToastContext.Provider value={{ showToast }}>
            {children}
            {/* Toast Container */}
            <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-2 w-max max-w-[90vw]">
                {toasts.map((toast) => (
                    <div 
                        key={toast.id} 
                        className="bg-gray-900 text-white px-4 py-3 rounded shadow-lg flex items-center justify-between gap-4 text-sm animate-in fade-in slide-in-from-bottom-2"
                    >
                        <span>{toast.message}</span>
                        {toast.action && (
                            <button 
                                onClick={() => {
                                    toast.action.onClick();
                                    removeToast(toast.id);
                                }}
                                className="text-blue-400 font-bold hover:text-blue-300 uppercase text-xs"
                            >
                                {toast.action.label}
                            </button>
                        )}
                        <button 
                             onClick={() => removeToast(toast.id)}
                             className="text-gray-500 hover:text-white"
                        >
                            ×
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};
