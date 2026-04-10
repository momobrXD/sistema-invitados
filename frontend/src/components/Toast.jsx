import { useState, useEffect, createContext, useContext, useCallback } from 'react'

const ToastContext = createContext()

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)

  const show = useCallback((msg, error = false) => {
    setToast({ msg, error })
  }, [])

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 3500)
    return () => clearTimeout(t)
  }, [toast])

  return (
    <ToastContext.Provider value={show}>
      {children}
      {toast && (
        <div
          className={`fixed bottom-8 right-8 px-6 py-3.5 rounded-xl text-white font-semibold text-[0.9rem] z-[9999] shadow-[0_8px_32px_rgba(0,0,0,.15)] transition-all ${
            toast.error ? 'bg-red-500' : 'bg-emerald-500'
          }`}
        >
          {toast.msg}
        </div>
      )}
    </ToastContext.Provider>
  )
}

export function useToast() {
  return useContext(ToastContext)
}
