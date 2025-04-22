"use client"

import { useEffect, useState, useRef } from "react"
import Image from "next/image"

interface SplashScreenProps {
  moduleName: string
  onComplete?: () => void
}

export function SplashScreen({ moduleName, onComplete }: SplashScreenProps) {
  const [progress, setProgress] = useState(0)
  const completedRef = useRef(false)

  // Effect for progress animation
  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer)
          return 100
        }
        return prev + 5
      })
    }, 100)

    return () => clearInterval(timer)
  }, [])

  // Separate effect to handle completion
  useEffect(() => {
    if (progress === 100 && onComplete && !completedRef.current) {
      completedRef.current = true
      // Add a small delay before calling onComplete
      const timeout = setTimeout(() => {
        onComplete()
      }, 500)

      return () => clearTimeout(timeout)
    }
  }, [progress, onComplete])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#001529] relative overflow-hidden">
      {/* Background glow effect */}
      <div className="absolute inset-0 bg-[#001529]">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-[#00e5ff] opacity-10 blur-[100px]" />
      </div>

      <div className="flex flex-col md:flex-row items-center justify-center gap-8 z-10 px-6">
        {/* TerraFusion Logo */}
        <div className="w-24 h-24 relative">
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png"
            alt="TerraFusion Logo"
            width={96}
            height={96}
            className="object-contain"
          />
        </div>

        {/* Module name */}
        <h1 className="text-4xl font-bold text-white text-shadow-[0_0_10px_rgba(0,229,255,0.5)]">{moduleName}</h1>
      </div>

      {/* Progress bar */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-1/3 max-w-md">
        <div className="h-10 bg-black/20 rounded-full overflow-hidden backdrop-blur-md">
          <div
            className="h-full bg-gradient-to-r from-[#00b8d4] to-[#00e5ff] transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  )
}
