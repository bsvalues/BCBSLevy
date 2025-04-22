"use client"

import { GlassmorphicContainer } from "../animation/glassmorphic-effects"

interface TypographyShowcaseProps {
  title: string
  description?: string
  className?: string
}

export function TypographyShowcase({ title, description, className = "" }: TypographyShowcaseProps) {
  return (
    <GlassmorphicContainer className={`overflow-hidden ${className}`}>
      <div className="p-6">
        <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
        {description && <p className="text-sm text-[#00e5ff]/70 mb-4">{description}</p>}

        <div className="space-y-6">
          <div>
            <h4 className="text-sm font-medium text-[#00e5ff]/70 mb-2">Headings</h4>
            <div className="space-y-4 bg-[#002a4a]/50 p-4 rounded-lg">
              <div>
                <h1 className="text-4xl font-bold text-white">Heading 1</h1>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-4xl font-bold</p>
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white">Heading 2</h2>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-3xl font-bold</p>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Heading 3</h3>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-2xl font-bold</p>
              </div>
              <div>
                <h4 className="text-xl font-medium text-white">Heading 4</h4>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-xl font-medium</p>
              </div>
              <div>
                <h5 className="text-lg font-medium text-white">Heading 5</h5>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-lg font-medium</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-[#00e5ff]/70 mb-2">Body Text</h4>
            <div className="space-y-4 bg-[#002a4a]/50 p-4 rounded-lg">
              <div>
                <p className="text-base text-white">
                  Base paragraph text. TerraFusion provides a comprehensive design system with consistent typography,
                  colors, and components.
                </p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-base</p>
              </div>
              <div>
                <p className="text-sm text-white">
                  Small paragraph text. Use this for secondary information or supporting content within your
                  application.
                </p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-sm</p>
              </div>
              <div>
                <p className="text-xs text-white">
                  Extra small text. Ideal for captions, footnotes, or metadata that should be visually de-emphasized.
                </p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-xs</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-[#00e5ff]/70 mb-2">Text Styles</h4>
            <div className="space-y-4 bg-[#002a4a]/50 p-4 rounded-lg">
              <div>
                <p className="font-bold text-white">Bold text for emphasis</p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">font-bold</p>
              </div>
              <div>
                <p className="font-medium text-white">Medium weight text for subtitles</p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">font-medium</p>
              </div>
              <div>
                <p className="italic text-white">Italic text for quotes or emphasis</p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">italic</p>
              </div>
              <div>
                <p className="text-[#00e5ff] font-medium">Colored text for highlights</p>
                <p className="text-xs text-[#00e5ff]/50 mt-1">text-[#00e5ff]</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </GlassmorphicContainer>
  )
}
