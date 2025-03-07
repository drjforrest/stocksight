'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Dashboard from '../components/Dashboard';
import AdminPanel from '../components/AdminPanel';

export default function Page() {
  const [featureFlags, setFeatureFlags] = useState({ competitor_score: false });

  useEffect(() => {
    // Fetch feature flags (e.g., competitor score toggle)
    axios.get('/api/feature-flags').then((res) => {
      setFeatureFlags(res.data);
    });
  }, []);

  return (
    <main className="p-6">
      {/* Dashboard with Tabs */}
      <Dashboard />

      {/* Admin Panel - Only show if competitor scoring is enabled */}
      {featureFlags.competitor_score && (
        <div className="mt-6">
          <AdminPanel />
        </div>
      )}
    </main>
  );
}