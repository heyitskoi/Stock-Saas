"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import {
  Computer,
  Briefcase,
  Truck,
  Plus,
  CheckCircle,
  XCircle,
  Package,
  Users,
  MoreVertical,
  Edit,
  Trash2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import type { Department, Category } from "@/types/stock"
import { ICON_LIST } from "./iconList"

interface SidebarProps {
  departments: Department[]
  categories: Category[]
  selectedDepartment: number | null
  onSelectDepartment: (departmentId: number | null) => void
  onAddDepartment: () => void
  onAddCategory: () => void
  onEditDepartment?: (department: Department) => void
  onDeleteDepartment?: (departmentId: number) => void
  onEditCategory?: (category: Category) => void
  onDeleteCategory?: (categoryId: number) => void
}

export function Sidebar({
  departments,
  categories,
  selectedDepartment,
  onSelectDepartment,
  onAddDepartment,
  onAddCategory,
  onEditDepartment,
  onDeleteDepartment,
  onEditCategory,
  onDeleteCategory,
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { user } = useAuth()
  const isDev = process.env.NODE_ENV === "development"
  const isAdminOrManager = user?.is_admin === true || isDev
  const isAdmin = user?.is_admin === true || isDev

  const getIconComponent = (iconName: string) => {
    const found = ICON_LIST.find(iconObj => iconObj.name === iconName);
    if (found) {
      const IconComp = found.icon;
      return <IconComp className="h-5 w-5" />;
    }
    // fallback
    const DefaultIcon = ICON_LIST[0].icon;
    return <DefaultIcon className="h-5 w-5" />;
  }

  // Get categories for the selected department
  const departmentCategories = selectedDepartment
    ? categories.filter((category) => category.department_id === selectedDepartment)
    : []

  return (
    <div
      className={cn(
        "bg-muted/40 border-r flex flex-col h-full transition-all duration-300",
        isCollapsed ? "w-[70px]" : "w-[250px]",
      )}
    >
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Departments Section */}
          <div>
            <h2 className={cn("text-sm font-semibold mb-2", isCollapsed && "text-center")}>
              {!isCollapsed && "Departments"}
            </h2>
            <div className="space-y-1">
              {departments.map((department) => (
                <div key={department.id} className="flex items-center">
                  <Button
                    variant={selectedDepartment === department.id ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start",
                      isCollapsed && "justify-center px-2",
                      !isCollapsed && "rounded-r-none",
                    )}
                    onClick={() => onSelectDepartment(selectedDepartment === department.id ? null : department.id)}
                  >
                    {getIconComponent(department.icon)}
                    {!isCollapsed && <span className="ml-2">{department.name}</span>}
                  </Button>

                  {!isCollapsed && isAdminOrManager && onEditDepartment && onDeleteDepartment && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-9 w-9 rounded-l-none border-l">
                          <MoreVertical className="h-4 w-4" />
                          <span className="sr-only">Department actions</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-40">
                        <DropdownMenuItem onClick={() => onEditDepartment(department)}>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => onDeleteDepartment(department.id)}
                          className="text-red-600 focus:text-red-600"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              ))}
              {isAdminOrManager && (
                <Button
                  variant="ghost"
                  className={cn("w-full justify-start text-muted-foreground", isCollapsed && "justify-center px-2")}
                  onClick={onAddDepartment}
                >
                  <Plus className="h-5 w-5" />
                  {!isCollapsed && <span className="ml-2">Add Department</span>}
                </Button>
              )}
            </div>
          </div>

          {/* Admin Section */}
          {isAdmin && (
            <div>
              <h2 className={cn("text-sm font-semibold mb-2", isCollapsed && "text-center")}>
                {!isCollapsed && "Admin"}
              </h2>
              <div className="space-y-1">
                <Button
                  variant="ghost"
                  className={cn("w-full justify-start", isCollapsed && "justify-center px-2")}
                  asChild
                >
                  <a href="/admin/rbac-dashboard">
                    <Computer className="h-5 w-5" />
                    {!isCollapsed && <span className="ml-2">RBAC Dashboard</span>}
                  </a>
                </Button>
                <Button
                  variant="ghost"
                  className={cn("w-full justify-start", isCollapsed && "justify-center px-2")}
                  asChild
                >
                  <a href="/admin/users">
                    <Users className="h-5 w-5" />
                    {!isCollapsed && <span className="ml-2">User Management</span>}
                  </a>
                </Button>
              </div>
            </div>
          )}

          {/* Categories Section */}
          <div>
            <h2 className={cn("text-sm font-semibold mb-2", isCollapsed && "text-center")}>
              {!isCollapsed && (selectedDepartment ? "Categories" : "Quick Filters")}
            </h2>
            <div className="space-y-1">
              {selectedDepartment ? (
                // Show categories for selected department
                departmentCategories.length > 0 ? (
                  departmentCategories.map((category) => (
                    <div key={category.id} className="flex items-center">
                      <Button
                        variant="ghost"
                        className={cn(
                          "w-full justify-start",
                          isCollapsed && "justify-center px-2",
                          !isCollapsed && "rounded-r-none",
                        )}
                      >
                        <Package className="h-5 w-5" />
                        {!isCollapsed && <span className="ml-2">{category.name}</span>}
                      </Button>

                      {!isCollapsed && onEditCategory && onDeleteCategory && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-l-none border-l">
                              <MoreVertical className="h-4 w-4" />
                              <span className="sr-only">Category actions</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-40">
                            <DropdownMenuItem onClick={() => onEditCategory(category)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => onDeleteCategory(category.id)}
                              className="text-red-600 focus:text-red-600"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="px-2 py-3 text-sm text-muted-foreground">
                    {!isCollapsed && "No categories in this department"}
                  </div>
                )
              ) : (
                // Show quick filters when no department is selected
                <>
                  <Button variant="ghost" className={cn("w-full justify-start", isCollapsed && "justify-center px-2")}>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    {!isCollapsed && <span className="ml-2">Available Stock</span>}
                  </Button>
                  <Button variant="ghost" className={cn("w-full justify-start", isCollapsed && "justify-center px-2")}>
                    <XCircle className="h-5 w-5 text-red-500" />
                    {!isCollapsed && <span className="ml-2">Out of Stock</span>}
                  </Button>
                  <Button variant="ghost" className={cn("w-full justify-start", isCollapsed && "justify-center px-2")}>
                    <Package className="h-5 w-5 text-yellow-500" />
                    {!isCollapsed && <span className="ml-2">Ordered Stock</span>}
                  </Button>
                  <Button variant="ghost" className={cn("w-full justify-start", isCollapsed && "justify-center px-2")}>
                    <Users className="h-5 w-5 text-blue-500" />
                    {!isCollapsed && <span className="ml-2">Distributors List</span>}
                  </Button>
                </>
              )}

              {selectedDepartment && (
                <Button
                  variant="ghost"
                  className={cn("w-full justify-start text-muted-foreground", isCollapsed && "justify-center px-2")}
                  onClick={onAddCategory}
                >
                  <Plus className="h-5 w-5" />
                  {!isCollapsed && <span className="ml-2">Add Category</span>}
                </Button>
              )}
            </div>
          </div>
        </div>
      </ScrollArea>

      {/* Collapse Button */}
      <Button variant="ghost" size="sm" className="m-2" onClick={() => setIsCollapsed(!isCollapsed)}>
        {isCollapsed ? "→" : "←"}
      </Button>
    </div>
  )
}
