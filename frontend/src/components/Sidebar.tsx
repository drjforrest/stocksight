import Link from "next/link";
import { Home, TrendingUp, BarChart3, Settings } from "lucide-react";
import { Icon } from '@iconify/react';

export function Sidebar() {
  return (
    <div className="w-64 h-full bg-gray-900 text-white p-4 flex flex-col">
      <h1 className="text-xl font-bold mb-6">StockSight</h1>
      <nav className="flex flex-col space-y-4">
        <Link href="/" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700">
          <Home size={20} /> Dashboard
        </Link>
        <Link href="/browse" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700">
          <TrendingUp size={20} /> Browse
        </Link>
        <Link href="/tracked" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700">
          <BarChart3 size={20} /> Tracked
        </Link>
        <Link href="/analytics" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700 mt-auto">
          <Settings size={20} /> Analytics
        </Link>
      </nav>
    </div>
  );
}