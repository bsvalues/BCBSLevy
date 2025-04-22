"use client"

import type React from "react"

import { useState, useMemo } from "react"
import { ChevronDown, ChevronUp, ChevronsUpDown, Search } from "lucide-react"
import { Input } from "@/components/ui/input"

interface Column<T> {
  header: string
  accessorKey: keyof T
  cell?: (item: T) => React.ReactNode
  sortable?: boolean
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  searchable?: boolean
  searchKeys?: Array<keyof T>
  pagination?: boolean
  pageSize?: number
  className?: string
}

export function DataTable<T>({
  data,
  columns,
  searchable = true,
  searchKeys,
  pagination = true,
  pageSize = 5,
  className = "",
}: DataTableProps<T>) {
  const [sortConfig, setSortConfig] = useState<{
    key: keyof T | null
    direction: "asc" | "desc" | null
  }>({
    key: null,
    direction: null,
  })

  const [searchQuery, setSearchQuery] = useState("")
  const [currentPage, setCurrentPage] = useState(1)

  // Handle sorting
  const handleSort = (key: keyof T) => {
    let direction: "asc" | "desc" | null = "asc"

    if (sortConfig.key === key) {
      if (sortConfig.direction === "asc") {
        direction = "desc"
      } else if (sortConfig.direction === "desc") {
        direction = null
      }
    }

    setSortConfig({ key, direction })
  }

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let processedData = [...data]

    // Filter by search query
    if (searchQuery && searchKeys?.length) {
      processedData = processedData.filter((item) => {
        return searchKeys.some((key) => {
          const value = item[key]
          if (typeof value === "string") {
            return value.toLowerCase().includes(searchQuery.toLowerCase())
          }
          if (typeof value === "number") {
            return value.toString().includes(searchQuery)
          }
          return false
        })
      })
    }

    // Sort data
    if (sortConfig.key && sortConfig.direction) {
      processedData.sort((a, b) => {
        const aValue = a[sortConfig.key as keyof T]
        const bValue = b[sortConfig.key as keyof T]

        if (aValue === bValue) return 0

        if (sortConfig.direction === "asc") {
          return aValue < bValue ? -1 : 1
        } else {
          return aValue > bValue ? -1 : 1
        }
      })
    }

    return processedData
  }, [data, searchQuery, searchKeys, sortConfig])

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return filteredAndSortedData

    const startIndex = (currentPage - 1) * pageSize
    return filteredAndSortedData.slice(startIndex, startIndex + pageSize)
  }, [filteredAndSortedData, currentPage, pageSize, pagination])

  // Calculate total pages
  const totalPages = useMemo(() => {
    return Math.ceil(filteredAndSortedData.length / pageSize)
  }, [filteredAndSortedData, pageSize])

  // Generate page numbers
  const pageNumbers = useMemo(() => {
    const pages = []
    const maxVisiblePages = 5

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Always show first page
      pages.push(1)

      // Calculate start and end of visible pages
      let start = Math.max(2, currentPage - 1)
      let end = Math.min(totalPages - 1, currentPage + 1)

      // Adjust if at edges
      if (currentPage <= 2) {
        end = 4
      } else if (currentPage >= totalPages - 1) {
        start = totalPages - 3
      }

      // Add ellipsis if needed
      if (start > 2) {
        pages.push("...")
      }

      // Add visible pages
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      // Add ellipsis if needed
      if (end < totalPages - 1) {
        pages.push("...")
      }

      // Always show last page
      pages.push(totalPages)
    }

    return pages
  }, [currentPage, totalPages])

  return (
    <div className={`bg-[#001529]/90 border border-[#00e5ff]/20 rounded-xl overflow-hidden ${className}`}>
      {/* Search bar */}
      {searchable && (
        <div className="p-4 border-b border-[#00e5ff]/10">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#00e5ff]/50" />
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setCurrentPage(1) // Reset to first page on search
              }}
              className="pl-9 bg-[#002a4a] border-[#00e5ff]/20 text-white placeholder:text-[#00e5ff]/50 focus:border-[#00e5ff]/50"
            />
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#00e5ff]/10">
              {columns.map((column, index) => (
                <th
                  key={index}
                  className={`px-4 py-3 text-left text-xs font-medium text-[#00e5ff]/70 uppercase tracking-wider ${
                    column.sortable !== false ? "cursor-pointer hover:text-[#00e5ff]" : ""
                  }`}
                  onClick={() => column.sortable !== false && handleSort(column.accessorKey)}
                >
                  <div className="flex items-center gap-1">
                    <span>{column.header}</span>
                    {column.sortable !== false && (
                      <div className="flex flex-col">
                        {sortConfig.key === column.accessorKey ? (
                          sortConfig.direction === "asc" ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : sortConfig.direction === "desc" ? (
                            <ChevronDown className="w-3 h-3" />
                          ) : (
                            <ChevronsUpDown className="w-3 h-3" />
                          )
                        ) : (
                          <ChevronsUpDown className="w-3 h-3 opacity-50" />
                        )}
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#00e5ff]/10">
            {paginatedData.length > 0 ? (
              paginatedData.map((item, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-[#00e5ff]/5 transition-colors">
                  {columns.map((column, colIndex) => (
                    <td key={colIndex} className="px-4 py-3 text-sm text-white">
                      {column.cell ? column.cell(item) : String(item[column.accessorKey] || "")}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-4 py-6 text-sm text-center text-[#00e5ff]/50">
                  No results found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="p-4 border-t border-[#00e5ff]/10 flex items-center justify-between">
          <div className="text-xs text-[#00e5ff]/50">
            Showing {(currentPage - 1) * pageSize + 1} to{" "}
            {Math.min(currentPage * pageSize, filteredAndSortedData.length)} of {filteredAndSortedData.length} results
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="p-1 rounded text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10 disabled:opacity-50 disabled:pointer-events-none"
            >
              <ChevronDown className="w-4 h-4 rotate-90" />
            </button>

            {pageNumbers.map((page, index) => (
              <button
                key={index}
                onClick={() => typeof page === "number" && setCurrentPage(page)}
                disabled={page === "..." || page === currentPage}
                className={`min-w-[32px] h-8 rounded flex items-center justify-center text-xs ${
                  page === currentPage
                    ? "bg-[#00e5ff]/20 text-[#00e5ff]"
                    : "text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10"
                } ${page === "..." ? "pointer-events-none" : ""}`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="p-1 rounded text-[#00e5ff]/70 hover:text-[#00e5ff] hover:bg-[#00e5ff]/10 disabled:opacity-50 disabled:pointer-events-none"
            >
              <ChevronDown className="w-4 h-4 -rotate-90" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
