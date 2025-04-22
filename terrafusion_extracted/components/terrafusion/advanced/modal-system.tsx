"use client"

import type React from "react"

import { useState, createContext, useContext, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"

// Types
interface ModalProps {
  title: string
  description?: string
  children?: React.ReactNode
  footer?: React.ReactNode
  size?: "sm" | "md" | "lg" | "full"
  onClose: () => void
}

interface ModalContextType {
  openModal: (props: Omit<ModalProps, "onClose">) => void
  closeModal: () => void
}

// Create context
const ModalContext = createContext<ModalContextType>({
  openModal: () => {},
  closeModal: () => {},
})

// Provider component
export function ModalProvider({ children }: { children: React.ReactNode }) {
  const [modalProps, setModalProps] = useState<ModalProps | null>(null)

  const openModal = useCallback((props: Omit<ModalProps, "onClose">) => {
    setModalProps({ ...props, onClose: () => setModalProps(null) })
  }, [])

  const closeModal = useCallback(() => {
    setModalProps(null)
  }, [])

  return (
    <ModalContext.Provider value={{ openModal, closeModal }}>
      {children}
      <AnimatePresence>{modalProps && <Modal {...modalProps} />}</AnimatePresence>
    </ModalContext.Provider>
  )
}

// Hook to use modal
export function useModal() {
  const context = useContext(ModalContext)

  if (!context) {
    throw new Error("useModal must be used within a ModalProvider")
  }

  return context
}

// Size map for modal width
const sizeMap = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
  full: "max-w-4xl",
}

// Modal component
function Modal({ title, description, children, footer, size = "md", onClose }: ModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        className={`relative ${sizeMap[size]} w-full bg-[#001529]/90 backdrop-blur-xl border border-[#00e5ff]/20 rounded-xl shadow-xl overflow-hidden`}
        style={{ boxShadow: "0 0 30px rgba(0,229,255,0.2)" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#00e5ff]/10">
          <div>
            <h2 className="text-lg font-medium text-white">{title}</h2>
            {description && <p className="text-sm text-[#00e5ff]/70 mt-1">{description}</p>}
          </div>

          <button onClick={onClose} className="text-[#00e5ff]/70 hover:text-[#00e5ff] transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">{children}</div>

        {/* Footer */}
        {footer && <div className="p-4 border-t border-[#00e5ff]/10 flex justify-end gap-2">{footer}</div>}

        {/* Bottom glow */}
        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[#00e5ff]/50 to-transparent" />
      </motion.div>
    </div>
  )
}

// Confirmation modal
export function useConfirmation() {
  const { openModal, closeModal } = useModal()

  const confirm = useCallback(
    ({
      title,
      message,
      confirmText = "Confirm",
      cancelText = "Cancel",
      onConfirm,
      onCancel,
      type = "default",
    }: {
      title: string
      message: string
      confirmText?: string
      cancelText?: string
      onConfirm: () => void
      onCancel?: () => void
      type?: "default" | "danger" | "warning"
    }) => {
      const buttonVariants = {
        default: "bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]",
        danger: "bg-red-500 hover:bg-red-600 text-white",
        warning: "bg-amber-500 hover:bg-amber-600 text-white",
      }

      openModal({
        title,
        description: message,
        size: "sm",
        footer: (
          <>
            <Button
              variant="outline"
              onClick={() => {
                closeModal()
                onCancel?.()
              }}
              className="text-[#00e5ff]/70 border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
            >
              {cancelText}
            </Button>
            <Button
              onClick={() => {
                closeModal()
                onConfirm()
              }}
              className={buttonVariants[type]}
            >
              {confirmText}
            </Button>
          </>
        ),
      })
    },
    [openModal, closeModal],
  )

  return { confirm }
}
