"use client"

import { useState, useEffect, useCallback } from "react"
import { Header } from "./header"
import { Sidebar } from "./sidebar"
import { MainPanel } from "./main-panel"
import { BarcodeScanner } from "./barcode-scanner"
import { RestockForm, type RestockFormData } from "./restock-form"
import { AddStockForm, type AddStockData } from "./add-stock-form"
import { EditDepartmentForm } from "./edit-department-form"
import { EditCategoryForm } from "./edit-category-form"
import { DeleteConfirmation } from "./delete-confirmation"
import { StockTransferForm, type StockTransferData } from "./stock-transfer-form"
import { useToast } from "@/components/ui/use-toast"
import type { Department, Category, StockItem, StockHistoryEntry, DepartmentStock } from "@/types/stock"
import { AddCategoryForm } from "./add-category-form"
import { AddEditStockItemForm } from "./add-edit-stock-item-form"
import { MoveItemDialog } from "./move-item-dialog"
import { ViewHistoryDialog } from "./view-history-dialog"
import { ICON_LIST } from "./iconList"
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip"
import { Button } from "@/components/ui/button"
import { apiFetch, apiPost, apiGet } from "@/lib/api"

const isDev = process.env.NODE_ENV === "development"

// Sample data
const sampleDepartments: Department[] = [
  { id: 1, name: "Systems", icon: "Computer" },
  { id: 2, name: "Accounts/Warehouse", icon: "Briefcase" },
  { id: 3, name: "Field Services", icon: "Truck" },
]

const sampleCategories: Category[] = [
  { id: 1, name: "Desktop Parts", department_id: 1 },
  { id: 2, name: "Switches/Routers", department_id: 1 },
  { id: 3, name: "Cables", department_id: 1 },
  { id: 4, name: "Office Supplies", department_id: 2 },
  { id: 5, name: "Tools", department_id: 3 },
]

const sampleItems: StockItem[] = [
  {
    id: 1,
    name: "Power Supply",
    quantity: 5,
    min_par: 2,
    category_id: 1,
    department_id: 1,
    stock_code: "PS-001",
    status: "available",
  },
  {
    id: 2,
    name: "RAM 8GB",
    quantity: 7,
    min_par: 3,
    category_id: 1,
    department_id: 1,
    stock_code: "RAM-8G",
    status: "available",
  },
  {
    id: 3,
    name: "SSD 500GB",
    quantity: 0,
    min_par: 5,
    category_id: 1,
    department_id: 1,
    stock_code: "SSD-500",
    status: "out",
  },
  {
    id: 4,
    name: "Network Switch 24-Port",
    quantity: 2,
    min_par: 1,
    category_id: 2,
    department_id: 1,
    stock_code: "NSW-24",
    status: "available",
  },
  {
    id: 5,
    name: "Router Wireless",
    quantity: 3,
    min_par: 2,
    category_id: 2,
    department_id: 1,
    stock_code: "RW-001",
    status: "available",
  },
  {
    id: 6,
    name: "Ethernet Cable 5m",
    quantity: 12,
    min_par: 10,
    category_id: 3,
    department_id: 1,
    stock_code: "EC-5M",
    status: "available",
  },
  {
    id: 7,
    name: "Stapler",
    quantity: 4,
    min_par: 5,
    category_id: 4,
    department_id: 2,
    stock_code: "ST-001",
    status: "low",
  },
  {
    id: 8,
    name: "Screwdriver Set",
    quantity: 2,
    min_par: 2,
    category_id: 5,
    department_id: 3,
    stock_code: "SD-SET",
    status: "available",
  },
]

// Initialize department stock tracking
const sampleDepartmentStock: DepartmentStock[] = sampleItems.map((item) => ({
  departmentId: item.department_id.toString(),
  itemId: item.id.toString(),
  quantity: item.quantity,
}))

