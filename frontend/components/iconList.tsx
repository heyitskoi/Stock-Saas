import {
  Computer,
  Briefcase,
  Truck,
  Package,
  Users,
  CheckCircle,
  XCircle,
  MoreVertical,
  Edit,
  Trash2,
  Plus,
} from "lucide-react";

export const ICON_LIST = [
  { name: "Computer", icon: Computer },
  { name: "Briefcase", icon: Briefcase },
  { name: "Truck", icon: Truck },
  { name: "Package", icon: Package },
  { name: "Users", icon: Users },
  { name: "CheckCircle", icon: CheckCircle },
  { name: "XCircle", icon: XCircle },
  { name: "MoreVertical", icon: MoreVertical },
  { name: "Edit", icon: Edit },
  { name: "Trash2", icon: Trash2 },
  { name: "Plus", icon: Plus },
];

export type IconName = typeof ICON_LIST[number]["name"]; 