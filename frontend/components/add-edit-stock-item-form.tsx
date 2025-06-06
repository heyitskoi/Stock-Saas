"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { StockItem, Department } from "@/types/stock"

interface AddEditStockItemFormProps {
  isOpen: boolean
  onClose: () => void
  initialItem: StockItem | null
  categoryId: number
  departments: Department[]
  onSubmit: (item: Omit<StockItem, "id">) => void
}

export function AddEditStockItemForm({
  isOpen,
  onClose,
  initialItem,
  categoryId,
  departments,
  onSubmit,
}: AddEditStockItemFormProps) {
  const [name, setName] = useState("")
  const [quantity, setQuantity] = useState(0)
  const [minPar, setMinPar] = useState(1)
  const [stockCode, setStockCode] = useState("")
  const [status, setStatus] = useState<"available" | "low" | "out">("available")
  const [departmentId, setDepartmentId] = useState<number>(departments[0]?.id ?? 0)

  useEffect(() => {
    if (initialItem) {
      setName(initialItem.name)
      setQuantity(initialItem.quantity)
      setMinPar(initialItem.min_par)
      setStockCode(initialItem.stock_code || "")
      const allowedStatuses = ["available", "low", "out"] as const;
      if (initialItem.status && allowedStatuses.includes(initialItem.status as typeof allowedStatuses[number])) {
        setStatus(initialItem.status as typeof allowedStatuses[number]);
      } else {
        setStatus("available");
      }
      setDepartmentId(initialItem.department_id)
    } else {
      setName("")
      setQuantity(0)
      setMinPar(1)
      setStockCode("")
      setStatus("available")
      setDepartmentId(departments[0]?.id ?? 0)
    }
  }, [initialItem, isOpen, departments])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      name,
      quantity,
      min_par: minPar,
      stock_code: stockCode,
      category_id: categoryId,
      department_id: departmentId,
      status,
    })
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{initialItem ? "Edit Item" : "Add Item"}</DialogTitle>
          <DialogDescription>
            {initialItem ? "Edit the details of this stock item." : "Add a new stock item to this category."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-name" className="text-right">Name</Label>
              <Input id="item-name" value={name} onChange={e => setName(e.target.value)} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-quantity" className="text-right">Quantity</Label>
              <Input id="item-quantity" type="number" min="0" value={quantity} onChange={e => setQuantity(Number(e.target.value))} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-min-par" className="text-right">Min Par</Label>
              <Input id="item-min-par" type="number" min="1" value={minPar} onChange={e => setMinPar(Number(e.target.value))} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-stock-code" className="text-right">Stock Code</Label>
              <Input id="item-stock-code" value={stockCode} onChange={e => setStockCode(e.target.value)} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-status" className="text-right">Status</Label>
              <Select value={status} onValueChange={v => setStatus(v as "available" | "low" | "out") }>
                <SelectTrigger id="item-status" className="col-span-3">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="out">Out</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-department" className="text-right">Department</Label>
              <Select value={departmentId.toString()} onValueChange={v => setDepartmentId(Number(v))}>
                <SelectTrigger id="item-department" className="col-span-3">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((dept) => (
                    <SelectItem key={dept.id} value={dept.id.toString()}>{dept.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit">{initialItem ? "Save Changes" : "Add Item"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
} 