export async function generateReport(selectedCharts: string[], email?: string) {
    const response = await fetch("/api/generate-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selectedCharts, email }),
    });
  
    if (!response.ok) throw new Error("Failed to generate report");
  
    return response.json();
  }