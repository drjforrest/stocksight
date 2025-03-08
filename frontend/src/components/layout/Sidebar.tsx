import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  TrendingUp,
  BarChart3,
  Settings,
  FileText,
  List,
} from "lucide-react";
import { cn } from "@/lib/utils"; // Utility function for conditional classNames

export function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    { label: "Dashboard", href: "/", icon: <Home size={20} /> },
    { label: "Browse", href: "/browse", icon: <TrendingUp size={20} /> },
    { label: "Tracked", href: "/tracked", icon: <BarChart3 size={20} /> },
    { label: "Comparison", href: "/compare", icon: <List size={20} /> },
    { label: "Report Builder", href: "/report", icon: <FileText size={20} /> },
    { label: "Analytics", href: "/analytics", icon: <Settings size={20} /> },
  ];

  return (
    <aside className="w-64 h-screen bg-gray-900 text-white p-4 flex flex-col">
      <h1 className="text-xl font-bold mb-6">StockSight</h1>
      <nav className="flex flex-col space-y-4">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700 transition",
              pathname === item.href && "bg-gray-700",
            )}
          >
            {item.icon} {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
