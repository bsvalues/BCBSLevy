"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"

interface GlassmorphicContainerProps {
  children: React.ReactNode
  className?: string
  intensity?: "light" | "medium" | "strong"
  interactive?: boolean
  hoverEffect?: boolean
  glowColor?: string
}

export function GlassmorphicContainer({
  children,
  className = "",
  intensity = "medium",
  interactive = false,
  hoverEffect = false,
  glowColor = "#00e5ff",
}: GlassmorphicContainerProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  // Intensity settings
  const blurMap = {
    light: "backdrop-blur-md",
    medium: "backdrop-blur-xl",
    strong: "backdrop-blur-2xl",
  }

  const bgOpacityMap = {
    light: "bg-[#001529]/60",
    medium: "bg-[#001529]/70",
    strong: "bg-[#001529]/80",
  }

  const borderOpacityMap = {
    light: "border-[#00e5ff]/10",
    medium: "border-[#00e5ff]/20",
    strong: "border-[#00e5ff]/30",
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!interactive || !containerRef.current) return

    const rect = containerRef.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100

    setPosition({ x, y })
  }

  return (
    <motion.div
      ref={containerRef}
      className={`relative border rounded-xl overflow-hidden ${blurMap[intensity]} ${bgOpacityMap[intensity]} ${borderOpacityMap[intensity]} ${className}`}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      animate={
        hoverEffect
          ? {
              scale: isHovered ? 1.02 : 1,
              boxShadow: isHovered
                ? `0 0 30px rgba(${Number.parseInt(glowColor.slice(1, 3), 16)}, ${Number.parseInt(
                    glowColor.slice(3, 5),
                    16,
                  )}, ${Number.parseInt(glowColor.slice(5, 7), 16)}, 0.3)`
                : `0 0 20px rgba(${Number.parseInt(glowColor.slice(1, 3), 16)}, ${Number.parseInt(
                    glowColor.slice(3, 5),
                    16,
                  )}, ${Number.parseInt(glowColor.slice(5, 7), 16)}, 0.1)`,
            }
          : {}
      }
      transition={{ duration: 0.3 }}
    >
      {/* Interactive glow effect */}
      {interactive && (
        <div
          className="absolute pointer-events-none transition-opacity duration-300"
          style={{
            background: `radial-gradient(circle at ${position.x}% ${position.y}%, ${glowColor}20 0%, ${glowColor}00 60%)`,
            width: "150%",
            height: "150%",
            left: "-25%",
            top: "-25%",
            opacity: isHovered ? 1 : 0,
          }}
        />
      )}

      {/* Bottom highlight */}
      <div
        className={`absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[${glowColor}] to-transparent transition-opacity duration-300`}
        style={{ opacity: isHovered && interactive ? 0.5 : 0.3 }}
      />

      {children}
    </motion.div>
  )
}

interface GlowEffectProps {
  children: React.ReactNode
  color?: string
  intensity?: "light" | "medium" | "strong"
  className?: string
  pulseEffect?: boolean
}

export function GlowEffect({
  children,
  color = "#00e5ff",
  intensity = "medium",
  className = "",
  pulseEffect = false,
}: GlowEffectProps) {
  // Intensity settings
  const blurMap = {
    light: "10px",
    medium: "15px",
    strong: "25px",
  }

  const opacityMap = {
    light: 0.2,
    medium: 0.3,
    strong: 0.4,
  }

  return (
    <div className={`relative ${className}`}>
      <div
        className={`absolute inset-0 -z-10 ${pulseEffect ? "animate-pulse-glow" : ""}`}
        style={{
          background: color,
          filter: `blur(${blurMap[intensity]})`,
          opacity: opacityMap[intensity],
        }}
      />
      {children}
    </div>
  )
}

interface FloatingElementProps {
  children: React.ReactNode
  amplitude?: number
  duration?: number
  className?: string
}

export function FloatingElement({ children, amplitude = 10, duration = 4, className = "" }: FloatingElementProps) {
  return (
    <motion.div
      className={className}
      animate={{
        y: [0, -amplitude, 0, amplitude, 0],
      }}
      transition={{
        duration,
        repeat: Number.POSITIVE_INFINITY,
        ease: "easeInOut",
      }}
    >
      {children}
    </motion.div>
  )
}

interface ParticleFieldProps {
  count?: number
  color?: string
  size?: number
  speed?: number
  className?: string
}

export function ParticleField({
  count = 50,
  color = "#00e5ff",
  size = 2,
  speed = 3,
  className = "",
}: ParticleFieldProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })
  const [particles, setParticles] = useState<Array<{ x: number; y: number; size: number; duration: number }>>([])

  useEffect(() => {
    if (!containerRef.current) return

    const updateDimensions = () => {
      if (!containerRef.current) return
      const { width, height } = containerRef.current.getBoundingClientRect()
      setDimensions({ width, height })

      // Generate particles
      const newParticles = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * size + 1,
        duration: Math.random() * speed + speed / 2,
      }))

      setParticles(newParticles)
    }

    updateDimensions()
    window.addEventListener("resize", updateDimensions)

    return () => {
      window.removeEventListener("resize", updateDimensions)
    }
  }, [count, size, speed])

  return (
    <div ref={containerRef} className={`absolute inset-0 overflow-hidden ${className}`}>
      {particles.map((particle, index) => (
        <motion.div
          key={index}
          className="absolute rounded-full"
          style={{
            backgroundColor: color,
            width: particle.size,
            height: particle.size,
            left: particle.x,
            top: particle.y,
            opacity: 0.6,
          }}
          animate={{
            y: [0, -dimensions.height],
            opacity: [0, 0.8, 0],
          }}
          transition={{
            duration: particle.duration,
            repeat: Number.POSITIVE_INFINITY,
            delay: Math.random() * speed,
            ease: "linear",
          }}
        />
      ))}
    </div>
  )
}

interface AnimatedBackgroundProps {
  children: React.ReactNode
  variant?: "particles" | "gradient" | "waves"
  className?: string
}

export function AnimatedBackground({ children, variant = "gradient", className = "" }: AnimatedBackgroundProps) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      {variant === "particles" && <ParticleField />}

      {variant === "gradient" && (
        <motion.div
          className="absolute inset-0 -z-10"
          style={{
            background: "radial-gradient(circle at 50% 50%, #00e5ff10, #00152900 70%)",
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
      )}

      {variant === "waves" && (
        <div className="absolute inset-0 -z-10">
          <svg className="absolute bottom-0 left-0 w-full" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
            <motion.path
              fill="#00e5ff10"
              d="M0,192L48,176C96,160,192,128,288,133.3C384,139,480,181,576,186.7C672,192,768,160,864,154.7C960,149,1056,171,1152,165.3C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
              animate={{
                d: [
                  "M0,192L48,176C96,160,192,128,288,133.3C384,139,480,181,576,186.7C672,192,768,160,864,154.7C960,149,1056,171,1152,165.3C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z",
                  "M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,138.7C672,128,768,160,864,165.3C960,171,1056,149,1152,154.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z",
                ],
              }}
              transition={{
                duration: 10,
                repeat: Number.POSITIVE_INFINITY,
                repeatType: "reverse",
                ease: "easeInOut",
              }}
            />
          </svg>
        </div>
      )}

      {children}
    </div>
  )
}
