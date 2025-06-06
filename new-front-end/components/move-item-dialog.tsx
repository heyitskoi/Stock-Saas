"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { StockItem, Department, Category } from "@/types/stock"

interface MoveItemDialogProps {
  isOpen: boolean
  onClose: () => void
  item: StockItem | null
  departments: Department[]
  categories: Category[]
  onSubmit: (data: { department_id: number; category_id: number }) => void
}

export function MoveItemDialog({
  isOpen,
  onClose,
  item,
  departments,
  categories,
  onSubmit,
}: MoveItemDialogProps) {
  const [departmentId, setDepartmentId] = useState<number>(departments[0]?.id ?? 0)
  const [categoryId, setCategoryId] = useState<number>(0)

  useEffect(() => {
    if (item) {
      setDepartmentId(item.department_id)
      setCategoryId(item.category_id)
    } else if (departments.length > 0) {
      setDepartmentId(departments[0].id)
      setCategoryId(0)
    }
  }, [item, departments, isOpen])

  // Filter categories by selected department
  const filteredCategories = categories.filter((cat) => cat.department_id === departmentId)

  useEffect(() => {
    // If the current categoryId is not in the filtered list, reset it
    if (!filteredCategories.some((cat) => cat.id === categoryId)) {
      setCategoryId(filteredCategories[0]?.id ?? 0)
    }
  }, [departmentId, categories, isOpen])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (categoryId && departmentId) {
      onSubmit({ department_id: departmentId, category_id: categoryId })
      onClose()
    }
  }

  if (!item) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Move Item</DialogTitle>
          <DialogDescription>
            Move <span className="font-semibold">{item.name}</span> to another department and category.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <label htmlFor="move-department" className="text-right">Department</label>
              <Select value={departmentId.toString()} onValueChange={v => setDepartmentId(Number(v))}>
                <SelectTrigger id="move-department" className="col-span-3">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((dept) => (
                    <SelectItem key={dept.id} value={dept.id.toString()}>{dept.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <label htmlFor="move-category" className="text-right">Category</label>
              <Select value={categoryId.toString()} onValueChange={v => setCategoryId(Number(v))}>
                <SelectTrigger id="move-category" className="col-span-3">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {filteredCategories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id.toString()}>{cat.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit">Move Item</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
} 