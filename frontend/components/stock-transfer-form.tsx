"use client"

import React from "react"

import { useState } from "react"
import { ArrowRightCircle } from "lucide-react"
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
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import type { StockItem, Department } from "@/types/stock"

interface StockTransferFormProps {
  isOpen: boolean
  onClose: () => void
  item: StockItem | null
  departments: Department[]
  currentDepartmentId: string
  onSubmit: (data: StockTransferData) => void
}

export interface StockTransferData {
  itemId: string
  quantity: number
  fromDepartmentId: string
  toDepartmentId: string | "customer"
  transferType: "internal" | "customer"
  notes: string
  date: string
}

export function StockTransferForm({
  isOpen,
  onClose,
  item,
  departments,
  currentDepartmentId,
  onSubmit,
}: StockTransferFormProps) {
  const [quantity, setQuantity] = useState(1)
  const [transferType, setTransferType] = useState<"internal" | "customer">("internal")
  const [toDepartmentId, setToDepartmentId] = useState("")
  const [notes, setNotes] = useState("")
  const [date, setDate] = useState(() => {
    const today = new Date()
    return today.toISOString().split("T")[0]
  })

  // Reset form when item changes
  React.useEffect(() => {
    if (item) {
      setQuantity(1)
      setTransferType("internal")
      setToDepartmentId("")
      setNotes("")
    }
  }, [item])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!item) return

    onSubmit({
      itemId: item.id,
      quantity,
      fromDepartmentId: currentDepartmentId,
      toDepartmentId: transferType === "internal" ? toDepartmentId : "customer",
      transferType,
      notes,
      date,
    })

    onClose()
  }

  if (!item) return null

  const maxQuantity = item.quantity

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ArrowRightCircle className="h-5 w-5" />
            Transfer Stock
          </DialogTitle>
          <DialogDescription>Transfer {item.name} to another department or issue to customer</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item-name" className="text-right">
                Item
              </Label>
              <Input id="item-name" value={item.name} readOnly className="col-span-3 bg-muted" />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="current-quantity" className="text-right">
                Available
              </Label>
              <Input id="current-quantity" value={item.quantity} readOnly className="w-20 bg-muted text-center" />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="transfer-quantity" className="text-right">
                Transfer
              </Label>
              <Input
                id="transfer-quantity"
                type="number"
                min="1"
                max={maxQuantity}
                value={quantity}
                onChange={(e) => setQuantity(Math.min(Number.parseInt(e.target.value) || 1, maxQuantity))}
                className="w-20 text-center"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">From</Label>
              <div className="col-span-3">
                <Input
                  value={departments.find((d) => d.id === currentDepartmentId)?.name || "Current Department"}
                  readOnly
                  className="bg-muted"
                />
              </div>
            </div>

            <div className="grid grid-cols-4 items-start gap-4">
              <Label className="text-right pt-2">Transfer To</Label>
              <RadioGroup
                value={transferType}
                onValueChange={(value) => setTransferType(value as "internal" | "customer")}
                className="col-span-3 space-y-3"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="internal" id="internal" />
                  <Label htmlFor="internal" className="font-normal">
                    Another Department
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="customer" id="customer" />
                  <Label htmlFor="customer" className="font-normal">
                    Issue to Customer/External
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {transferType === "internal" && (
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="to-department" className="text-right">
                  Department
                </Label>
                <Select value={toDepartmentId} onValueChange={setToDepartmentId} required>
                  <SelectTrigger id="to-department" className="col-span-3">
                    <SelectValue placeholder="Select destination department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments
                      .filter((dept) => dept.id !== currentDepartmentId)
                      .map((department) => (
                        <SelectItem key={department.id} value={department.id}>
                          {department.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="transfer-date" className="text-right">
                Date
              </Label>
              <Input
                id="transfer-date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="transfer-notes" className="text-right">
                Notes
              </Label>
              <Textarea
                id="transfer-notes"
                placeholder={
                  transferType === "internal"
                    ? "Add any notes about this transfer"
                    : "Add customer details or reference numbers"
                }
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="col-span-3"
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={transferType === "internal" && !toDepartmentId}>
              {transferType === "internal" ? "Transfer Stock" : "Issue to Customer"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
