"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"

interface ProgressIndicatorProps {
  value: number
  max?: number
  size?: "sm" | "md" | "lg"
  variant?: "line" | "circle" | "semicircle"
  showValue?: boolean
  color?: string
  trackColor?: string
  className?: string
  label?: string
  animated?: boolean
}

export function ProgressIndicator({
  value,
  max = 100,
  size = "md",
  variant = "line",
  showValue = true,
  color = "#00e5ff",
  trackColor = "#002a4a",
  className = "",
  label,
  animated = true,
}: ProgressIndicatorProps) {
  const [displayValue, setDisplayValue] = useState(0)

  // Normalize value between 0 and 100
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  // Size maps
  const sizeMap = {
    sm: variant === "line" ? "h-1" : "w-16 h-16",
    md: variant === "line" ? "h-2" : "w-24 h-24",
    lg: variant === "line" ? "h-3" : "w-32 h-32",
  }

  // Text size maps
  const textSizeMap = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  }

  // Animate value
  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setDisplayValue(percentage)
      }, 100)
      return () => clearTimeout(timer)
    } else {
      setDisplayValue(percentage)
    }
  }, [percentage, animated])

  // Render line progress
  if (variant === "line") {
    return (
      <div className={`w-full ${className}`}>
        {label && (
          <div className="flex justify-between mb-1">
            <span className="text-xs text-[#00e5ff]/70">{label}</span>
            {showValue && <span className="text-xs text-[#00e5ff]/70">{Math.round(displayValue)}%</span>}
          </div>
        )}
        <div className={`w-full ${sizeMap[size]} bg-[${trackColor}] rounded-full overflow-hidden`}>
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: color }}
            initial={{ width: 0 }}
            animate={{ width: `${displayValue}%` }}
            transition={{ duration: animated ? 1 : 0, ease: "easeOut" }}
          />
        </div>
      </div>
    )
  }

  // Render circle or semicircle progress
  const radius = variant === "circle" ? 40 : 40
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (displayValue / 100) * circumference
  const viewBox = variant === "circle" ? "0 0 100 100" : "0 0 100 50"

  return (
    <div className={`flex flex-col items-center ${className}`}>
      {label && <span className="text-sm text-[#00e5ff]/70 mb-2">{label}</span>}
      <div className={`relative ${sizeMap[size]}`}>
        <svg className="w-full h-full" viewBox={viewBox}>
          {/* Background track */}
          {variant === "circle" ? (
            <circle cx="50" cy="50" r={radius} fill="none" stroke={trackColor} strokeWidth="8" />
          ) : (
            <path
              d={`M 10 50 A 40 40 0 0 1 90 50`}
              fill="none"
              stroke={trackColor}
              strokeWidth="8"
              strokeLinecap="round"
            />
          )}

          {/* Progress */}
          {variant === "circle" ? (
            <motion.circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth="8"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: animated ? 1 : 0, ease: "easeOut" }}
              strokeLinecap="round"
              transform="rotate(-90 50 50)"
            />
          ) : (
            <motion.path
              d={`M 10 50 A 40 40 0 0 1 90 50`}
              fill="none"
              stroke={color}
              strokeWidth="8"
              strokeDasharray={circumference / 2}
              initial={{ strokeDashoffset: circumference / 2 }}
              animate={{ strokeDashoffset: circumference / 2 - (displayValue / 100) * (circumference / 2) }}
              transition={{ duration: animated ? 1 : 0, ease: "easeOut" }}
              strokeLinecap="round"
            />
          )}
        </svg>

        {/* Center text */}
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`font-bold text-white ${textSizeMap[size]}`}>{Math.round(displayValue)}%</span>
          </div>
        )}
      </div>
    </div>
  )
}
