"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"

interface ToastProps {
  message: string
  duration?: number
  onClose?: () => void
}

export function NotificationToast({ message, duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      onClose?.()
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  if (!isVisible) return null

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-4 max-w-[400px] min-h-[64px] px-4 py-2 bg-[#001529] border border-[#00e5ff]/20 text-white rounded-xl shadow-[0_0_20px_rgba(0,229,255,0.2)]">
      {/* TerraFusion Seal Icon */}
      <div className="w-6 h-6 flex-shrink-0 relative">
        <div className="w-6 h-6 rounded-full border border-[#00e5ff] flex items-center justify-center">
          <div className="w-4 h-4 text-[#00e5ff]">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M12 2L4 6V12C4 15.31 7.58 18.5 12 20C16.42 18.5 20 15.31 20 12V6L12 2Z"
                stroke="currentColor"
                strokeWidth="2"
              />
              <path
                d="M9 12L11 14L15 10"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Message text */}
      <p className="text-base font-normal flex-1">{message}</p>

      {/* Close button */}
      <button
        onClick={() => {
          setIsVisible(false)
          onClose?.()
        }}
        className="w-6 h-6 flex items-center justify-center text-[#00e5ff]/60 hover:text-[#00e5ff]"
      >
        <X size={16} />
      </button>
    </div>
  )
}
