"use client"

import type React from "react"

import { useState, useEffect, createContext, useContext, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from "lucide-react"

// Types
type NotificationType = "success" | "error" | "info" | "warning"

interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  duration?: number
}

interface NotificationContextType {
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, "id">) => void
  removeNotification: (id: string) => void
}

// Create context
const NotificationContext = createContext<NotificationContextType>({
  notifications: [],
  addNotification: () => {},
  removeNotification: () => {},
})

// Provider component
export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = useCallback((notification: Omit<Notification, "id">) => {
    const id = Math.random().toString(36).substring(2, 9)
    setNotifications((prev) => [...prev, { ...notification, id }])
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id))
  }, [])

  return (
    <NotificationContext.Provider value={{ notifications, addNotification, removeNotification }}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  )
}

// Hook to use notifications
export function useNotifications() {
  const context = useContext(NotificationContext)

  if (!context) {
    throw new Error("useNotifications must be used within a NotificationProvider")
  }

  return context
}

// Notification container
function NotificationContainer() {
  const { notifications, removeNotification } = useNotifications()

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      <AnimatePresence>
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}

// Individual notification
function NotificationItem({
  notification,
  onClose,
}: {
  notification: Notification
  onClose: () => void
}) {
  useEffect(() => {
    if (notification.duration !== Number.POSITIVE_INFINITY) {
      const timer = setTimeout(() => {
        onClose()
      }, notification.duration || 5000)

      return () => clearTimeout(timer)
    }
  }, [notification, onClose])

  // Icon based on type
  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
  }

  // Colors based on type
  const colors = {
    success: "bg-[#00e5ff]/10 border-[#00e5ff]/30 text-[#00e5ff]",
    error: "bg-red-500/10 border-red-500/30 text-red-500",
    info: "bg-blue-500/10 border-blue-500/30 text-blue-500",
    warning: "bg-amber-500/10 border-amber-500/30 text-amber-500",
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      className={`relative backdrop-blur-lg rounded-lg border ${colors[notification.type]} p-4 shadow-lg`}
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0 mt-0.5">{icons[notification.type]}</div>

        <div className="flex-1">
          <h4 className="font-medium text-sm">{notification.title}</h4>
          <p className="text-xs opacity-80 mt-1">{notification.message}</p>
        </div>

        <button onClick={onClose} className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Progress bar */}
      {notification.duration !== Number.POSITIVE_INFINITY && (
        <motion.div
          className="absolute bottom-0 left-0 h-[2px] bg-current"
          initial={{ width: "100%" }}
          animate={{ width: "0%" }}
          transition={{ duration: (notification.duration || 5000) / 1000, ease: "linear" }}
        />
      )}
    </motion.div>
  )
}
