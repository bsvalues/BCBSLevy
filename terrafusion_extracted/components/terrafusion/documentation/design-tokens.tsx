"use client"

import { GlassmorphicContainer } from "../animation/glassmorphic-effects"

interface TokenGroup {
  name: string
  tokens: {
    name: string
    value: string
    description?: string
  }[]
}

interface DesignTokensProps {
  title: string
  description?: string
  tokenGroups: TokenGroup[]
  className?: string
}

export function DesignTokens({ title, description, tokenGroups, className = "" }: DesignTokensProps) {
  return (
    <GlassmorphicContainer className={`overflow-hidden ${className}`}>
      <div className="p-6">
        <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
        {description && <p className="text-sm text-[#00e5ff]/70 mb-4">{description}</p>}

        <div className="space-y-6">
          {tokenGroups.map((group, index) => (
            <div key={index}>
              <h4 className="text-sm font-medium text-[#00e5ff]/70 mb-2">{group.name}</h4>
              <div className="bg-[#002a4a]/50 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#00e5ff]/10">
                      <th className="text-left p-3 text-[#00e5ff]/70">Token</th>
                      <th className="text-left p-3 text-[#00e5ff]/70">Value</th>
                      <th className="text-left p-3 text-[#00e5ff]/70 hidden md:table-cell">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.tokens.map((token, tokenIndex) => (
                      <tr
                        key={tokenIndex}
                        className={`${tokenIndex !== group.tokens.length - 1 ? "border-b border-[#00e5ff]/10" : ""}`}
                      >
                        <td className="p-3 text-white font-mono text-xs">{token.name}</td>
                        <td className="p-3 text-white font-mono text-xs">{token.value}</td>
                        <td className="p-3 text-[#00e5ff]/70 hidden md:table-cell">{token.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>
    </GlassmorphicContainer>
  )
}
