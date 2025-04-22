"use client"

import type React from "react"

import { createContext, useContext, useEffect, useState } from "react"

type Theme = "standard" | "advanced"
type ThemeMode = "light" | "dark"

interface ThemeContextType {
  theme: Theme
  mode: ThemeMode
  setTheme: (theme: Theme) => void
  setMode: (mode: ThemeMode) => void
  toggleTheme: () => void
  toggleMode: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
  defaultMode?: ThemeMode
}

export function TerraFusionThemeProvider({
  children,
  defaultTheme = "standard",
  defaultMode = "dark",
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(defaultTheme)
  const [mode, setModeState] = useState<ThemeMode>(defaultMode)

  // Initialize theme from localStorage if available
  useEffect(() => {
    const savedTheme = localStorage.getItem("tf-theme") as Theme | null
    const savedMode = localStorage.getItem("tf-mode") as ThemeMode | null

    if (savedTheme) {
      setThemeState(savedTheme)
    }

    if (savedMode) {
      setModeState(savedMode)
      document.documentElement.classList.toggle("dark", savedMode === "dark")
    } else {
      document.documentElement.classList.toggle("dark", defaultMode === "dark")
    }
  }, [defaultMode])

  // Set theme
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    localStorage.setItem("tf-theme", newTheme)
    document.documentElement.setAttribute("data-theme", newTheme)
  }

  // Set mode
  const setMode = (newMode: ThemeMode) => {
    setModeState(newMode)
    localStorage.setItem("tf-mode", newMode)
    document.documentElement.classList.toggle("dark", newMode === "dark")
  }

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = theme === "standard" ? "advanced" : "standard"
    setTheme(newTheme)
  }

  // Toggle mode
  const toggleMode = () => {
    const newMode = mode === "light" ? "dark" : "light"
    setMode(newMode)
  }

  return (
    <ThemeContext.Provider
      value={{
        theme,
        mode,
        setTheme,
        setMode,
        toggleTheme,
        toggleMode,
      }}
    >
      <div data-theme={theme} className={mode === "dark" ? "dark" : ""}>
        {children}
      </div>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a TerraFusionThemeProvider")
  }
  return context
}
