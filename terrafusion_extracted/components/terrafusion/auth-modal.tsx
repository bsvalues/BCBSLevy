"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Image from "next/image"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/64 flex items-center justify-center p-4 z-50">
      <div
        className="w-full max-w-md bg-[#001529]/80 backdrop-blur-[18px] border border-[#00e5ff]/20 rounded-[24px] p-8 flex flex-col gap-6"
        style={{ boxShadow: "0 0 20px rgba(0,229,255,0.2)" }}
      >
        {/* TerraFusion Logo */}
        <div className="w-16 h-16 mx-auto relative">
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png"
            alt="TerraFusion Logo"
            width={64}
            height={64}
            className="object-contain"
          />
        </div>

        <h2 className="text-2xl font-bold text-white text-center">Sign In</h2>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-12 px-4 bg-[#002a4a] border-[#00e5ff]/30 text-white focus:border-[#00e5ff]"
              placeholder="your@email.com"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-12 px-4 bg-[#002a4a] border-[#00e5ff]/30 text-white focus:border-[#00e5ff]"
              placeholder="••••••••"
            />
          </div>
        </div>

        <div className="space-y-4">
          <Button
            className="w-full h-12 bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529] font-medium transition-colors duration-200 ease-in-out"
            onClick={() => console.log("Login clicked")}
          >
            Sign In
          </Button>

          <Button
            variant="ghost"
            className="w-full text-[#00e5ff]/80 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
            onClick={onClose}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}
