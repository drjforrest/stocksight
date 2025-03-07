import './globals.css';
import type { Metadata } from 'next';
import { Inter } from "next/font/google";
import React from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: 'StockSight',
  description: 'Real-time stock tracking and IPO insights',
};

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900">
          {children}
        </main>
      </div>
    </div>
  );
}