export function StockDashboard() {
  const { toast } = useToast()
  const [departments, setDepartments] = useState<Department[]>(isDev ? sampleDepartments : [])
  const [categories, setCategories] = useState<Category[]>(isDev ? sampleCategories : [])
  const [items, setItems] = useState<StockItem[]>(isDev ? sampleItems : [])
  const [departmentStock, setDepartmentStock] = useState<DepartmentStock[]>(isDev ? sampleDepartmentStock : [])
  const [stockHistory, setStockHistory] = useState<StockHistoryEntry[]>([])
  const [selectedDepartment, setSelectedDepartment] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterOptions, setFilterOptions] = useState({
    category: "",
    stockStatus: "",
    department: "",
    stockCode: "",
  })
  
  // Loading states
  const [isLoading, setIsLoading] = useState({
    departments: false,
    categories: false,
    items: false
  })

  // State for modals
  const [isScannerOpen, setScannerOpen] = useState(false)
  const [isRestockFormOpen, setRestockFormOpen] = useState(false)
  const [isAddStockFormOpen, setAddStockFormOpen] = useState(false)
  const [isTransferStockOpen, setTransferStockOpen] = useState(false)
  const [isEditDepartmentOpen, setEditDepartmentOpen] = useState(false)
  const [isEditCategoryOpen, setEditCategoryOpen] = useState(false)
  const [isDeleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [isAddCategoryOpen, setAddCategoryOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<StockItem | null>(null)
  const [selectedDepartmentForEdit, setSelectedDepartmentForEdit] = useState<Department | null>(null)
  const [selectedCategoryForEdit, setSelectedCategoryForEdit] = useState<Category | null>(null)
  const [deleteType, setDeleteType] = useState<"department" | "category">("department")
  const [deleteId, setDeleteId] = useState<number>(0)
  const [isAddEditItemOpen, setAddEditItemOpen] = useState(false)
  const [addEditInitialItem, setAddEditInitialItem] = useState<StockItem | null>(null)
  const [addEditCategoryId, setAddEditCategoryId] = useState<number | null>(null)
  const [isMoveItemOpen, setIsMoveItemOpen] = useState(false)
  const [moveItem, setMoveItem] = useState<StockItem | null>(null)
  const [isDeleteItemOpen, setIsDeleteItemOpen] = useState(false)
  const [deleteItem, setDeleteItem] = useState<StockItem | null>(null)
  const [isViewHistoryOpen, setIsViewHistoryOpen] = useState(false)
  const [historyItem, setHistoryItem] = useState<StockItem | null>(null)

  // Add state for Add Department modal
  const [isAddDepartmentOpen, setIsAddDepartmentOpen] = useState(false)
  const [newDepartmentName, setNewDepartmentName] = useState("")
  const [newDepartmentIcon, setNewDepartmentIcon] = useState(ICON_LIST[0].name) // Default to first icon
  const [iconSearch, setIconSearch] = useState("")

  const loadItems = useCallback(async () => {
    try {
      setIsLoading(prev => ({ ...prev, items: true }))
      const data = await apiGet<StockItem[]>("/items/status?tenant_id=1")
      if (Array.isArray(data)) {
        setItems(data)
      }
    } catch (err) {
      console.error("Failed to fetch items", err)
      if (isDev) setItems(sampleItems)
    } finally {
      setIsLoading(prev => ({ ...prev, items: false }))
    }
  }, [])

  // Fetch departments and categories from API on mount - only once
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch departments with loading state
        setIsLoading(prev => ({ ...prev, departments: true }));
        const fetchedDepartments = await apiGet<Department[]>('/api/departments/');
        if (Array.isArray(fetchedDepartments) && fetchedDepartments.length > 0) {
          setDepartments(fetchedDepartments);
          console.log("Fetched departments:", fetchedDepartments);
        } else {
          console.warn("Empty or invalid departments response:", fetchedDepartments);
        }
        setIsLoading(prev => ({ ...prev, departments: false }));
        
        // Fetch categories with loading state
        setIsLoading(prev => ({ ...prev, categories: true }));
        const fetchedCategories = await apiGet<Category[]>('/api/categories/');
        if (Array.isArray(fetchedCategories)) {
          setCategories(fetchedCategories);
          console.log("Fetched categories:", fetchedCategories);
        } else {
          console.warn("Empty or invalid categories response:", fetchedCategories);
        }
        setIsLoading(prev => ({ ...prev, categories: false }));
      } catch (error) {
        console.error("Error fetching initial data:", error);
        setIsLoading({ departments: false, categories: false, items: false });
        
        // Show a more detailed error message
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        toast({
          title: "Connection Error",
          description: `Failed to load data: ${errorMessage}. Using sample data instead.`,
          variant: "destructive",
        });
      }
    };
    
    fetchData();
    // Empty dependency array ensures this only runs once on component mount
  }, []);

  // Fetch items on mount
  useEffect(() => {
    loadItems()
  }, [loadItems])

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const protocol = apiUrl.startsWith('https') ? 'wss' : 'ws'
    const host = apiUrl.replace(/^https?:\/\//, '')
    const ws = new WebSocket(`${protocol}://${host}/ws/inventory/1`)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (['update', 'transfer', 'delete'].includes(data.event)) {
          loadItems()
        }
        if (data.event === 'low_stock') {
          toast({
            title: 'Low Stock',
            description: `${data.item} has ${data.available} remaining (threshold ${data.threshold})`,
            variant: 'destructive',
          })
        }
      } catch (err) {
        console.error('WebSocket message error', err)
      }
    }

    return () => {
      ws.close()
    }
  }, [loadItems, toast])

  // Filter items based on search term and filter options
  const filteredItems = items.filter((item) => {
    // Search term filter
    if (
      searchTerm &&
      !item.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !item.stock_code?.toLowerCase().includes(searchTerm.toLowerCase())
    ) {
      return false
    }

    // Department filter
    if (selectedDepartment && item.department_id !== selectedDepartment) {
      return false
    }

    // Category filter
    if (filterOptions.category && item.category_id !== parseInt(filterOptions.category)) {
      return false
    }

    // Stock status filter
    if (filterOptions.stockStatus) {
      if (
        (filterOptions.stockStatus === "outOfStock" && item.quantity > 0) ||
        (filterOptions.stockStatus === "available" && item.quantity === 0) ||
        (filterOptions.stockStatus === "belowPar" && item.quantity >= item.min_par)
      ) {
        return false
      }
    }

    return true
  })

  // Group items by category
  const itemsByCategory = filteredItems.reduce(
    (acc, item) => {
      const categoryId = item.category_id.toString()
      if (!acc[categoryId]) {
        acc[categoryId] = []
      }
      acc[categoryId].push(item)
      return acc
    },
    {} as Record<string, StockItem[]>,
  )

  const handleAddItem = (categoryId: string) => {
    const category = categories.find((c: Category) => c.id === parseInt(categoryId));
    if (!category) return;
    setAddEditInitialItem(null);
    setAddEditCategoryId(category.id);
    setAddEditItemOpen(true);
  }

  const handleEditItem = (itemId: string) => {
    const item = items.find((i) => i.id === parseInt(itemId));
    if (!item) return;
    setAddEditInitialItem(item);
    setAddEditCategoryId(item.category_id);
    setAddEditItemOpen(true);
  }

  const handleAddEditItemSubmit = async (itemData: Omit<StockItem, "id">) => {
    if (addEditInitialItem) {
      try {
        const updated = await apiFetch<StockItem>("/api/items/update", {
          method: "PUT",
          body: { id: addEditInitialItem.id, ...itemData },
        })
        setItems(items.map((item) => item.id === updated.id ? updated : item))
        toast({
          title: "Item Updated",
          description: `Item '${itemData.name}' has been updated.`,
        })
      } catch (err) {
        console.error("update item failed", err)
      }
    } else {
      try {
        const created = await apiFetch<StockItem>("/api/items/add", {
          method: "POST",
          body: itemData,
        })
        setItems([...items, created])
        toast({
          title: "Item Added",
          description: `New item '${created.name}' added to ${getCategoryName(created.category_id)}.`,
        })
      } catch (err) {
        console.error("add item failed", err)
      }
    }
    setAddEditItemOpen(false)
  }

  const handleAddDepartment = () => {
    setIsAddDepartmentOpen(true);
  };

  const handleAddDepartmentSubmit = async () => {
    if (!newDepartmentName.trim()) {
      toast({ title: "Error", description: "Department name is required", variant: "destructive" });
      return;
    }

    try {
      const response = await apiPost<Department>('/api/departments/', {
        name: newDepartmentName,
        icon: newDepartmentIcon || "Computer"
      });

      setDepartments(prev => [...prev, response]);
      setIsAddDepartmentOpen(false);
      setNewDepartmentName("");
      setNewDepartmentIcon(ICON_LIST[0].name);
      toast({ 
        title: "Department Added", 
        description: `Department '${newDepartmentName}' has been added.` 
      });
    } catch (error) {
      console.error('Failed to create department:', error);
      toast({ 
        title: "Error", 
        description: error instanceof Error ? error.message : "Failed to create department", 
        variant: "destructive" 
      });
    }
  };

  const handleAddCategory = () => {
    // Implementation for adding a new category
    if (!selectedDepartment) {
      toast({
        title: "Select Department",
        description: "Please select a department first",
        variant: "destructive",
      })
      return
    }

    setAddCategoryOpen(true)
  }

  const handleCreateCategory = async (categoryData: Omit<Category, "id">) => {
    try {
      // Set loading state for categories
      setIsLoading(prev => ({ ...prev, categories: true }));
      
      console.log("Creating category with data:", categoryData);
      const newCategory = await apiFetch<Category>("/api/categories/", {
        method: "POST",
        body: {
          name: categoryData.name,
          icon: categoryData.icon || "Package",
          department_id: categoryData.department_id,
        },
      });
      console.log("API response:", newCategory);
      
      // Only update UI after successful API call
      if (newCategory && typeof newCategory.id === 'number') {
        // Refresh the entire categories list to ensure consistency
        const refreshedCategories = await apiGet<Category[]>('/api/categories/');
        if (Array.isArray(refreshedCategories)) {
          setCategories(refreshedCategories);
        } else {
          // Fallback to just adding the new category if refresh fails
          setCategories((prev) => [...prev, newCategory]);
        }
        
        setAddCategoryOpen(false);
        toast({
          title: "Category Created",
          description: `${newCategory.name} has been added to the department`,
        });
      } else {
        throw new Error("Invalid response from server - missing or invalid category ID");
      }
    } catch (err: any) {
      console.error("Error creating category:", err);
      toast({
        title: "Error",
        description: err.message || "Failed to create category",
        variant: "destructive",
      });
    } finally {
      // Always reset loading state
      setIsLoading(prev => ({ ...prev, categories: false }));
    }
  }

  const handleItemAction = (action: string, itemId: string) => {
    // Implementation for item actions (edit, delete, move)
    console.log(`${action} item:`, itemId)

    const item = items.find((item) => item.id === parseInt(itemId))
    if (!item) {
      console.error(`Item with ID ${itemId} not found`);
      return;
    }

    try {
      switch (action) {
        case "edit":
          setAddEditInitialItem(item);
          setAddEditCategoryId(item.category_id);
          setAddEditItemOpen(true);
          break;
        case "move":
          setMoveItem(item);
          setIsMoveItemOpen(true);
          break;
        case "history":
          setHistoryItem(item);
          setIsViewHistoryOpen(true);
          break;
        case "delete":
          // When deleting, set the item and show the confirmation dialog
          setDeleteItem(item);
          setIsDeleteItemOpen(true);
          break;
        default:
          console.warn(`Unknown action: ${action}`);
      }
    } catch (error) {
      console.error(`Error handling ${action} action:`, error);
      toast({
        title: "Error",
        description: `Failed to perform ${action} action. Please try again.`,
        variant: "destructive",
      });
    }
  }

  const handleExportCSV = () => {
    // Implementation for exporting to CSV
    console.log("Exporting to CSV")
    toast({
      title: "Export to CSV",
      description: "Your data is being exported to CSV format",
    })

    // In a real implementation, we would generate and download a CSV file
    setTimeout(() => {
      toast({
        title: "Export Complete",
        description: "Your CSV file has been downloaded",
      })
    }, 1500)
  }

  const handleExportPDF = () => {
    // Implementation for exporting to PDF
    console.log("Exporting to PDF")
    toast({
      title: "Export to PDF",
      description: "Your data is being exported to PDF format",
    })

    // In a real implementation, we would generate and download a PDF file
    setTimeout(() => {
      toast({
        title: "Export Complete",
        description: "Your PDF file has been downloaded",
      })
    }, 1500)
  }

  const handleScanCode = () => {
    // Open the barcode scanner
    setScannerOpen(true)
  }

  const handleCodeScanned = (code: string) => {
    // Find the item with the scanned code
    const item = items.find((item) => item.stock_code === code)

    if (item) {
      toast({
        title: "Code Scanned",
        description: `Found item: ${item.name}`,
      })

      // In a real app, we might open an edit form or update the quantity
      setSearchTerm(code)
    } else {
      toast({
        title: "Code Not Found",
        description: `No item found with code: ${code}`,
        variant: "destructive",
      })
    }
  }

  const handleRequestRestock = (item: StockItem) => {
    setSelectedItem(item)
    setRestockFormOpen(true)
  }

  const handleRestockSubmit = (data: RestockFormData) => {
    console.log("Restock request submitted:", data)

    // Add to stock history
    const historyEntry: StockHistoryEntry = {
      id: Date.now(),
      item_id: parseInt(data.itemId),
      date: new Date().toISOString(),
      type: "request",
      quantity: data.quantity,
      previous_quantity: selectedItem?.quantity || 0,
      new_quantity: selectedItem?.quantity || 0, // Request doesn't change quantity yet
      notes: `Priority: ${data.priority}. ${data.notes}`,
    }

    setStockHistory((prev) => [...prev, historyEntry])

    toast({
      title: "Restock Requested",
      description: `Requested ${data.quantity} units of ${selectedItem?.name} with ${data.priority} priority`,
    })
  }

  const handleAddStock = (item: StockItem) => {
    setSelectedItem(item)
    setAddStockFormOpen(true)
  }

  const handleAddStockSubmit = async (data: AddStockData) => {
    console.log("Add stock submitted:", data)

    if (!selectedItem) return

    // Update the item quantity
    const updatedItems = items.map((item) =>
      item.id === parseInt(data.itemId) ? { ...item, quantity: item.quantity + data.quantity } : item,
    )
    setItems(updatedItems)

    // Update department stock
    setDepartmentStock((prev) => {
      const existingRecord = prev.find(
        (ds) => ds.itemId === data.itemId && ds.departmentId === selectedItem.department_id.toString(),
      )
      if (existingRecord) {
        return prev.map((ds) =>
          ds.itemId === data.itemId && ds.departmentId === selectedItem.department_id.toString()
            ? { ...ds, quantity: ds.quantity + data.quantity }
            : ds,
        )
      } else {
        return [
          ...prev,
          {
            departmentId: selectedItem.department_id.toString(),
            itemId: data.itemId,
            quantity: data.quantity,
          },
        ]
      }
    })

    // Add to stock history
    const historyEntry: StockHistoryEntry = {
      id: Date.now(),
      item_id: parseInt(data.itemId),
      date: data.date,
      type: "add",
      quantity: data.quantity,
      previous_quantity: selectedItem.quantity || 0,
      new_quantity: (selectedItem.quantity || 0) + data.quantity,
      source: data.source,
      notes: data.notes,
    }

    setStockHistory((prev) => [...prev, historyEntry])

    toast({
      title: "Stock Added",
      description: `Added ${data.quantity} units to ${selectedItem.name}`,
    })
  }

  const handleTransferStock = (item: StockItem) => {
    setSelectedItem(item)
    setTransferStockOpen(true)
  }

  const handleTransferStockSubmit = (data: StockTransferData) => {
    console.log("Transfer stock submitted:", data)

    if (!selectedItem) return

    // Update the source department's stock
    const updatedItems = items.map((item) =>
      item.id === parseInt(data.itemId) ? { ...item, quantity: item.quantity - data.quantity } : item,
    )
    setItems(updatedItems)

    // Update department stock records
    setDepartmentStock((prev) => {
      // Reduce quantity in source department
      const updatedStock = prev.map((ds) =>
        ds.itemId === data.itemId && ds.departmentId === data.fromDepartmentId
          ? { ...ds, quantity: ds.quantity - data.quantity }
          : ds,
      )

      // If transferring to another department (not customer), add to destination department
      if (data.transferType === "internal") {
        const existingDestRecord = updatedStock.find(
          (ds) => ds.itemId === data.itemId && ds.departmentId === data.toDepartmentId,
        )

        if (existingDestRecord) {
          return updatedStock.map((ds) =>
            ds.itemId === data.itemId && ds.departmentId === data.toDepartmentId
              ? { ...ds, quantity: ds.quantity + data.quantity }
              : ds,
          )
        } else {
          return [
            ...updatedStock,
            {
              departmentId: data.toDepartmentId as string,
              itemId: data.itemId,
              quantity: data.quantity,
            },
          ]
        }
      }

      return updatedStock
    })

    // Add to stock history
    const historyEntry: StockHistoryEntry = {
      id: Date.now(),
      item_id: parseInt(data.itemId),
      date: data.date,
      type: data.transferType === "internal" ? "transfer" : "issue",
      quantity: data.quantity,
      previous_quantity: selectedItem.quantity,
      new_quantity: selectedItem.quantity - data.quantity,
      notes: data.notes,
      from_department_id: parseInt(data.fromDepartmentId),
      to_department_id: data.toDepartmentId ? parseInt(data.toDepartmentId) : undefined,
    }

    setStockHistory((prev) => [...prev, historyEntry])

    toast({
      title: data.transferType === "internal" ? "Stock Transferred" : "Stock Issued",
      description:
        data.transferType === "internal"
          ? `Transferred ${data.quantity} units of ${selectedItem.name} to ${getDepartmentName(parseInt(data.toDepartmentId as string))}`
          : `Issued ${data.quantity} units of ${selectedItem.name} to customer`,
    })
  }

  // Department and Category Management
  const handleEditDepartment = (department: Department) => {
    setSelectedDepartmentForEdit(department)
    setEditDepartmentOpen(true)
  }

  const handleEditCategory = (category: Category) => {
    setSelectedCategoryForEdit(category)
    setEditCategoryOpen(true)
  }

  const handleDeleteDepartment = (departmentId: number) => {
    setDeleteType("department")
    setDeleteId(departmentId)
    setDeleteConfirmOpen(true)
  }

  const handleDeleteCategory = (categoryId: number) => {
    setDeleteType("category")
    setDeleteId(categoryId)
    setDeleteConfirmOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (deleteType === "department") {
      await apiFetch(`/api/departments/${deleteId}`, { method: "DELETE" })
      setDepartments(departments.filter((dept) => dept.id !== deleteId))
      setCategories(categories.filter((cat) => cat.department_id !== deleteId))
      if (selectedDepartment === deleteId) {
        setSelectedDepartment(null)
      }
      toast({
        title: "Department Deleted",
        description: "Department and its categories have been removed",
      })
    } else {
      await apiFetch(`/api/categories/${deleteId}`, { method: "DELETE" })
      setCategories(categories.filter((cat) => cat.id !== deleteId))
      toast({
        title: "Category Deleted",
        description: "Category has been removed",
      })
    }
  }

  const handleSaveDepartment = async (updatedDepartment: Department) => {
    const res = await apiFetch<Department>(`/api/departments/${updatedDepartment.id}`, {
      method: "PUT",
      body: updatedDepartment,
    })
    setDepartments(departments.map((dept) => (dept.id === res.id ? res : dept)))
    toast({
      title: "Department Updated",
      description: `${res.name} has been updated`,
    })
  }

  const handleSaveCategory = async (updatedCategory: Category) => {
    const res = await apiFetch<Category>(`/api/categories/${updatedCategory.id}`, {
      method: "PUT",
      body: updatedCategory,
    })
    setCategories(categories.map((cat) => (cat.id === res.id ? res : cat)))
    toast({
      title: "Category Updated",
      description: `${res.name} has been updated`,
    })
  }

  const getCategoryName = (categoryId: number) => {
    const category = categories.find((c: Category) => c.id === categoryId)
    return category ? category.name : "Unknown Category"
  }

  const getDepartmentName = (departmentId: number) => {
    const department = departments.find((d) => d.id === departmentId)
    return department ? department.name : "Unknown Department"
  }

  // Get the current department ID (for transfers)
  const currentDepartmentId = selectedDepartment?.toString() || departments[0]?.id.toString() || ""

  // Get categories for the selected department
  const departmentCategories = selectedDepartment
    ? categories.filter((category) => category.department_id === selectedDepartment)
    : []

  const handleMoveItemSubmit = ({ department_id, category_id }: { department_id: number; category_id: number }) => {
    if (!moveItem) return;
    setItems(items.map((item) =>
      item.id === moveItem.id ? { ...item, department_id, category_id } : item
    ));
    setIsMoveItemOpen(false);
    setMoveItem(null);
    toast({
      title: "Item Moved",
      description: `Item has been moved to the new department and category.`,
    });
  }

  const handleConfirmDeleteItem = async () => {
    if (!deleteItem) return;

    try {
      await apiFetch("/api/items/delete", {
        method: "DELETE",
        body: { id: deleteItem.id },
      })
      setItems(items.filter((item) => item.id !== deleteItem.id));
      
      // Add to stock history
      const historyEntry: StockHistoryEntry = {
        id: Date.now(),
        item_id: deleteItem.id,
        date: new Date().toISOString(),
        type: "delete",
        quantity: deleteItem.quantity,
        previous_quantity: deleteItem.quantity,
        new_quantity: 0,
        notes: "Item deleted from inventory",
      };
      
      setStockHistory((prev) => [...prev, historyEntry]);
      
      // Close the dialog and clear the selected item
      setIsDeleteItemOpen(false);
      setDeleteItem(null);
      
      toast({
        title: "Item Deleted",
        description: `${deleteItem.name} has been removed from inventory.`,
        variant: "destructive",
      });
    } catch (error) {
      console.error("Error deleting item:", error);
      toast({
        title: "Error",
        description: "Failed to delete item. Please try again.",
        variant: "destructive",
      });
    }
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        departments={departments}
        categories={categories}
        selectedDepartment={selectedDepartment}
        onSelectDepartment={setSelectedDepartment}
        onAddDepartment={handleAddDepartment}
        onAddCategory={handleAddCategory}
        onEditDepartment={handleEditDepartment}
        onDeleteDepartment={handleDeleteDepartment}
        onEditCategory={handleEditCategory}
        onDeleteCategory={handleDeleteCategory}
      />

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          filterOptions={filterOptions}
          onFilterChange={setFilterOptions}
          departments={departments}
          categories={categories}
          onExportCSV={handleExportCSV}
          onExportPDF={handleExportPDF}
          onScanCode={handleScanCode}
        />

              {/* Loading indicators */}
      {(isLoading.departments || isLoading.categories) && (
        <div className="fixed top-0 left-0 w-full bg-blue-500 text-white text-center p-1 z-50">
          {isLoading.departments && "Loading departments..."}
          {isLoading.categories && !isLoading.departments && "Loading categories..."}
        </div>
      )}
      
      {/* Main Panel */}
      <MainPanel
        categories={categories}
        itemsByCategory={itemsByCategory}
        selectedDepartment={selectedDepartment}
        onAddItem={handleAddItem}
        onAddCategory={handleAddCategory}
        onItemAction={handleItemAction}
        onRequestRestock={handleRequestRestock}
        onAddStock={handleAddStock}
        onTransferStock={handleTransferStock}
        onAddDepartment={handleAddDepartment}
        departments={departments}
      />
      </div>

      {/* Modals */}
      <BarcodeScanner isOpen={isScannerOpen} onClose={() => setScannerOpen(false)} onCodeScanned={handleCodeScanned} />

      <RestockForm
        isOpen={isRestockFormOpen}
        onClose={() => setRestockFormOpen(false)}
        item={selectedItem}
        onSubmit={handleRestockSubmit}
      />

      <AddStockForm
        isOpen={isAddStockFormOpen}
        onClose={() => setAddStockFormOpen(false)}
        item={selectedItem}
        onSubmit={handleAddStockSubmit}
      />

      <StockTransferForm
        isOpen={isTransferStockOpen}
        onClose={() => setTransferStockOpen(false)}
        item={selectedItem}
        departments={departments}
        currentDepartmentId={currentDepartmentId}
        onSubmit={handleTransferStockSubmit}
      />

      <EditDepartmentForm
        isOpen={isEditDepartmentOpen}
        onClose={() => setEditDepartmentOpen(false)}
        department={selectedDepartmentForEdit}
        onSubmit={handleSaveDepartment}
      />

      <EditCategoryForm
        isOpen={isEditCategoryOpen}
        onClose={() => setEditCategoryOpen(false)}
        category={selectedCategoryForEdit}
        departments={departments}
        onSubmit={handleSaveCategory}
      />

      <DeleteConfirmation
        isOpen={isDeleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        title={`Delete ${deleteType === "department" ? "Department" : "Category"}`}
        description={`Are you sure you want to delete this ${deleteType}? This action cannot be undone.${
          deleteType === "department" ? " All categories in this department will also be deleted." : ""
        }`}
        onConfirm={handleConfirmDelete}
      />

      <AddCategoryForm
        isOpen={isAddCategoryOpen}
        onClose={() => setAddCategoryOpen(false)}
        departmentId={selectedDepartment !== null ? selectedDepartment.toString() : ""}
        onSubmit={handleCreateCategory}
      />

      <AddEditStockItemForm
        isOpen={isAddEditItemOpen}
        onClose={() => setAddEditItemOpen(false)}
        initialItem={addEditInitialItem}
        categoryId={addEditCategoryId ?? 0}
        departments={departments}
        onSubmit={handleAddEditItemSubmit}
      />

      <MoveItemDialog
        isOpen={isMoveItemOpen}
        onClose={() => setIsMoveItemOpen(false)}
        item={moveItem}
        departments={departments}
        categories={categories}
        onSubmit={handleMoveItemSubmit}
      />

      <ViewHistoryDialog
        isOpen={isViewHistoryOpen}
        onClose={() => setIsViewHistoryOpen(false)}
        item={historyItem}
        stockHistory={stockHistory}
      />

      {/* Stock Item Delete Confirmation */}
      <DeleteConfirmation
        isOpen={isDeleteItemOpen}
        onClose={() => setIsDeleteItemOpen(false)}
        title="Delete Stock Item"
        description={`Are you sure you want to delete ${deleteItem?.name || 'this item'}? This action cannot be undone.`}
        onConfirm={handleConfirmDeleteItem}
      />

      {/* Add Department Modal */}
      {isAddDepartmentOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded shadow-md w-96">
            <h2 className="text-lg font-bold mb-4">Add Department</h2>
            <input
              className="w-full border p-2 mb-2"
              placeholder="Department Name"
              value={newDepartmentName}
              onChange={e => setNewDepartmentName(e.target.value)}
            />
            {/* Icon Picker */}
            <div className="mb-2">
              <input
                className="w-full border p-2 mb-2"
                placeholder="Search icons..."
                value={iconSearch}
                onChange={e => setIconSearch(e.target.value)}
              />
              <TooltipProvider>
                <div className="grid grid-cols-5 gap-2 max-h-32 overflow-y-auto">
                  {ICON_LIST.filter(iconObj =>
                    iconObj.name.toLowerCase().includes(iconSearch.toLowerCase())
                  ).map(iconObj => {
                    const IconComp = iconObj.icon;
                    return (
                      <Tooltip key={iconObj.name}>
                        <TooltipTrigger asChild>
                          <Button
                            type="button"
                            variant={newDepartmentIcon === iconObj.name ? "secondary" : "ghost"}
                            size="icon"
                            className={
                              newDepartmentIcon === iconObj.name
                                ? "border-2 border-blue-500"
                                : ""
                            }
                            onClick={() => setNewDepartmentIcon(iconObj.name)}
                            aria-label={iconObj.name}
                          >
                            <IconComp className="h-5 w-5" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>{iconObj.name}</TooltipContent>
                      </Tooltip>
                    );
                  })}
                </div>
              </TooltipProvider>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setIsAddDepartmentOpen(false)} className="px-4 py-2">Cancel</button>
              <button onClick={handleAddDepartmentSubmit} className="px-4 py-2 bg-blue-600 text-white rounded">Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

