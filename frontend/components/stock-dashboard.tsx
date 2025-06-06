import { Category } from '../types/stock';
import { apiFetch, apiGet } from '../lib/api';
import { useToast } from '@/components/ui/use-toast';
import { useState } from 'react';

const isDev = process.env.NODE_ENV === 'development';

interface LoadingState {
  categories: boolean;
  [key: string]: boolean;
}

export default function StockDashboard() {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState<LoadingState>({ categories: false });
  const [categories, setCategories] = useState<Category[]>([]);
  const [addCategoryOpen, setAddCategoryOpen] = useState(false);

  const handleCreateCategory = async (categoryData: Omit<Category, "id">) => {
    try {
      // Set loading state for categories
      setIsLoading(prev => ({ ...prev, categories: true }));

      if (isDev) console.log("Creating category with data:", categoryData);
      const newCategory = await apiFetch<Category>("/api/categories/", {
        method: "POST",
        body: {
          name: categoryData.name,
          icon: categoryData.icon || "Package",
          department_id: categoryData.department_id,
        },
      });
      if (isDev) console.log("API response:", newCategory);

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
  };

  return (
    <div>
      {/* Add your dashboard UI here */}
    </div>
  );
}
