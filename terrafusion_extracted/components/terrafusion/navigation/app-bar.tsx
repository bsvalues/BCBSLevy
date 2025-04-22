"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import { Menu, X, Bell, Search, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import Image from "next/image"

interface AppBarProps {
  title?: string
  logo?: string
  onMenuClick?: () => void
  actions?: React.ReactNode
  className?: string
  variant?: "default" | "transparent" | "glassmorphic"
  position?: "static" | "sticky" | "fixed"
}

export function AppBar({
  title = "TerraFusion",
  logo = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png",
  onMenuClick,
  actions,
  className = "",
  variant = "default",
  position = "static",
}: AppBarProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false)

  const variantStyles = {
    default: "bg-[#001529] border-b border-[#00e5ff]/20",
    transparent: "bg-transparent",
    glassmorphic: "bg-[#001529]/70 backdrop-blur-xl border-b border-[#00e5ff]/20",
  }

  const positionStyles = {
    static: "",
    sticky: "sticky top-0 z-40",
    fixed: "fixed top-0 left-0 right-0 z-40",
  }

  return (
    <header
      className={`${variantStyles[variant]} ${positionStyles[position]} transition-colors duration-300 ${className}`}
    >
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Left section: Menu button and logo */}
        <div className="flex items-center gap-4">
          {onMenuClick && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onMenuClick}
              className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
            >
              <Menu className="h-5 w-5" />
            </Button>
          )}

          <div className="flex items-center gap-3">
            {logo && (
              <div className="w-8 h-8 relative">
                <Image src={logo || "/placeholder.svg"} alt={title} width={32} height={32} className="object-contain" />
              </div>
            )}
            <h1 className="text-lg font-medium text-white hidden sm:block">{title}</h1>
          </div>
        </div>

        {/* Right section: Actions */}
        <div className="flex items-center gap-2">
          {isSearchOpen ? (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: "240px", opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="relative"
            >
              <Input
                className="h-9 bg-[#002a4a] border-[#00e5ff]/20 text-white pr-9"
                placeholder="Search..."
                autoFocus
                onBlur={() => setIsSearchOpen(false)}
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-0 top-0 h-9 w-9 text-[#00e5ff]/70"
                onClick={() => setIsSearchOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </motion.div>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSearchOpen(true)}
              className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
            >
              <Search className="h-5 w-5" />
            </Button>
          )}

          <Button
            variant="ghost"
            size="icon"
            className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10 relative"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </Button>

          <Button variant="ghost" size="icon" className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10">
            <User className="h-5 w-5" />
          </Button>

          {actions}
        </div>
      </div>
    </header>
  )
}
