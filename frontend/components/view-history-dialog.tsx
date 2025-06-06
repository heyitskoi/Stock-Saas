"use client"

import type React from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import type { StockItem, StockHistoryEntry } from "@/types/stock"

interface ViewHistoryDialogProps {
  isOpen: boolean
  onClose: () => void
  item: StockItem | null
  stockHistory: StockHistoryEntry[]
}

export function ViewHistoryDialog({ isOpen, onClose, item, stockHistory }: ViewHistoryDialogProps) {
  if (!item) return null
  const itemHistory = stockHistory.filter((entry) => entry.item_id === item.id)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Change History</DialogTitle>
          <DialogDescription>
            Showing history for <span className="font-semibold">{item.name}</span>
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-96 overflow-y-auto">
          {itemHistory.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">No history for this item.</div>
          ) : (
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-2">Date</th>
                  <th className="text-left py-2 px-2">Type</th>
                  <th className="text-right py-2 px-2">Qty</th>
                  <th className="text-right py-2 px-2">Prev</th>
                  <th className="text-right py-2 px-2">New</th>
                  <th className="text-left py-2 px-2">Notes</th>
                </tr>
              </thead>
              <tbody>
                {itemHistory.map((entry) => (
                  <tr key={entry.id} className="border-b last:border-0">
                    <td className="py-1 px-2 whitespace-nowrap">{new Date(entry.date).toLocaleString()}</td>
                    <td className="py-1 px-2 whitespace-nowrap capitalize">{entry.type}</td>
                    <td className="py-1 px-2 text-right">{entry.quantity}</td>
                    <td className="py-1 px-2 text-right">{entry.previous_quantity}</td>
                    <td className="py-1 px-2 text-right">{entry.new_quantity}</td>
                    <td className="py-1 px-2">{entry.notes || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 