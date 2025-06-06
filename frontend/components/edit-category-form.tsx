"use client"

import type React from "react"

import { useState } from "react"
import { Edit } from "lucide-react"
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Category, Department } from "@/types/stock"

interface EditCategoryFormProps {
  isOpen: boolean
  onClose: () => void
  category: Category | null
  departments: Department[]
  onSubmit: (data: Category) => void
}

export function EditCategoryForm({ isOpen, onClose, category, departments, onSubmit }: EditCategoryFormProps) {
  const [name, setName] = useState(category?.name || "")
  const [departmentId, setDepartmentId] = useState(category?.departmentId || "")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!category) return

    onSubmit({
      id: category.id,
      name,
      departmentId,
    })

    onClose()
  }

  if (!category) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Edit className="h-5 w-5" />
            Edit Category
          </DialogTitle>
          <DialogDescription>Update category details</DialogDescription>
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
                required
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="category-department" className="text-right">
                Department
              </Label>
              <Select value={departmentId} onValueChange={setDepartmentId}>
                <SelectTrigger id="category-department" className="col-span-3">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((department) => (
                    <SelectItem key={department.id} value={department.id}>
                      {department.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Save Changes</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
