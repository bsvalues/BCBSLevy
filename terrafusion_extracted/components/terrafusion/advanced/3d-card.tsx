"use client"

import type React from "react"

import { useState, useRef } from "react"
import { motion } from "framer-motion"
import Image from "next/image"

interface ThreeDCardProps {
  title: string
  description: string
  icon?: React.ReactNode
  image?: string
  className?: string
  children?: React.ReactNode
}

export function ThreeDCard({ title, description, icon, image, className = "", children }: ThreeDCardProps) {
  const [rotateX, setRotateX] = useState(0)
  const [rotateY, setRotateY] = useState(0)
  const [glowX, setGlowX] = useState(0)
  const [glowY, setGlowY] = useState(0)
  const [isHovered, setIsHovered] = useState(false)

  const cardRef = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return

    const rect = cardRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    // Calculate distance from center (normalized from -1 to 1)
    const rotateYValue = ((e.clientX - centerX) / (rect.width / 2)) * 5
    const rotateXValue = ((e.clientY - centerY) / (rect.height / 2)) * -5

    // Calculate glow position
    const glowXValue = ((e.clientX - rect.left) / rect.width) * 100
    const glowYValue = ((e.clientY - rect.top) / rect.height) * 100

    setRotateX(rotateXValue)
    setRotateY(rotateYValue)
    setGlowX(glowXValue)
    setGlowY(glowYValue)
  }

  return (
    <motion.div
      ref={cardRef}
      className={`relative overflow-hidden rounded-xl bg-[#001529]/90 border border-[#00e5ff]/20 ${className}`}
      style={{
        boxShadow: "0 0 20px rgba(0,229,255,0.1)",
        transformStyle: "preserve-3d",
        perspective: "1000px",
      }}
      animate={{
        rotateX: rotateX,
        rotateY: rotateY,
      }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false)
        setRotateX(0)
        setRotateY(0)
      }}
    >
      {/* Dynamic glow effect */}
      <div
        className="absolute pointer-events-none transition-opacity duration-300"
        style={{
          background: `radial-gradient(circle at ${glowX}% ${glowY}%, rgba(0,229,255,0.15) 0%, rgba(0,229,255,0) 50%)`,
          width: "150%",
          height: "150%",
          left: "-25%",
          top: "-25%",
          opacity: isHovered ? 1 : 0,
        }}
      />

      {/* Card content */}
      <div className="p-6 relative z-10">
        {image && (
          <div className="absolute top-0 right-0 w-24 h-24 opacity-10">
            <Image src={image || "/placeholder.svg"} alt="" width={96} height={96} className="object-contain" />
          </div>
        )}

        <div className="flex items-start gap-4">
          {icon && <div className="text-[#00e5ff] p-2 rounded-lg bg-[#00e5ff]/10">{icon}</div>}

          <div>
            <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
            <p className="text-[#00e5ff]/70 text-sm">{description}</p>

            {children && <div className="mt-4">{children}</div>}
          </div>
        </div>
      </div>

      {/* Bottom highlight */}
      <div
        className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[#00e5ff]/50 to-transparent transition-opacity duration-300"
        style={{ opacity: isHovered ? 1 : 0 }}
      />
    </motion.div>
  )
}
