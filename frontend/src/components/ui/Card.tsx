import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = "" }: CardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 ${className}`}>
      {children}
    </div>
  );
}

function CardContent({ children, className = "" }: CardContentProps) {
  return <div className={`mt-2 ${className}`}>{children}</div>;
}

export { Card, CardContent };