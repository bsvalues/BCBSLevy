"use client"

import type React from "react"

import { GlassmorphicContainer } from "../animation/glassmorphic-effects"

interface InfoCardProps {
  title: string
  content: string | React.ReactNode
  icon?: React.ReactNode
  actions?: React.ReactNode
  className?: string
  variant?: "default" | "bordered" | "elevated"
}

export function InfoCard({ title, content, icon, actions, className = "", variant = "default" }: InfoCardProps) {
  const variantStyles = {
    default: "",
    bordered: "border-2 border-[#00e5ff]/30",
    elevated: "shadow-lg",
  }

  return (
    <GlassmorphicContainer className={`overflow-hidden ${variantStyles[variant]} ${className}`}>
      <div className="p-6">
        {/* Header with title and icon */}
        <div className="flex items-center gap-3 mb-4">
          {icon && <div className="text-[#00e5ff] p-2 rounded-lg bg-[#00e5ff]/10">{icon}</div>}
          <h3 className="text-lg font-medium text-white">{title}</h3>
        </div>

        {/* Content */}
        <div className="text-[#00e5ff]/70 text-sm">{typeof content === "string" ? <p>{content}</p> : content}</div>

        {/* Actions */}
        {actions && <div className="mt-4 flex gap-2 justify-end">{actions}</div>}
      </div>
    </GlassmorphicContainer>
  )
}
