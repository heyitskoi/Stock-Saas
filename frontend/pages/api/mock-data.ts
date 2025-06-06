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

export let departments: Department[] = [
  { id: 1, name: "Systems", icon: "Computer" },
  { id: 2, name: "Accounts/Warehouse", icon: "Briefcase" },
  { id: 3, name: "Field Services", icon: "Truck" },
];

export let categories: Category[] = [
  { id: 1, name: "Desktop Parts", department_id: 1 },
  { id: 2, name: "Switches/Routers", department_id: 1 },
  { id: 3, name: "Cables", department_id: 1 },
  { id: 4, name: "Office Supplies", department_id: 2 },
  { id: 5, name: "Tools", department_id: 3 },
];

export let items: StockItem[] = [
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
];
