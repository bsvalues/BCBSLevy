"use client"

import type React from "react"

import { useState } from "react"
import { motion } from "framer-motion"
import { Code, Copy, Check, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { GlassmorphicContainer } from "../animation/glassmorphic-effects"

interface ComponentShowcaseProps {
  title: string
  description?: string
  component: React.ReactNode
  code: string
  defaultOpen?: boolean
  className?: string
}

export function ComponentShowcase({
  title,
  description,
  component,
  code,
  defaultOpen = false,
  className = "",
}: ComponentShowcaseProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const [isCopied, setIsCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <GlassmorphicContainer className={`overflow-hidden ${className}`}>
      <div className="p-6">
        <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
        {description && <p className="text-sm text-[#00e5ff]/70 mb-4">{description}</p>}

        {/* Component preview */}
        <div className="p-6 bg-[#002a4a]/50 rounded-lg mb-4 flex items-center justify-center">{component}</div>

        {/* Code section */}
        <div className="border border-[#00e5ff]/20 rounded-lg overflow-hidden">
          <div className="flex items-center justify-between p-2 bg-[#002a4a]/50 border-b border-[#00e5ff]/20">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
            >
              <Code className="w-4 h-4 mr-2" />
              <span>Code</span>
              <ChevronDown className={`w-4 h-4 ml-2 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
            >
              {isCopied ? (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-2" />
                  <span>Copy</span>
                </>
              )}
            </Button>
          </div>

          <motion.div
            initial={false}
            animate={{ height: isOpen ? "auto" : 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <pre className="p-4 text-sm text-[#00e5ff]/70 overflow-x-auto">{code}</pre>
          </motion.div>
        </div>
      </div>
    </GlassmorphicContainer>
  )
}
