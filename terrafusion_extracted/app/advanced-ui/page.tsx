"use client"

import { useState } from "react"
import {
  Activity,
  AlertCircle,
  Bell,
  Check,
  ChevronRight,
  Database,
  Server,
  Settings,
  Shield,
  Users,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThreeDCard } from "@/components/terrafusion/advanced/3d-card"
import { NotificationProvider, useNotifications } from "@/components/terrafusion/advanced/notification-system"
import { ModalProvider, useModal, useConfirmation } from "@/components/terrafusion/advanced/modal-system"
import { DashboardWidget } from "@/components/terrafusion/advanced/dashboard-widget"
import { DataTable } from "@/components/terrafusion/advanced/data-table"
import Image from "next/image"

// Demo data for table
const demoUsers = [
  { id: 1, name: "Alex Johnson", email: "alex@terrafusion.com", role: "Admin", status: "Active" },
  { id: 2, name: "Sarah Williams", email: "sarah@terrafusion.com", role: "User", status: "Active" },
  { id: 3, name: "Michael Brown", email: "michael@terrafusion.com", role: "Editor", status: "Inactive" },
  { id: 4, name: "Emily Davis", email: "emily@terrafusion.com", role: "User", status: "Active" },
  { id: 5, name: "David Wilson", email: "david@terrafusion.com", role: "Admin", status: "Active" },
  { id: 6, name: "Jessica Taylor", email: "jessica@terrafusion.com", role: "User", status: "Pending" },
  { id: 7, name: "Ryan Martinez", email: "ryan@terrafusion.com", role: "Editor", status: "Active" },
]

// Table columns
const columns = [
  { header: "Name", accessorKey: "name" as const },
  { header: "Email", accessorKey: "email" as const },
  {
    header: "Role",
    accessorKey: "role" as const,
    cell: (user: (typeof demoUsers)[0]) => (
      <span
        className={`px-2 py-1 rounded-full text-xs ${
          user.role === "Admin"
            ? "bg-[#00e5ff]/20 text-[#00e5ff]"
            : user.role === "Editor"
              ? "bg-amber-500/20 text-amber-500"
              : "bg-blue-500/20 text-blue-500"
        }`}
      >
        {user.role}
      </span>
    ),
  },
  {
    header: "Status",
    accessorKey: "status" as const,
    cell: (user: (typeof demoUsers)[0]) => (
      <span
        className={`flex items-center gap-1 ${
          user.status === "Active" ? "text-green-500" : user.status === "Inactive" ? "text-red-500" : "text-amber-500"
        }`}
      >
        <span
          className={`w-2 h-2 rounded-full ${
            user.status === "Active" ? "bg-green-500" : user.status === "Inactive" ? "bg-red-500" : "bg-amber-500"
          }`}
        />
        {user.status}
      </span>
    ),
  },
  {
    header: "Actions",
    accessorKey: "id" as const,
    cell: () => (
      <Button variant="ghost" size="sm" className="h-8 px-2 text-[#00e5ff]">
        <ChevronRight className="w-4 h-4" />
      </Button>
    ),
  },
]

