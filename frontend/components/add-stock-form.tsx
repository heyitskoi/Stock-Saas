"use client"

import type React from "react"

import { useState } from "react"
import { PackagePlus } from "lucide-react"
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
import type { StockItem } from "@/types/stock"

interface AddStockFormProps {
  isOpen: boolean
  onClose: () => void
  item: StockItem | null
  onSubmit: (data: AddStockData) => void
}

export interface AddStockData {
  itemId: string
  quantity: number
  source: string
  notes: string
  date: string
}

export function AddStockForm({ isOpen, onClose, item, onSubmit }: AddStockFormProps) {
  const [quantity, setQuantity] = useState(1)
  const [source, setSource] = useState("supplier")
  const [notes, setNotes] = useState("")
  const [date, setDate] = useState(() => {
    const today = new Date()
    return today.toISOString().split("T")[0]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!item) return

    onSubmit({
      // item.id is a number but consumers expect a string
      itemId: item.id.toString(),
      quantity,
      source,
      notes,
      date,
    })

    // Reset form
    setQuantity(1)
    setSource("supplier")
    setNotes("")
    onClose()
  }

  if (!item) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <PackagePlus className="h-5 w-5" />
            Add Stock
          </DialogTitle>
          <DialogDescription>Add new stock for {item.name}</DialogDescription>
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
                Current
              </Label>
              <div className="col-span-3 flex items-center gap-2">
                <Input id="current-quantity" value={item.quantity} readOnly className="w-20 bg-muted text-center" />
                <span className="text-sm text-muted-foreground">Min: {item.min_par}</span>
              </div>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="add-quantity" className="text-right">
                Add
              </Label>
              <Input
                id="add-quantity"
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(Number.parseInt(e.target.value) || 1)}
                className="w-20 text-center"
              />
              <div className="col-span-2 text-sm text-muted-foreground">
                New total: <span className="font-medium">{item.quantity + quantity}</span>
              </div>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="source" className="text-right">
                Source
              </Label>
              <Select value={source} onValueChange={setSource}>
                <SelectTrigger id="source" className="col-span-3">
                  <SelectValue placeholder="Select source" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="supplier">Supplier Order</SelectItem>
                  <SelectItem value="transfer">Department Transfer</SelectItem>
                  <SelectItem value="return">Customer Return</SelectItem>
                  <SelectItem value="adjustment">Inventory Adjustment</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="date" className="text-right">
                Date
              </Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="notes" className="text-right">
                Notes
              </Label>
              <Textarea
                id="notes"
                placeholder="Add any notes about this stock addition"
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
            <Button type="submit">Add Stock</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
