"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { SplashScreen } from "@/components/terrafusion/splash-screen"
import { AuthModal } from "@/components/terrafusion/auth-modal"
import { NotificationToast } from "@/components/terrafusion/notification-toast"
import { DashboardCard } from "@/components/terrafusion/dashboard-card"
import Image from "next/image"

export default function TerraFusionShowcase() {
  const [showSplash, setShowSplash] = useState(false)
  const [showAuth, setShowAuth] = useState(false)
  const [showToast, setShowToast] = useState(false)
  const [activeTab, setActiveTab] = useState<string>("brand")

  const renderComponent = () => {
    switch (activeTab) {
      case "brand":
        return (
          <div className="flex flex-col items-center justify-center p-8 bg-[#001529] rounded-lg">
            <h2 className="text-xl font-bold mb-8 text-white">TerraFusion Brand Assets</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="flex flex-col items-center">
                <h3 className="text-lg font-medium mb-4 text-[#00e5ff]">Primary Logo</h3>
                <Image
                  src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png"
                  alt="TerraFusion Logo"
                  width={300}
                  height={300}
                  className="object-contain"
                />
              </div>
              <div className="flex flex-col items-center">
                <h3 className="text-lg font-medium mb-4 text-[#00e5ff]">Logo Variations</h3>
                <Image
                  src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-0h7tzBkj83NtRDd6ZwGUXg67nKeW5j.png"
                  alt="TerraFusion Logo Variations"
                  width={300}
                  height={300}
                  className="object-contain"
                />
              </div>
            </div>
          </div>
        )
      case "splash":
        return showSplash ? (
          <SplashScreen moduleName="Analytics Module" onComplete={() => setShowSplash(false)} />
        ) : (
          <div className="flex flex-col items-center justify-center p-8 bg-[#001529] rounded-lg">
            <h2 className="text-xl font-bold mb-4 text-white">Module Splash Screen</h2>
            <Button onClick={() => setShowSplash(true)} className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">
              Show Splash Screen
            </Button>
          </div>
        )
      case "auth":
        return (
          <div className="flex flex-col items-center justify-center p-8 bg-[#001529] rounded-lg">
            <h2 className="text-xl font-bold mb-4 text-white">Auth / Login Modal</h2>
            <Button onClick={() => setShowAuth(true)} className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">
              Show Auth Modal
            </Button>
            <AuthModal isOpen={showAuth} onClose={() => setShowAuth(false)} />
          </div>
        )
      case "toast":
        return (
          <div className="flex flex-col items-center justify-center p-8 bg-[#001529] rounded-lg">
            <h2 className="text-xl font-bold mb-4 text-white">Notification Toast</h2>
            <Button onClick={() => setShowToast(true)} className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">
              Show Toast Notification
            </Button>
            {showToast && (
              <NotificationToast message="Operation completed successfully!" onClose={() => setShowToast(false)} />
            )}
          </div>
        )
      case "dashboard":
        return (
          <div className="flex flex-col items-center justify-center p-8 bg-[#001529] rounded-lg">
            <h2 className="text-xl font-bold mb-4 text-white">Analytics Dashboard Card</h2>
            <DashboardCard title="System Uptime" metric="98%" description="Last 30 days performance" />
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-[#001529]">
      <header className="bg-[#001529] border-b border-[#00e5ff]/20 p-6 flex items-center">
        <div className="w-10 h-10 mr-4">
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png"
            alt="TerraFusion Logo"
            width={40}
            height={40}
            className="object-contain"
          />
        </div>
        <h1 className="text-2xl font-bold text-white">TerraFusion Design System</h1>
      </header>

      <main className="container mx-auto py-8 px-4">
        <div className="flex flex-wrap gap-2 mb-8">
          {[
            { id: "brand", label: "Brand Assets" },
            { id: "splash", label: "Splash Screen" },
            { id: "auth", label: "Auth Modal" },
            { id: "toast", label: "Toast" },
            { id: "dashboard", label: "Dashboard Card" },
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "outline"}
              onClick={() => setActiveTab(tab.id)}
              className={
                activeTab === tab.id
                  ? "bg-[#00e5ff] text-[#001529] hover:bg-[#00b8d4]"
                  : "text-[#00e5ff] border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
              }
            >
              {tab.label}
            </Button>
          ))}
        </div>

        <div className="mt-8">{renderComponent()}</div>
      </main>
    </div>
  )
}
