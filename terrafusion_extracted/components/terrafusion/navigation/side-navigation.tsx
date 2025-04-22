"use client"

import type React from "react"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface NavItem {
  label: string
  icon?: React.ReactNode
  href?: string
  active?: boolean
  children?: NavItem[]
}

interface SideNavigationProps {
  items: NavItem[]
  collapsed?: boolean
  onItemClick?: (item: NavItem) => void
  className?: string
}

export function SideNavigation({ items, collapsed = false, onItemClick, className = "" }: SideNavigationProps) {
  return (
    <nav
      className={`bg-[#001529] border-r border-[#00e5ff]/20 h-full transition-all duration-300 ${
        collapsed ? "w-16" : "w-64"
      } ${className}`}
    >
      <div className="py-4">
        <ul className="space-y-1">
          {items.map((item, index) => (
            <NavItemComponent key={index} item={item} collapsed={collapsed} onItemClick={onItemClick} />
          ))}
        </ul>
      </div>
    </nav>
  )
}

interface NavItemComponentProps {
  item: NavItem
  collapsed: boolean
  depth?: number
  onItemClick?: (item: NavItem) => void
}

function NavItemComponent({ item, collapsed, depth = 0, onItemClick }: NavItemComponentProps) {
  const [isOpen, setIsOpen] = useState(false)
  const hasChildren = item.children && item.children.length > 0

  const handleClick = () => {
    if (hasChildren) {
      setIsOpen(!isOpen)
    }
    if (onItemClick) {
      onItemClick(item)
    }
  }

  return (
    <li>
      <Button
        variant="ghost"
        className={`w-full justify-start px-4 py-2 h-10 ${
          item.active
            ? "bg-[#00e5ff]/20 text-[#00e5ff]"
            : "text-[#00e5ff]/70 hover:bg-[#00e5ff]/10 hover:text-[#00e5ff]"
        } ${depth > 0 ? "pl-8" : ""}`}
        onClick={handleClick}
      >
        {item.icon && <span className="mr-3">{item.icon}</span>}
        {!collapsed && (
          <>
            <span className="flex-1 text-left">{item.label}</span>
            {hasChildren && (
              <span className="ml-2">
                {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </span>
            )}
          </>
        )}
      </Button>

      {/* Submenu */}
      {!collapsed && hasChildren && (
        <AnimatePresence initial={false}>
          {isOpen && (
            <motion.ul
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              {item.children?.map((child, index) => (
                <NavItemComponent
                  key={index}
                  item={child}
                  collapsed={collapsed}
                  depth={depth + 1}
                  onItemClick={onItemClick}
                />
              ))}
            </motion.ul>
          )}
        </AnimatePresence>
      )}
    </li>
  )
}
