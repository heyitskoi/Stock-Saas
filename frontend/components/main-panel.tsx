"use client"

import {
  Plus,
  MoreHorizontal,
  AlertTriangle,
  ShoppingCart,
  PackagePlus,
  ArrowRightCircle,
  FolderPlus,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import type { Category, StockItem } from "@/types/stock"

interface MainPanelProps {
  categories: Category[]
  itemsByCategory: Record<string, StockItem[]>
  selectedDepartment: number | null
  onAddItem: (categoryId: string) => void
  onAddCategory: () => void
  onItemAction: (action: string, itemId: string) => void
  onRequestRestock: (item: StockItem) => void
  onAddStock: (item: StockItem) => void
  onTransferStock: (item: StockItem) => void
  onAddDepartment: () => void
  departments: any[]
}

export function MainPanel({
  categories,
  itemsByCategory,
  selectedDepartment,
  onAddItem,
  onAddCategory,
  onItemAction,
  onRequestRestock,
  onAddStock,
  onTransferStock,
  onAddDepartment,
  departments,
}: MainPanelProps) {
  const getCategoryName = (categoryId: string) => {
    const category = categories.find((c) => c.id === parseInt(categoryId))
    return category ? category.name : "Unknown Category"
  }

  // Calculate stock level percentage
  const getStockLevelPercentage = (quantity: number, min_par: number) => {
    // If min_par is 0, avoid division by zero
    if (min_par === 0) return quantity > 0 ? 100 : 0

    // Calculate percentage based on minimum par (2x min_par is considered 100%)
    const percentage = Math.min(Math.round((quantity / (min_par * 2)) * 100), 100)
    return percentage
  }

  // Get color class based on stock level
  const getStockLevelColorClass = (quantity: number, min_par: number) => {
    if (quantity === 0) return "bg-red-500"
    if (quantity < min_par) return "bg-amber-500"
    return "bg-green-500"
  }

  // Get categories for the selected department
  const departmentCategories = categories.filter(
    (cat) => cat.department_id === selectedDepartment
  );

  return (
    <ScrollArea className="flex-1 p-6">
      {selectedDepartment && (
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold">Department Stock</h2>
          {departments.length === 0 ? (
            <div className="flex items-center gap-2">
              <Button disabled className="gap-2">
                <FolderPlus className="h-4 w-4" />
                Add New Stock Category
              </Button>
              <p className="text-sm text-muted-foreground">Please add a department first</p>
            </div>
          ) : (
            <Button onClick={onAddCategory} className="gap-2">
              <FolderPlus className="h-4 w-4" />
              Add New Stock Category
            </Button>
          )}
          <Button onClick={onAddDepartment} className="gap-2 ml-2" variant="outline">
            <Plus className="h-4 w-4" />
            Add Department
          </Button>
        </div>
      )}

      {departmentCategories.length > 0 ? (
        <div className="space-y-6">
          {departmentCategories.map((category) => {
            const items = itemsByCategory[category.id] || [];
            return (
              <Card key={category.id}>
                <CardHeader className="flex flex-row items-center justify-between py-4">
                  <CardTitle>{category.name}</CardTitle>
                  <Button size="sm" variant="outline" className="gap-1" onClick={() => onAddItem(category.id.toString())}>
                    <Plus className="h-4 w-4" />
                    Add Item
                  </Button>
                </CardHeader>
                <CardContent>
                  {items.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Item Name</TableHead>
                          <TableHead className="w-[180px]">Stock Level</TableHead>
                          <TableHead className="w-[100px] text-center">Quantity</TableHead>
                          <TableHead className="w-[100px] text-center">Min Par</TableHead>
                          <TableHead className="w-[100px] text-center">Stock Code</TableHead>
                          <TableHead className="w-[150px]"></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {items.map((item) => {
                          const stockPercentage = getStockLevelPercentage(item.quantity, item.min_par)
                          const isLowStock = item.quantity < item.min_par
                          const isOutOfStock = item.quantity === 0

                          return (
                            <TableRow
                              key={item.id}
                              className={
                                isOutOfStock
                                  ? "bg-red-50 dark:bg-red-950/20"
                                  : isLowStock
                                    ? "bg-amber-50 dark:bg-amber-950/20"
                                    : ""
                              }
                            >
                              <TableCell className="font-medium">
                                <div className="flex items-center gap-2">
                                  {item.name}
                                  {isLowStock && (
                                    <Badge variant="outline" className="text-amber-500 border-amber-500">
                                      <AlertTriangle className="h-3 w-3 mr-1" />
                                      Low Stock
                                    </Badge>
                                  )}
                                  {isOutOfStock && (
                                    <Badge variant="outline" className="text-red-500 border-red-500">
                                      Out of Stock
                                    </Badge>
                                  )}
                                </div>
                              </TableCell>
                              <TableCell>
                                <div className="flex items-center gap-2">
                                  <Progress
                                    value={stockPercentage}
                                    className="h-2"
                                    indicatorClassName={getStockLevelColorClass(item.quantity, item.min_par)}
                                  />
                                  <span className="text-xs text-muted-foreground w-8">{stockPercentage}%</span>
                                </div>
                              </TableCell>
                              <TableCell className="text-center">
                                <span
                                  className={
                                    isOutOfStock
                                      ? "text-red-500 font-medium"
                                      : isLowStock
                                        ? "text-amber-500 font-medium"
                                        : ""
                                  }
                                >
                                  {item.quantity}
                                </span>
                              </TableCell>
                              <TableCell className="text-center">{item.min_par}</TableCell>
                              <TableCell className="text-center text-muted-foreground">{item.stock_code || "-"}</TableCell>
                              <TableCell>
                                <div className="flex justify-end gap-1">
                                  <Button
                                    variant="outline"
                                    size="icon"
                                    className="h-8 w-8 text-green-600"
                                    onClick={() => onAddStock(item)}
                                    title="Add Stock"
                                  >
                                    <PackagePlus className="h-4 w-4" />
                                  </Button>

                                  {item.quantity > 0 && (
                                    <Button
                                      variant="outline"
                                      size="icon"
                                      className="h-8 w-8 text-blue-600"
                                      onClick={() => onTransferStock(item)}
                                      title="Transfer Stock"
                                    >
                                      <ArrowRightCircle className="h-4 w-4" />
                                    </Button>
                                  )}

                                  {(isLowStock || isOutOfStock) && (
                                    <Button
                                      variant="outline"
                                      size="icon"
                                      className="h-8 w-8 text-amber-600"
                                      onClick={() => onRequestRestock(item)}
                                      title="Request Restock"
                                    >
                                      <ShoppingCart className="h-4 w-4" />
                                    </Button>
                                  )}
                                  <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                      <Button variant="ghost" size="icon" className="h-8 w-8">
                                        <MoreHorizontal className="h-4 w-4" />
                                        <span className="sr-only">Open menu</span>
                                      </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                      <DropdownMenuItem onClick={() => onItemAction("edit", item.id.toString())}>
                                        Edit
                                      </DropdownMenuItem>
                                      <DropdownMenuItem onClick={() => onItemAction("move", item.id.toString())}>
                                        Move to another category
                                      </DropdownMenuItem>
                                      <DropdownMenuItem onClick={() => onItemAction("history", item.id.toString())}>
                                        View change history
                                      </DropdownMenuItem>
                                      <DropdownMenuItem
                                        onClick={(e) => {
                                          e.stopPropagation()
                                          onItemAction("delete", item.id.toString())
                                        }}
                                        className="text-red-600"
                                      >
                                        Delete
                                      </DropdownMenuItem>
                                    </DropdownMenuContent>
                                  </DropdownMenu>
                                </div>
                              </TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
                  ) : (
                    <div className="text-center text-muted-foreground py-6">
                      No items in this category yet.
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : selectedDepartment ? (
        <div className="flex flex-col items-center justify-center h-[50vh] text-center">
          <FolderPlus className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-xl font-medium mb-2">No Stock Categories</h3>
          <p className="text-muted-foreground mb-6">This department doesn't have any stock categories yet.</p>
          <Button onClick={onAddCategory} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Stock Category
          </Button>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-[50vh] text-center">
          <h3 className="text-xl font-medium mb-2">Select a Department</h3>
          <p className="text-muted-foreground">Please select a department from the sidebar to view stock items.</p>
        </div>
      )}
    </ScrollArea>
  )
}
