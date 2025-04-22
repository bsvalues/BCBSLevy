"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { ArrowUp, ArrowDown, MoreVertical, RefreshCw } from "lucide-react"

interface DashboardWidgetProps {
  title: string
  value: number | string
  previousValue?: number | string
  unit?: string
  icon?: React.ReactNode
  loading?: boolean
  refreshInterval?: number
  onRefresh?: () => Promise<any>
  className?: string
  children?: React.ReactNode
}

export function DashboardWidget({
  title,
  value,
  previousValue,
  unit = "",
  icon,
  loading = false,
  refreshInterval,
  onRefresh,
  className = "",
  children,
}: DashboardWidgetProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [currentValue, setCurrentValue] = useState(value)
  const [previousVal, setPreviousVal] = useState(previousValue)

  // Calculate percentage change
  const percentageChange =
    previousVal !== undefined && typeof currentValue === "number" && typeof previousVal === "number"
      ? ((currentValue - previousVal) / previousVal) * 100
      : undefined

  // Handle refresh
  const handleRefresh = async () => {
    if (isRefreshing || !onRefresh) return

    setIsRefreshing(true)
    try {
      const result = await onRefresh()
      if (result !== undefined) {
        setPreviousVal(currentValue)
        setCurrentValue(result)
      }
    } catch (error) {
      console.error("Failed to refresh widget:", error)
    } finally {
      setIsRefreshing(false)
    }
  }

  // Auto refresh
  useEffect(() => {
    if (!refreshInterval || !onRefresh) return

    const interval = setInterval(handleRefresh, refreshInterval)
    return () => clearInterval(interval)
  }, [refreshInterval, onRefresh])

  // Update value when prop changes
  useEffect(() => {
    setCurrentValue(value)
  }, [value])

  // Update previous value when prop changes
  useEffect(() => {
    setPreviousVal(previousValue)
  }, [previousValue])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-[#001529]/90 border border-[#00e5ff]/20 rounded-xl overflow-hidden ${className}`}
      style={{ boxShadow: "0 0 20px rgba(0,229,255,0.1)" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[#00e5ff]/10">
        <div className="flex items-center gap-2">
          {icon && <div className="text-[#00e5ff] p-1 rounded-md bg-[#00e5ff]/10">{icon}</div>}
          <h3 className="text-sm font-medium text-white">{title}</h3>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || loading}
            className="p-1 text-[#00e5ff]/70 hover:text-[#00e5ff] disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
          </button>

          <button className="p-1 text-[#00e5ff]/70 hover:text-[#00e5ff] transition-colors">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Value */}
        <div className="flex items-end gap-2">
          {loading || isRefreshing ? (
            <div className="h-10 w-24 bg-[#00e5ff]/10 animate-pulse rounded" />
          ) : (
            <div className="text-3xl font-bold text-white">
              {currentValue}
              <span className="text-sm ml-1 text-[#00e5ff]/70">{unit}</span>
            </div>
          )}

          {/* Percentage change */}
          {percentageChange !== undefined && (
            <div className={`flex items-center text-xs ${percentageChange >= 0 ? "text-green-400" : "text-red-400"}`}>
              {percentageChange >= 0 ? (
                <ArrowUp className="w-3 h-3 mr-0.5" />
              ) : (
                <ArrowDown className="w-3 h-3 mr-0.5" />
              )}
              {Math.abs(percentageChange).toFixed(1)}%
            </div>
          )}
        </div>

        {/* Additional content */}
        {children && <div className="mt-4">{children}</div>}
      </div>

      {/* Bottom glow */}
      <div className="h-[1px] bg-gradient-to-r from-transparent via-[#00e5ff]/30 to-transparent" />
    </motion.div>
  )
}
