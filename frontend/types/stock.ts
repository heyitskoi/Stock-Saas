export interface Department {
  id: number;
  name: string;
  icon?: string;
}

export interface Category {
  id: number;
  name: string;
  department_id: number;
  icon?: string;
}

export interface StockItem {
  id: number;
  name: string;
  quantity: number;
  min_par: number;
  category_id: number;
  department_id: number;
  stock_code?: string;
  status?: string;
}

export interface StockHistoryEntry {
  id: number;
  item_id: number;
  change: number;
  timestamp: string;
  note?: string;
}

export interface DepartmentStock {
  departmentId: string;
  itemId: string;
  quantity: number;
}
