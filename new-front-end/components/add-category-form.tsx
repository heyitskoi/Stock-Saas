"use client"

import type React from "react"

import { useState } from "react"
import { FolderPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { Category } from "@/types/stock"
import { ICON_LIST } from "./iconList"
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip"

interface AddCategoryFormProps {
  isOpen: boolean
  onClose: () => void
  departmentId: string
  onSubmit: (data: Omit<Category, "id">) => void
}

export function AddCategoryForm({ isOpen, onClose, departmentId, onSubmit }: AddCategoryFormProps) {
  const [name, setName] = useState("")
  const [selectedIcon, setSelectedIcon] = useState<string>(ICON_LIST[0].name)
  const [iconSearch, setIconSearch] = useState("")
  const [error, setError] = useState<string>("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      setError("Category name is required.")
      return
    }
    if (!selectedIcon) {
      setError("Please select an icon.")
      return
    }
    setError("")
    onSubmit({
      name,
      department_id: Number(departmentId),
      icon: selectedIcon,
    })
    setName("")
    setSelectedIcon(ICON_LIST[0].name)
    onClose()
  }

  const filteredIcons = ICON_LIST.filter(iconObj =>
    iconObj.name.toLowerCase().includes(iconSearch.toLowerCase())
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FolderPlus className="h-5 w-5" />
            Add Stock Category
          </DialogTitle>
          <DialogDescription>Create a new stock category for this department</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="category-name" className="text-right">
                Name
              </Label>
              <Input
                id="category-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3"
                placeholder="e.g., Workstations, Monitors, Peripherals"
                required
              />
            </div>
            <div>
              <Label className="mb-2 block">Icon</Label>
              <Input
                placeholder="Search icons..."
                value={iconSearch}
                onChange={e => setIconSearch(e.target.value)}
                className="mb-2"
              />
              <TooltipProvider>
                <div className="grid grid-cols-4 gap-4 max-h-40 overflow-y-auto">
                  {filteredIcons.map(iconObj => {
                    const IconComp = iconObj.icon
                    return (
                      <Tooltip key={iconObj.name}>
                        <TooltipTrigger asChild>
                          <Button
                            type="button"
                            variant={selectedIcon === iconObj.name ? "secondary" : "ghost"}
                            size="icon"
                            className={`w-10 h-10 flex items-center justify-center ${selectedIcon === iconObj.name ? "border-2 border-blue-500" : ""}`}
                            onClick={() => setSelectedIcon(iconObj.name)}
                            aria-label={iconObj.name}
                          >
                            <IconComp className="w-6 h-6" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>{iconObj.name}</TooltipContent>
                      </Tooltip>
                    )
                  })}
                </div>
              </TooltipProvider>
            </div>
            {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Create Category</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
