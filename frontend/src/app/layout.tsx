import './globals.css';
import { Inter } from "next/font/google";
import Layout from '@/components/Layout';

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        {children} {/* No <Layout> here! Page.tsx handles it */}
      </body>
    </html>
  );
}