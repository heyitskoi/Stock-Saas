"use client"

import { Search, Filter, FileText, Download, QrCode } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Department, Category } from "@/types/stock"
import { ThemeToggle } from "@/components/theme-toggle"

interface HeaderProps {
  searchTerm: string
  onSearchChange: (value: string) => void
  filterOptions: {
    category: string
    stockStatus: string
    department: string
    stockCode: string
  }
  onFilterChange: (options: any) => void
  departments: Department[]
  categories: Category[]
  onExportCSV: () => void
  onExportPDF: () => void
  onScanCode: () => void
}

import { DropdownMenuItem } from "@/components/ui/dropdown-menu"

export function Header({
  searchTerm,
  onSearchChange,
  filterOptions,
  onFilterChange,
  departments,
  categories,
  onExportCSV,
  onExportPDF,
  onScanCode,
}: HeaderProps) {
  const handleFilterChange = (key: string, value: string) => {
    onFilterChange({
      ...filterOptions,
      [key]: value,
    })
  }

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-background border-b">
      <div className="flex items-center">
        <h1 className="text-xl font-bold mr-8">Systems Stock</h1>
      </div>

      <div className="flex items-center gap-4 flex-1 max-w-xl">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search for item..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="gap-2">
              <Filter className="h-4 w-4" />
              Filter
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>Filter Options</DropdownMenuLabel>
            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuLabel className="px-2 py-1.5 text-xs font-normal text-muted-foreground">
                Category
              </DropdownMenuLabel>
              <Select value={filterOptions.category} onValueChange={(value) => handleFilterChange("category", value)}>
                <SelectTrigger className="mx-2 w-[calc(100%-16px)]">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuLabel className="px-2 py-1.5 text-xs font-normal text-muted-foreground">
                Stock Status
              </DropdownMenuLabel>
              <Select
                value={filterOptions.stockStatus}
                onValueChange={(value) => handleFilterChange("stockStatus", value)}
              >
                <SelectTrigger className="mx-2 w-[calc(100%-16px)]">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="outOfStock">Out of Stock</SelectItem>
                  <SelectItem value="belowPar">Below Minimum</SelectItem>
                </SelectContent>
              </Select>
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuLabel className="px-2 py-1.5 text-xs font-normal text-muted-foreground">
                Department
              </DropdownMenuLabel>
              <Select
                value={filterOptions.department}
                onValueChange={(value) => handleFilterChange("department", value)}
              >
                <SelectTrigger className="mx-2 w-[calc(100%-16px)]">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map((department) => (
                    <SelectItem key={department.id} value={department.id}>
                      {department.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuLabel className="px-2 py-1.5 text-xs font-normal text-muted-foreground">
                Stock Code
              </DropdownMenuLabel>
              <div className="px-2 py-1.5">
                <Input
                  placeholder="Enter stock code"
                  value={filterOptions.stockCode}
                  onChange={(e) => handleFilterChange("stockCode", e.target.value)}
                  className="h-8"
                />
              </div>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        <Button variant="outline" size="icon" onClick={onScanCode} title="Scan Barcode/QR Code">
          <QrCode className="h-4 w-4" />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="icon">
              <Download className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={onExportCSV}>
              <FileText className="mr-2 h-4 w-4" />
              Export to CSV
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onExportPDF}>
              <FileText className="mr-2 h-4 w-4" />
              Export to PDF
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
