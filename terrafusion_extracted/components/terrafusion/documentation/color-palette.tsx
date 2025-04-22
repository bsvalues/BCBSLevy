"use client"

import { useState } from "react"
import { Copy, Check } from "lucide-react"
import { GlassmorphicContainer } from "../animation/glassmorphic-effects"

interface ColorSwatch {
  name: string
  value: string
  textColor?: string
}

interface ColorPaletteProps {
  title: string
  description?: string
  colors: ColorSwatch[]
  className?: string
}

export function ColorPalette({ title, description, colors, className = "" }: ColorPaletteProps) {
  return (
    <GlassmorphicContainer className={`overflow-hidden ${className}`}>
      <div className="p-6">
        <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
        {description && <p className="text-sm text-[#00e5ff]/70 mb-4">{description}</p>}

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {colors.map((color, index) => (
            <ColorSwatch key={index} name={color.name} value={color.value} textColor={color.textColor} />
          ))}
        </div>
      </div>
    </GlassmorphicContainer>
  )
}

function ColorSwatch({ name, value, textColor = "#ffffff" }: ColorSwatch) {
  const [isCopied, setIsCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(value)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <div className="flex flex-col">
      <div
        className="h-20 rounded-t-lg flex items-center justify-center cursor-pointer"
        style={{ backgroundColor: value }}
        onClick={handleCopy}
      >
        {isCopied ? (
          <Check className="w-6 h-6" style={{ color: textColor }} />
        ) : (
          <Copy className="w-5 h-5 opacity-70" style={{ color: textColor }} />
        )}
      </div>
      <div className="bg-[#002a4a] p-2 rounded-b-lg">
        <p className="text-xs font-medium text-white">{name}</p>
        <p className="text-xs text-[#00e5ff]/70">{value}</p>
      </div>
    </div>
  )
}
