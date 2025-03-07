import React from "react";
import { StockChart } from "@/components/StockChart";
import { MarketTrends } from "@/components/MarketTrends";
import { IPOInsights } from "@/components/IPOInsights";
import { Card, CardContent } from "@/components/ui/card";

export default function Dashboard() {
  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Stock Performance Chart */}
      <Card>
        <CardContent>
          <h2 className="text-xl font-bold mb-4">Stock Performance</h2>
          <StockChart />
        </CardContent>
      </Card>
      
      {/* Market Trends */}
      <Card>
        <CardContent>
          <h2 className="text-xl font-bold mb-4">Market Trends</h2>
          <MarketTrends />
        </CardContent>
      </Card>
      
      {/* IPO Insights */}
      <Card>
        <CardContent>
          <h2 className="text-xl font-bold mb-4">IPO Insights</h2>
          <IPOInsights />
        </CardContent>
      </Card>
    </div>
  );
}
