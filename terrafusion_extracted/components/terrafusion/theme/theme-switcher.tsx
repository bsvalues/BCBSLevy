"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Moon, Sun, Sparkles, Monitor } from "lucide-react"
import { useTheme } from "./theme-provider"
import { Button } from "@/components/ui/button"

interface ThemeSwitcherProps {
  variant?: "icon" | "button" | "dropdown"
  className?: string
}

export function ThemeSwitcher({ variant = "icon", className = "" }: ThemeSwitcherProps) {
  const { theme, mode, toggleTheme, toggleMode, setTheme, setMode } = useTheme()
  const [isOpen, setIsOpen] = useState(false)

  // Icon-only variant
  if (variant === "icon") {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleMode}
          className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10 relative"
          title={mode === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          <div className="relative w-5 h-5">
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: mode === "dark" ? 0 : 1, scale: mode === "dark" ? 0.5 : 1 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <Sun className="w-5 h-5" />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: mode === "dark" ? 1 : 0, scale: mode === "dark" ? 1 : 0.5 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <Moon className="w-5 h-5" />
            </motion.div>
          </div>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
          title={theme === "standard" ? "Switch to advanced theme" : "Switch to standard theme"}
        >
          <Sparkles className="w-5 h-5" />
        </Button>
      </div>
    )
  }

  // Button variant
  if (variant === "button") {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Button
          variant="outline"
          size="sm"
          onClick={toggleMode}
          className="text-[#00e5ff]/70 border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
        >
          {mode === "dark" ? (
            <>
              <Sun className="w-4 h-4 mr-2" /> Light Mode
            </>
          ) : (
            <>
              <Moon className="w-4 h-4 mr-2" /> Dark Mode
            </>
          )}
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={toggleTheme}
          className="text-[#00e5ff]/70 border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          {theme === "standard" ? "Advanced" : "Standard"}
        </Button>
      </div>
    )
  }

  // Dropdown variant
  return (
    <div className={`relative ${className}`}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="text-[#00e5ff]/70 border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
      >
        {mode === "dark" ? <Moon className="w-4 h-4 mr-2" /> : <Sun className="w-4 h-4 mr-2" />}
        Theme
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-[#001529] border border-[#00e5ff]/20 rounded-md shadow-lg z-50">
          <div className="p-2">
            <h3 className="text-xs font-medium text-[#00e5ff]/50 px-3 py-1">Mode</h3>
            <Button
              variant="ghost"
              className={`w-full justify-start text-left px-3 py-1.5 text-sm ${
                mode === "light" ? "bg-[#00e5ff]/20 text-[#00e5ff]" : "text-[#00e5ff]/70 hover:bg-[#00e5ff]/10"
              }`}
              onClick={() => {
                setMode("light")
                setIsOpen(false)
              }}
            >
              <Sun className="w-4 h-4 mr-2" /> Light
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-left px-3 py-1.5 text-sm ${
                mode === "dark" ? "bg-[#00e5ff]/20 text-[#00e5ff]" : "text-[#00e5ff]/70 hover:bg-[#00e5ff]/10"
              }`}
              onClick={() => {
                setMode("dark")
                setIsOpen(false)
              }}
            >
              <Moon className="w-4 h-4 mr-2" /> Dark
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-left px-3 py-1.5 text-sm text-[#00e5ff]/70 hover:bg-[#00e5ff]/10"
              onClick={() => {
                setMode(window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
                setIsOpen(false)
              }}
            >
              <Monitor className="w-4 h-4 mr-2" /> System
            </Button>

            <div className="my-1 border-t border-[#00e5ff]/10" />

            <h3 className="text-xs font-medium text-[#00e5ff]/50 px-3 py-1">Theme</h3>
            <Button
              variant="ghost"
              className={`w-full justify-start text-left px-3 py-1.5 text-sm ${
                theme === "standard" ? "bg-[#00e5ff]/20 text-[#00e5ff]" : "text-[#00e5ff]/70 hover:bg-[#00e5ff]/10"
              }`}
              onClick={() => {
                setTheme("standard")
                setIsOpen(false)
              }}
            >
              Standard
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-left px-3 py-1.5 text-sm ${
                theme === "advanced" ? "bg-[#00e5ff]/20 text-[#00e5ff]" : "text-[#00e5ff]/70 hover:bg-[#00e5ff]/10"
              }`}
              onClick={() => {
                setTheme("advanced")
                setIsOpen(false)
              }}
            >
              <Sparkles className="w-4 h-4 mr-2" /> Advanced
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
