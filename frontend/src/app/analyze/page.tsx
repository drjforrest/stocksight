'use client';

import React from 'react';
import MarketDashboard from '@/components/analyze/MarketDashboard';

export default function AnalyzePage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Market Analysis</h1>
      <MarketDashboard />
    </div>
  );
} 