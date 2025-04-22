"use client"

import { useTheme } from "./theme-provider"
import { useEffect } from "react"

// This component injects theme-specific CSS variables based on the current theme
export function ThemeStyles() {
  const { theme, mode } = useTheme()

  useEffect(() => {
    const root = document.documentElement

    // Base colors for both themes
    const baseColors = {
      light: {
        background: "#ffffff",
        foreground: "#001529",
        muted: "#f5f5f5",
        border: "#e0e0e0",
      },
      dark: {
        background: "#001529",
        foreground: "#ffffff",
        muted: "#002a4a",
        border: "#003a5a",
      },
    }

    // Standard theme colors
    const standardColors = {
      light: {
        primary: "#00b8d4",
        secondary: "#0091a7",
        accent: "#00e5ff",
      },
      dark: {
        primary: "#00e5ff",
        secondary: "#00b8d4",
        accent: "#00e5ff",
      },
    }

    // Advanced theme colors (more vibrant and with glow effects)
    const advancedColors = {
      light: {
        primary: "#00e5ff",
        secondary: "#00b8d4",
        accent: "#00f2ff",
      },
      dark: {
        primary: "#00f2ff",
        secondary: "#00e5ff",
        accent: "#80fbff",
      },
    }

    // Select the appropriate color scheme
    const baseColorScheme = baseColors[mode]
    const themeColorScheme = theme === "standard" ? standardColors[mode] : advancedColors[mode]

    // Apply colors
    root.style.setProperty("--tf-background", baseColorScheme.background)
    root.style.setProperty("--tf-foreground", baseColorScheme.foreground)
    root.style.setProperty("--tf-muted", baseColorScheme.muted)
    root.style.setProperty("--tf-border", baseColorScheme.border)
    root.style.setProperty("--tf-primary", themeColorScheme.primary)
    root.style.setProperty("--tf-secondary", themeColorScheme.secondary)
    root.style.setProperty("--tf-accent", themeColorScheme.accent)

    // Advanced theme specific styles
    if (theme === "advanced") {
      root.style.setProperty(
        "--tf-shadow-light",
        `0 0 10px ${mode === "dark" ? "rgba(0, 229, 255, 0.3)" : "rgba(0, 229, 255, 0.2)"}`,
      )
      root.style.setProperty(
        "--tf-shadow-medium",
        `0 0 20px ${mode === "dark" ? "rgba(0, 229, 255, 0.4)" : "rgba(0, 229, 255, 0.3)"}`,
      )
      root.style.setProperty(
        "--tf-shadow-strong",
        `0 0 30px ${mode === "dark" ? "rgba(0, 229, 255, 0.5)" : "rgba(0, 229, 255, 0.4)"}`,
      )
    } else {
      root.style.setProperty("--tf-shadow-light", "0 0 10px rgba(0, 0, 0, 0.1)")
      root.style.setProperty("--tf-shadow-medium", "0 0 20px rgba(0, 0, 0, 0.15)")
      root.style.setProperty("--tf-shadow-strong", "0 0 30px rgba(0, 0, 0, 0.2)")
    }
  }, [theme, mode])

  return null
}
