"use client"

import { useState } from "react"
import { Activity, Bell, Calendar, Home, Info, Settings, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Animation System
import { RevealAnimation, StaggeredList } from "@/components/terrafusion/animation/use-animation-hooks"
import {
  GlassmorphicContainer,
  GlowEffect,
  FloatingElement,
  AnimatedBackground,
} from "@/components/terrafusion/animation/glassmorphic-effects"

// Expanded Component Library
import { AppBar } from "@/components/terrafusion/navigation/app-bar"
import { SideNavigation } from "@/components/terrafusion/navigation/side-navigation"
import { StatCard } from "@/components/terrafusion/data-display/stat-card"
import { ProgressIndicator } from "@/components/terrafusion/data-display/progress-indicator"
import { InfoCard } from "@/components/terrafusion/data-display/info-card"
import { ThemeSwitcher } from "@/components/terrafusion/theme/theme-switcher"

// Documentation
import { ComponentShowcase } from "@/components/terrafusion/documentation/component-showcase"
import { ColorPalette } from "@/components/terrafusion/documentation/color-palette"
import { TypographyShowcase } from "@/components/terrafusion/documentation/typography-showcase"
import { DesignTokens } from "@/components/terrafusion/documentation/design-tokens"

// Advanced UI Patterns
import { ThreeDCard } from "@/components/terrafusion/advanced/3d-card"
import { useNotifications } from "@/components/terrafusion/advanced/notification-system"
import { useModal } from "@/components/terrafusion/advanced/modal-system"
import { DashboardWidget } from "@/components/terrafusion/advanced/dashboard-widget"
import { DataTable } from "@/components/terrafusion/advanced/data-table"

// Demo navigation items
const navItems = [
  {
    label: "Dashboard",
    icon: <Home className="w-5 h-5" />,
    href: "#",
    active: true,
  },
  {
    label: "Analytics",
    icon: <Activity className="w-5 h-5" />,
    href: "#",
  },
  {
    label: "Calendar",
    icon: <Calendar className="w-5 h-5" />,
    href: "#",
    children: [
      {
        label: "Month View",
        href: "#",
      },
      {
        label: "Week View",
        href: "#",
      },
    ],
  },
  {
    label: "Notifications",
    icon: <Bell className="w-5 h-5" />,
    href: "#",
  },
  {
    label: "Settings",
    icon: <Settings className="w-5 h-5" />,
    href: "#",
  },
]

// Demo table data
const demoUsers = [
  { id: 1, name: "Alex Johnson", email: "alex@terrafusion.com", role: "Admin", status: "Active" },
  { id: 2, name: "Sarah Williams", email: "sarah@terrafusion.com", role: "User", status: "Active" },
  { id: 3, name: "Michael Brown", email: "michael@terrafusion.com", role: "Editor", status: "Inactive" },
]

// Demo table columns
const columns = [
  { header: "Name", accessorKey: "name" as const },
  { header: "Email", accessorKey: "email" as const },
  { header: "Role", accessorKey: "role" as const },
  { header: "Status", accessorKey: "status" as const },
]

// Design tokens
const designTokens = [
  {
    name: "Colors",
    tokens: [
      { name: "--tf-dark-blue", value: "#001529", description: "Primary background color" },
      { name: "--tf-medium-blue", value: "#002a4a", description: "Secondary background color" },
      { name: "--tf-light-blue", value: "#004d7a", description: "Tertiary background color" },
      { name: "--tf-primary", value: "#00e5ff", description: "Primary accent color" },
      { name: "--tf-secondary", value: "#00b8d4", description: "Secondary accent color" },
    ],
  },
  {
    name: "Spacing",
    tokens: [
      { name: "--spacing-sm", value: "8px", description: "Small spacing unit" },
      { name: "--spacing-md", value: "16px", description: "Medium spacing unit" },
      { name: "--spacing-lg", value: "32px", description: "Large spacing unit" },
    ],
  },
]

// Brand colors
const brandColors = [
  { name: "Dark Blue", value: "#001529", textColor: "#ffffff" },
  { name: "Medium Blue", value: "#002a4a", textColor: "#ffffff" },
  { name: "Light Blue", value: "#004d7a", textColor: "#ffffff" },
  { name: "Primary", value: "#00e5ff", textColor: "#001529" },
  { name: "Secondary", value: "#00b8d4", textColor: "#001529" },
]

function ShowcaseContent() {
  const { addNotification } = useNotifications()
  const { openModal } = useModal()
  const [showAuth, setShowAuth] = useState(false)
  const [showToast, setShowToast] = useState(false)
  const [showSplash, setShowSplash] = useState(false)

  // Show demo modal
  const showDemoModal = () => {
    openModal({
      title: "TerraFusion Modal",
      description: "This is a demo modal from the TerraFusion design system",
      children: (
        <div className="space-y-4">
          <p className="text-[#00e5ff]/70">
            This modal demonstrates the advanced UI patterns implemented in the TerraFusion design system.
          </p>
          <Input
            placeholder="Enter some text"
            className="bg-[#002a4a] border-[#00e5ff]/20 text-white"
          />
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
          <Button className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">Confirm</Button>
        </>
      ),
    })
  }

  return (
    <div className="min-h-screen bg-[#001529]">
      <AppBar
        title="TerraFusion Design System"
        position="sticky"
        variant="glassmorphic"
        actions={<ThemeSwitcher variant="icon" />}
      />

      <main className="container mx-auto py-8 px-4">
        <RevealAnimation>
          <h1 className="text-3xl font-bold text-white mb-2">TerraFusion Design System</h1>
          <p className="text-[#00e5ff]/70 mb-8">
            A comprehensive implementation of all phases of the TerraFusion design system enhancement plan.
          </p>
        </RevealAnimation>

        <Tabs defaultValue="animation">
          <TabsList className="bg-[#002a4a] border border-[#00e5ff]/20">
            <TabsTrigger value="animation" className="data-[state=active]:bg-[#00e5ff]/20 data-[state=active]:text-[#00e5ff]">
              Animation System
            </TabsTrigger>
            <TabsTrigger value="components" className="data-[state=active]:bg-[#00e5ff]/20 data-[state=active]:text-[#00e5ff]">
              Component Library
            </TabsTrigger>
            <TabsTrigger value="theme" className="data-[state=active]:bg-[#00e5ff]/20 data-[state=active]:text-[#00e5ff]">
              Theme System
            </TabsTrigger>
            <TabsTrigger value="documentation" className="data-[state=active]:bg-[#00e5ff]/20 data-[state=active]:text-[#00e5ff]">
              Documentation
            </TabsTrigger>
            <TabsTrigger value="advanced" className="data-[state=active]:bg-[#00e5ff]/20 data-[state=active]:text-[#00e5ff]">
              Advanced UI
            </TabsTrigger>
            <TabsTrigger value="existing" className="data-[state=active]:bg-[#00e5ff]/20 data-[state=active]:text-[#00e5ff]">
              Existing Components
            </TabsTrigger>
          </TabsList>

          {/* Animation System */}
          <TabsContent value="animation" className="mt-6">
            <StaggeredList className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ComponentShowcase
                title="Reveal Animation"
                description="Components that animate when they enter the viewport"
                component={
                  <RevealAnimation className="p-4 bg-[#00e5ff]/10 border border-[#00e5ff]/20 rounded-lg">
                    <p className="text-white">This content animates on scroll</p>
                  </RevealAnimation>
                }
                code={`<RevealAnimation direction="up" delay={0.2}>
  <p>This content animates on scroll</p>
</RevealAnimation>`}
              />

              <ComponentShowcase
                title="Staggered List"
                description="List items that animate in sequence"
                component={
                  <StaggeredList className="space-y-2">
                    <div className="p-2 bg-[#00e5ff]/10 border border-[#00e5ff]/20 rounded-lg text-white">
                      Item 1
                    </div>
                    <div className="p-2 bg-[#00e5ff]/10 border border-[#00e5ff]/20 rounded-lg text-white">
                      Item 2
                    </div>
                    <div className="p-2 bg-[#00e5ff]/10 border border-[#00e5ff]/20 rounded-lg text-white">
                      Item 3
                    </div>
                  </StaggeredList>
                }
                code={`<StaggeredList>
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</StaggeredList>`}
              />

              <ComponentShowcase
                title="Glassmorphic Container"
                description="Container with glassmorphic effect"
                component={
                  <GlassmorphicContainer className="p-4" interactive={true} hoverEffect={true}>
                    <p className="text-white">Hover over me to see the effect</p>
                  </GlassmorphicContainer>
                }
                code={`<GlassmorphicContainer interactive={true} hoverEffect={true}>
  <p>Hover over me to see the effect</p>
</GlassmorphicContainer>`}
              />

              <ComponentShowcase
                title="Glow Effect"
                description="Elements with a glowing effect"
                component={
                  <GlowEffect color="#00e5ff" intensity="medium" pulseEffect={true}>
                    <div className="p-4 bg-[#002a4a] rounded-lg text-white">
                      Element with glow effect
                    </div>
                  </GlowEffect>
                }
                code={`<GlowEffect color="#00e5ff" intensity="medium" pulseEffect={true}>
  <div>Element with glow effect</div>
</GlowEffect>`}
              />

              <ComponentShowcase
                title="Floating Element"
                description="Element that floats up and down"
                component={
                  <FloatingElement amplitude={10} duration={4}>
                    <div className="p-4 bg-[#00e5ff]/10 border border-[#00e5ff]/20 rounded-lg text-white">
                      Floating element
                    </div>
                  </FloatingElement>
                }
                code={`<FloatingElement amplitude={10} duration={4}>
  <div>Floating element</div>
</FloatingElement>`}
              />

              <ComponentShowcase
                title="Animated Background"
                description="Background with animated effects"
                component={
                  <AnimatedBackground variant="gradient" className="h-32 rounded-lg">
                    <div className="h-full flex items-center justify-center text-white">
                      Content with animated background
                    </div>
                  </AnimatedBackground>
                }
                code={`<AnimatedBackground variant="gradient">
  <div>Content with animated background</div>
</AnimatedBackground>`}
              />
            </StaggeredList>
          </TabsContent>

          {/* Component Library */}
          <TabsContent value="components" className="mt-6">
            <StaggeredList className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ComponentShowcase
                title="App Bar"
                description="Navigation bar for applications"
                component={
                  <AppBar
                    title="App Title"
                    variant="default"
                    className="w-full"
                    onMenuClick={() => {}}
                  />
                }
                code={`<AppBar
  title="App Title"
  variant="default"
  onMenuClick={() => {}}
/>`}
              />

              <ComponentShowcase
                title="Side Navigation"
                description="Vertical navigation menu"
                component={
                  <div className="h-64 overflow-hidden">
                    <SideNavigation items={navItems} className="h-full" />
                  </div>
                }
                code={`<SideNavigation items={navItems} />`}
              />

              <ComponentShowcase
                title="Stat Card"
                description="Card displaying a key metric"
                component={
                  <StatCard
                    title="Active Users"
                    value={1250}
                    previousValue={1180}
                    trend="up"
                    trendValue={5.9}
                    icon={<User className="w-5 h-5" />}
                  />
                }
                code={`<StatCard
  title="Active Users"
  value={1250}
  previousValue={1180}
  trend="up"
  trendValue={5.9}
  icon={<User />}
/>`}
              />

              <ComponentShowcase
                title="Progress Indicator"
                description="Visual representation of progress"
                component={
                  <div className="flex flex-col gap-4">
                    <ProgressIndicator value={75} label="Line Progress" />
                    <div className="flex gap-4">
                      <ProgressIndicator value={65} variant="circle" size="md" />
                      <ProgressIndicator value={40} variant="semicircle" size="md" />
                    </div>
                  </div>
                }
                code={`<ProgressIndicator value={75} label="Line Progress" />
<ProgressIndicator value={65} variant="circle" size="md" />
<ProgressIndicator value={40} variant="semicircle" size="md" />`}
              />

              <ComponentShowcase
                title="Info Card"
                description="Card displaying information with actions"
                component={
                  <InfoCard
                    title="Information"
                    content="This is an information card with actions."
                    icon={<Info className="w-5 h-5" />}
                    actions={
                      <Button size="sm" className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">
                        Action
                      </Button>
                    }
                  />
                }
                code={`<InfoCard
  title="Information"
  content="This is an information card with actions."
  icon={<Info />}
  actions={<Button>Action</Button>}
/>`}
              />
            </StaggeredList>
          </TabsContent>

          {/* Theme System */}
          <TabsContent value="theme" className="mt-6">
            <StaggeredList className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ComponentShowcase
                title="Theme Switcher (Icon)"
                description="Toggle between light/dark mode and standard/advanced themes"
                component={<ThemeSwitcher variant="icon" />}
                code={`<ThemeSwitcher variant="icon" />`}
              />

              <ComponentShowcase
                title="Theme Switcher (Button)"
                description="Button variant of the theme switcher"
                component={<ThemeSwitcher variant="button" />}
                code={`<ThemeSwitcher variant="button" />`}
              />

              <ComponentShowcase
                title="Theme Switcher (Dropdown)"
                description="Dropdown variant of the theme switcher"
                component={<ThemeSwitcher variant="dropdown" />}
                code={`<ThemeSwitcher variant="dropdown" />`}
              />

              <ColorPalette
                title="TerraFusion Color Palette"
                description="Core colors of the TerraFusion design system"
                colors={brandColors}
              />
            </StaggeredList>
          </TabsContent>

          {/* Documentation */}
          <TabsContent value="documentation" className="mt-6">
            <StaggeredList className="grid grid-cols-1 gap-6">
              <TypographyShowcase
                title="Typography"
                description="Text styles used in the TerraFusion design system"
              />

              <DesignTokens
                title="Design Tokens"
                description="Core design tokens used throughout the system"
                tokenGroups={designTokens}
              />

              <ComponentShowcase
                title="Component Showcase"
                description="Documentation component for showcasing other components"
                component={
                  <Button className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">
                    Example Button
                  </Button>
                }
                code={`<Button className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]">
  Example Button
</Button>`}
              />
            </StaggeredList>
          </TabsContent>

          {/* Advanced UI */}
          <TabsContent value="advanced" className="mt-6">
            <StaggeredList className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ComponentShowcase
                title="3D Card"
                description="Card with 3D perspective effect"
                component={
                  <ThreeDCard
                    title="3D Card"
                    description="Hover over me to see the 3D effect"
                    icon={<Settings className="w-5 h-5" />}
                  />
                }
                code={`<ThreeDCard
  title="3D Card"
  description="Hover over me to see the 3D effect"
  icon={<Settings />}
/>`}
              />

              <ComponentShowcase
                title="Notification System"
                description="System for displaying notifications"
                component={
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      className="bg-green-500 hover:bg-green-600 text-white"
                      onClick={() => {
                        addNotification({
                          type: "success",
                          title: "Success",
                          message: "Operation completed successfully",
                          duration: 3000,
                        })
                      }}
                    >
                      Success
                    </Button>
                    <Button
                      size="sm"
                      className="bg-red-500 hover:bg-red-600 text-white"
                      onClick={() => {
                        addNotification({
                          type: "error",
                          title: "Error",
                          message: "Something went wrong",
                          duration: 3000,
                        })
                      }}
                    >
                      Error
                    </Button>
                  </div>
                }
                code={`// Add notification
addNotification({
  type: "success",
  title: "Success",
  message: "Operation completed successfully",
  duration: 3000,
})`}
              />

              <ComponentShowcase
                title="Modal System"
                description="System for displaying modal dialogs"
                component={
                  <Button
                    className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]"
                    onClick={showDemoModal}
                  >
                    Open Modal
                  </Button>
                }
                code={`// Open modal
openModal({
  title: "Modal Title",
  description: "Modal description",
  children: <div>Modal content</div>,
  footer: (
    <>
      <Button variant="outline">Cancel</Button>
      <Button>Confirm</Button>
    </>
  ),
})`}
              />

              <ComponentShowcase
                title="Dashboard Widget"
                description="Widget for displaying dashboard metrics"
                component={
                  <DashboardWidget
                    title="Server Uptime"
                    value={98.5}
                    previousValue={96}
                    unit="%"
                    icon={<Activity className="w-5 h-5" />}
                  />
                }
                code={`<DashboardWidget
  title="Server Uptime"
  value={98.5}
  previousValue={96}
  unit="%"
  icon={<Activity />}
/>`}
              />

              <ComponentShowcase
                title="Data Table"
                description="Table for displaying data with sorting and pagination"
                component={
                  <DataTable
                    data={demoUsers}
                    columns={columns}
                    searchable
                    searchKeys={["name", "email"]}
                  />
                }
                code={`<DataTable
  data={users}
  columns={columns}
  searchable
  searchKeys={["name", "email"]}
/>`}
              />
            </StaggeredList>
          </TabsContent>

          {/* Existing Components */}
          <TabsContent value="existing" className="mt-6">
            <StaggeredList className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ComponentShowcase
                title="Splash Screen"
                description="Loading screen for modules"
                component={
                  <Button
                    className="bg-[#00e5ff] hover:bg-[#00b8d4] text-[#001529]"
                    onClick={() => setShowSplash(true)}
                  >
                    Show Splash Screen
                  </Button>
