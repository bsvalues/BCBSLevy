"use client"

import React from "react"

import { useState, useEffect, useRef } from "react"
import { useInView } from "framer-motion"
import type { MotionValue } from "framer-motion"
import { motion, useSpring, useTransform } from "framer-motion"

// Hook for reveal animations when elements come into view
export function useRevealAnimation(
  direction: "up" | "down" | "left" | "right" = "up",
  delay = 0,
  duration = 0.5,
  threshold = 0.1,
) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, amount: threshold })

  const getInitialPosition = () => {
    switch (direction) {
      case "up":
        return { opacity: 0, y: 40 }
      case "down":
        return { opacity: 0, y: -40 }
      case "left":
        return { opacity: 0, x: 40 }
      case "right":
        return { opacity: 0, x: -40 }
      default:
        return { opacity: 0, y: 40 }
    }
  }

  const getFinalPosition = () => {
    return { opacity: 1, x: 0, y: 0 }
  }

  const variants = {
    hidden: getInitialPosition(),
    visible: {
      ...getFinalPosition(),
      transition: {
        duration,
        delay,
        ease: [0.25, 0.1, 0.25, 1.0], // Cubic bezier for smooth easing
      },
    },
  }

  return { ref, isInView, variants }
}

// Hook for parallax scrolling effects
export function useParallax(value: MotionValue<number>, distance: number) {
  return useTransform(value, [0, 1], [-distance, distance])
}

// Hook for smooth counter animation
export function useSmoothCounter(targetValue: number, duration = 2, delay = 0, precision = 0) {
  const [displayValue, setDisplayValue] = useState(0)
  const springValue = useSpring(0, { duration: duration * 1000, delay: delay * 1000 })

  useEffect(() => {
    springValue.set(targetValue)
  }, [springValue, targetValue])

  useEffect(() => {
    const unsubscribe = springValue.onChange((latest) => {
      setDisplayValue(Number.parseFloat(latest.toFixed(precision)))
    })
    return unsubscribe
  }, [springValue, precision])

  return displayValue
}

// Hook for staggered animations in lists
export function useStaggeredAnimation(itemCount: number, staggerDelay = 0.1, initialDelay = 0.2, duration = 0.5) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: initialDelay,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration,
        ease: "easeOut",
      },
    },
  }

  return { containerVariants, itemVariants }
}

// Hook for hover animations
export function useHoverAnimation(scale = 1.05, duration = 0.2) {
  const [isHovered, setIsHovered] = useState(false)

  const variants = {
    initial: { scale: 1 },
    hover: {
      scale,
      transition: {
        duration,
        ease: "easeOut",
      },
    },
  }

  const handleHoverStart = () => setIsHovered(true)
  const handleHoverEnd = () => setIsHovered(false)

  return { isHovered, variants, handleHoverStart, handleHoverEnd }
}

// Hook for 3D tilt effect
export function useTiltEffect(intensity = 10, perspective = 1000, scale = 1.05, duration = 0.5) {
  const [tiltValues, setTiltValues] = useState({ rotateX: 0, rotateY: 0 })
  const ref = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return

    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    // Calculate distance from center (normalized from -1 to 1)
    const rotateYValue = ((e.clientX - centerX) / (rect.width / 2)) * intensity
    const rotateXValue = ((e.clientY - centerY) / (rect.height / 2)) * -intensity

    setTiltValues({ rotateX: rotateXValue, rotateY: rotateYValue })
  }

  const handleMouseLeave = () => {
    setTiltValues({ rotateX: 0, rotateY: 0 })
  }

  const style = {
    transform: `perspective(${perspective}px) rotateX(${tiltValues.rotateX}deg) rotateY(${tiltValues.rotateY}deg)`,
    transition: `transform ${duration}s ease-out`,
  }

  return { ref, style, handleMouseMove, handleMouseLeave }
}

// Animated component wrapper for reveal animations
export function RevealAnimation({
  children,
  direction = "up",
  delay = 0,
  duration = 0.5,
  threshold = 0.1,
  className = "",
}: {
  children: React.ReactNode
  direction?: "up" | "down" | "left" | "right"
  delay?: number
  duration?: number
  threshold?: number
  className?: string
}) {
  const { ref, isInView, variants } = useRevealAnimation(direction, delay, duration, threshold)

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={variants}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Staggered list animation component
export function StaggeredList({
  children,
  staggerDelay = 0.1,
  initialDelay = 0.2,
  duration = 0.5,
  className = "",
}: {
  children: React.ReactNode
  staggerDelay?: number
  initialDelay?: number
  duration?: number
  className?: string
}) {
  const { containerVariants, itemVariants } = useStaggeredAnimation(
    React.Children.count(children),
    staggerDelay,
    initialDelay,
    duration,
  )

  return (
    <motion.div initial="hidden" animate="visible" variants={containerVariants} className={className}>
      {React.Children.map(children, (child, index) => (
        <motion.div key={index} variants={itemVariants}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}
