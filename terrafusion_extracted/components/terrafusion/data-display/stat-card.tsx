"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ArrowUp, ArrowDown } from "lucide-react"
import { useSmoothCounter } from "../animation/use-animation-hooks"
import { GlassmorphicContainer } from "../animation/glassmorphic-effects"

interface StatCardProps {
  title: string
  value: number
  previousValue?: number
  unit?: string
  icon?: React.ReactNode
  description?: string
  trend?: "up" | "down" | "neutral"
  trendValue?: number
  loading?: boolean
  className?: string
}

export function StatCard({
  title,
  value,
  previousValue,
  unit = "",
  icon,
  description,
  trend,
  trendValue,
  loading = false,
  className = "",
}: StatCardProps) {
  // Calculate trend if not provided but previous value exists
  const [calculatedTrend, setCalculatedTrend] = useState<"up" | "down" | "neutral" | undefined>(trend)
  const [calculatedTrendValue, setCalculatedTrendValue] = useState<number | undefined>(trendValue)

  // Use smooth counter animation
  const displayValue = useSmoothCounter(value, 2, 0, 1)

  // Calculate trend if not provided
  useEffect(() => {
    if (trend === undefined && previousValue !== undefined && value !== previousValue) {
      const newTrend = value > previousValue ? "up" : value < previousValue ? "down" : "neutral"
      setCalculatedTrend(newTrend)

      if (trendValue === undefined) {
        const percentChange = ((value - previousValue) / previousValue) * 100
        setCalculatedTrendValue(Math.abs(percentChange))
      }
    }
  }, [value, previousValue, trend, trendValue])

  // Determine which trend to display
  const displayTrend = trend || calculatedTrend
  const displayTrendValue = trendValue || calculatedTrendValue

  return (
    <GlassmorphicContainer className={`p-6 ${className}`} interactive={true} hoverEffect={true}>
      <div className="flex flex-col">
        {/* Header with title and icon */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-[#00e5ff]/70">{title}</h3>
          {icon && <div className="text-[#00e5ff] p-1 rounded-md bg-[#00e5ff]/10">{icon}</div>}
        </div>

        {/* Value */}
        <div className="flex items-end gap-2">
          {loading ? (
            <div className="h-10 w-24 bg-[#00e5ff]/10 animate-pulse rounded" />
          ) : (
            <div className="text-3xl font-bold text-white">
              {displayValue}
              <span className="text-sm ml-1 text-[#00e5ff]/70">{unit}</span>
            </div>
          )}

          {/* Trend indicator */}
          {displayTrend && displayTrendValue !== undefined && (
            <div
              className={`flex items-center text-xs ${
                displayTrend === "up"
                  ? "text-green-400"
                  : displayTrend === "down"
                    ? "text-red-400"
                    : "text-[#00e5ff]/70"
              }`}
            >
              {displayTrend === "up" ? (
                <ArrowUp className="w-3 h-3 mr-0.5" />
              ) : displayTrend === "down" ? (
                <ArrowDown className="w-3 h-3 mr-0.5" />
              ) : null}
              {displayTrendValue.toFixed(1)}%
            </div>
          )}
        </div>

        {/* Description */}
        {description && <p className="mt-2 text-xs text-[#00e5ff]/50">{description}</p>}
      </div>
    </GlassmorphicContainer>
  )
}
