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
import type { Department } from "@/types/stock"

interface EditDepartmentFormProps {
  isOpen: boolean
  onClose: () => void
  department: Department | null
  onSubmit: (data: Department) => void
}

export function EditDepartmentForm({ isOpen, onClose, department, onSubmit }: EditDepartmentFormProps) {
  const [name, setName] = useState(department?.name || "")
  const [icon, setIcon] = useState(department?.icon || "Computer")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!department) return

    onSubmit({
      id: department.id,
      name,
      icon,
    })

    onClose()
  }

  if (!department) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Edit className="h-5 w-5" />
            Edit Department
          </DialogTitle>
          <DialogDescription>Update department details</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="department-name" className="text-right">
                Name
              </Label>
              <Input
                id="department-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3"
                required
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="department-icon" className="text-right">
                Icon
              </Label>
              <Select value={icon} onValueChange={setIcon}>
                <SelectTrigger id="department-icon" className="col-span-3">
                  <SelectValue placeholder="Select icon" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Computer">Computer</SelectItem>
                  <SelectItem value="Briefcase">Briefcase</SelectItem>
                  <SelectItem value="Truck">Truck</SelectItem>
                  <SelectItem value="Package">Package</SelectItem>
                  <SelectItem value="Users">Users</SelectItem>
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
