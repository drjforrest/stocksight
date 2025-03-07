import { Search } from "lucide-react";
import { Icon } from '@iconify/react';

export function Navbar() {
    return (
      <div className="h-16 w-full bg-white shadow-md flex items-center px-6 justify-between dark:bg-gray-800">
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <div className="flex items-center space-x-4">
          <input 
            type="text" 
            placeholder="Search..." 
            className="px-4 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600" 
          />
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Search</button>
        </div>
      </div>
    );
  }