// Demo component to showcase all advanced UI patterns
function AdvancedUIDemo() {
  const { addNotification } = useNotifications()
  const { openModal } = useModal()
  const { confirm } = useConfirmation()

  const [serverStatus, setServerStatus] = useState(98)
  const [userCount, setUserCount] = useState(1250)
  const [cpuUsage, setCpuUsage] = useState(42)

  // Demo function to simulate data refresh
  const refreshServerStatus = async () => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    const newValue = Math.floor(Math.random() * 10) + 90 // Random between 90-99
    return newValue
  }

  const refreshUserCount = async () => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    const change = Math.floor(Math.random() * 100) - 20 // Random between -20 and 80
    return userCount + change
  }

  const refreshCpuUsage = async () => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    const newValue = Math.floor(Math.random() * 60) + 20 // Random between 20-80
    return newValue
  }

  // Show demo modal
  const showDemoModal = () => {
    openModal({
      title: "System Configuration",
      description: "Manage your TerraFusion system settings",
      size: "lg",
      children: (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ThreeDCard
              title="API Settings"
              description="Configure API endpoints and authentication"
              icon={<Server className="w-5 h-5" />}
            >
              <Button size="sm" className="mt-2 bg-[#00e5ff]/20 text-[#00e5ff] hover:bg-[#00e5ff]/30">
                Configure
              </Button>
            </ThreeDCard>

            <ThreeDCard
              title="User Permissions"
              description="Manage role-based access control"
              icon={<Shield className="w-5 h-5" />}
            >
              <Button size="sm" className="mt-2 bg-[#00e5ff]/20 text-[#00e5ff] hover:bg-[#00e5ff]/30">
                Configure
              </Button>
            </ThreeDCard>
          </div>

          <div className="p-4 rounded-lg bg-[#00e5ff]/5 border border-[#00e5ff]/20">
            <h4 className="text-sm font-medium text-white mb-2">System Information</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-[#00e5ff]/70">Version</div>
              <div className="text-white">TerraFusion v2.5.0</div>

              <div className="text-[#00e5ff]/70">Environment</div>
              <div className="text-white">Production</div>

              <div className="text-[#00e5ff]/70">Last Updated</div>
              <div className="text-white">2023-04-22 14:30 UTC</div>
            </div>
          </div>
        </div>
      ),
      footer: (
        <>
          <Button
            variant="outline"
            className="text-[#00e5ff]/70 border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
          >
            Cancel
          </Button>
          <Button className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">Save Changes</Button>
        </>
      ),
    })
  }

  // Show demo confirmation
  const showDemoConfirmation = () => {
    confirm({
      title: "Confirm Action",
      message: "Are you sure you want to restart the server? This will cause a brief downtime.",
      onConfirm: () => {
        addNotification({
          type: "success",
          title: "Server Restarting",
          message: "The server is now restarting. This may take a few minutes.",
          duration: 5000,
        })
      },
      type: "warning",
    })
  }

  return (
    <div className="min-h-screen bg-[#001529]">
      <header className="bg-[#001529] border-b border-[#00e5ff]/20 p-6 flex items-center">
        <div className="w-10 h-10 mr-4">
          <Image src="/terrafusion-logo.png" alt="TerraFusion Logo" width={40} height={40} className="object-contain" />
        </div>
        <h1 className="text-2xl font-bold text-white">TerraFusion Advanced UI</h1>
      </header>

      <main className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h2 className="text-xl font-medium text-white mb-4">3D Glassmorphic Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <ThreeDCard
              title="System Performance"
              description="Monitor and optimize your system resources"
              icon={<Activity className="w-5 h-5" />}
            >
              <Button
                size="sm"
                className="mt-2 bg-[#00e5ff]/20 text-[#00e5ff] hover:bg-[#00e5ff]/30"
                onClick={() => {
                  addNotification({
                    type: "info",
                    title: "Performance Report",
                    message: "Generating system performance report. This may take a moment.",
                    duration: 5000,
                  })
                }}
              >
                Generate Report
              </Button>
            </ThreeDCard>

            <ThreeDCard
              title="User Management"
              description="Add, remove, and manage user permissions"
              icon={<Users className="w-5 h-5" />}
            >
              <Button
                size="sm"
                className="mt-2 bg-[#00e5ff]/20 text-[#00e5ff] hover:bg-[#00e5ff]/30"
                onClick={showDemoModal}
              >
                Manage Users
              </Button>
            </ThreeDCard>

            <ThreeDCard
              title="Database Status"
              description="View and manage database connections"
              icon={<Database className="w-5 h-5" />}
            >
              <Button
                size="sm"
                className="mt-2 bg-[#00e5ff]/20 text-[#00e5ff] hover:bg-[#00e5ff]/30"
                onClick={showDemoConfirmation}
              >
                Restart Server
              </Button>
            </ThreeDCard>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-medium text-white mb-4">Dashboard Widgets</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <DashboardWidget
              title="Server Uptime"
              value={serverStatus}
              previousValue={96}
              unit="%"
              icon={<Server className="w-5 h-5" />}
              refreshInterval={30000}
              onRefresh={refreshServerStatus}
            />

            <DashboardWidget
              title="Active Users"
              value={userCount}
              previousValue={1180}
              icon={<Users className="w-5 h-5" />}
              refreshInterval={15000}
              onRefresh={refreshUserCount}
            />

            <DashboardWidget
              title="CPU Usage"
              value={cpuUsage}
              previousValue={38}
              unit="%"
              icon={<Activity className="w-5 h-5" />}
              refreshInterval={10000}
              onRefresh={refreshCpuUsage}
            />
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-medium text-white mb-4">Data Table</h2>
          <DataTable data={demoUsers} columns={columns} searchable searchKeys={["name", "email", "role", "status"]} />
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-medium text-white mb-4">Notification System</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              className="bg-green-500 hover:bg-green-600 text-white"
              onClick={() => {
                addNotification({
                  type: "success",
                  title: "Operation Successful",
                  message: "The data has been successfully processed and saved.",
                  duration: 5000,
                })
              }}
            >
              <Check className="w-4 h-4 mr-2" />
              Success Notification
            </Button>

            <Button
              className="bg-red-500 hover:bg-red-600 text-white"
              onClick={() => {
                addNotification({
                  type: "error",
                  title: "Operation Failed",
                  message: "There was an error processing your request. Please try again.",
                  duration: 5000,
                })
              }}
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Error Notification
            </Button>

            <Button
              className="bg-blue-500 hover:bg-blue-600 text-white"
              onClick={() => {
                addNotification({
                  type: "info",
                  title: "Information",
                  message: "Your system is currently processing a background task.",
                  duration: 5000,
                })
              }}
            >
              <Bell className="w-4 h-4 mr-2" />
              Info Notification
            </Button>

            <Button
              className="bg-amber-500 hover:bg-amber-600 text-white"
              onClick={() => {
                addNotification({
                  type: "warning",
                  title: "Warning",
                  message: "Your storage is almost full. Please free up some space.",
                  duration: 5000,
                })
              }}
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Warning Notification
            </Button>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-medium text-white mb-4">Modal System</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]" onClick={showDemoModal}>
              <Settings className="w-4 h-4 mr-2" />
              Open Configuration Modal
            </Button>

            <Button className="bg-amber-500 hover:bg-amber-600 text-white" onClick={showDemoConfirmation}>
              <AlertCircle className="w-4 h-4 mr-2" />
              Show Confirmation Dialog
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}

// Wrap with providers
export default function AdvancedUIPage() {
  return (
    <NotificationProvider>
      <ModalProvider>
        <AdvancedUIDemo />
      </ModalProvider>
    </NotificationProvider>
  )
}
