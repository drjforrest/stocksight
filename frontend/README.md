This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## **StockSight Frontend Component Tree Overview**

This is a structured breakdown of the **StockSight** frontend components, based on the provided directory structure.

```
Tree diagram for: /Users/drjforrest/Development/DevProjects/WebDev/stocksight/frontend/src/components/
Generated on: 2025-03-08 01:54:52

├── AdminPanel.tsx
├── WelcomeModel.tsx
├── about
│   └── About.tsx
├── analyze
│   ├── IPOSuccess.tsx
│   ├── MarketDashboard.tsx
│   ├── MarketImpact.tsx
│   ├── MarketShareChart.tsx
│   ├── MarketVolatility.tsx
│   ├── StockChart.tsx
│   ├── StockPrediction.tsx
│   └── StockPrice.tsx
├── browse
│   ├── BrowseCompareTabs.tsx
│   ├── BrowseHelp.tsx
│   ├── CompareCompanies.tsx
│   └── SearchBrowse.tsx
├── dashboard-home
│   ├── Dashboard.tsx
│   ├── MarketOverview.tsx
│   └── TrackedCompaniesList.tsx
├── directory_tree.txt
├── layout
│   ├── Layout.tsx
│   ├── Navbar.tsx
│   └── Sidebar.tsx
├── report
│   └── ReportBuilder.tsx
├── track
│   ├── CompanyNews.tsx
│   ├── CompanyVisualizations.tsx
│   ├── IPOInsights.tsx
│   ├── PipelineComparisonChart.tsx
│   ├── TrackedCompanies.tsx
│   ├── TrackedCompaniesList.tsx
│   ├── TrackedCompanyCard.tsx
│   └── TrackedCompanySearch.tsx
└── ui
    ├── button.tsx
    └── card.tsx

```

---

### **📌 Core UI Components**

**🔷 Layout & Navigation (layout/)**

**	**•**	**Layout.tsx → Main wrapper for pages

**	**•**	**Navbar.tsx** → Global ****top navigation bar**

**	**•**	**Sidebar.tsx → (Optional) Sidebar for admin features

**🔷 UI Elements (ui/)**

**	**•**	**button.tsx → Styled buttons

**	**•**	**card.tsx → UI component for displaying **charts, insights, & summaries**

---

### **🏡 Dashboard (dashboard-home/)**

**📊 ****Dashboard.tsx** → **Main landing page**

**	**•**	****MarketOverview.tsx** → Displays **key stock indices & trends**

**	**•**	****TrackedCompaniesList.tsx** → **Summary of user-tracked firms**

---

### **🔎 Browse & Compare (browse/)**

**BrowseCompareTabs.tsx** → **Tab layout for search & comparison**

**	**•**	**🔍 **SearchBrowse.tsx** → **Company search & filter options**

**	**•**	**📊 **CompareCompanies.tsx** → **Dynamic company comparison**

**	**•**	**ℹ️ **BrowseHelp.tsx** → **Help & instructions for browsing**

---

### **📈 Analyze Market Trends (analyze/)**

This section **integrates AI-powered stock insights** & visualization tools.

**	**•**	**📊 **MarketDashboard.tsx** → **Overview of tracked companies**

**	**•**	**📈 **StockChart.tsx** → **Time-series visualization**

**	**•**	**💡 **StockPrediction.tsx** → **AI-powered stock price forecast**

**	**•**	**💰 **StockPrice.tsx** → **Live & historical stock data**

**	**•**	**📉 **MarketVolatility.tsx** → **Volatility analysis (Sharpe ratio, max drawdown)**

**	**•**	**🔄 **MarketImpact.tsx** → **Competitor reaction analysis**

**	**•**	**🏛 **MarketShareChart.tsx** → **Market dominance vs. competitors**

**	**•**	**📊 **IPOSuccess.tsx** → **IPO success rate & performance**

**🔽 ****🔀 Dynamic Dropdown:**

**	**•**	**Allows users to **switch between Tracked Companies**

---

### **🏛 Tracked Companies (track/)**

**Tracks ****user-selected biotech firms** & monitors  **news, performance, & competition** **.**

**	**•**	**🏛 **TrackedCompanies.tsx** → **List of user-tracked firms**

**	**•**	**📋 **TrackedCompaniesList.tsx** → **Detailed company insights**

**	**•**	**📜 **TrackedCompanyCard.tsx** → **Compact company profile**

**	**•**	**🔎 TrackedCompanySearch.tsx** → ****Add new companies**

**	**•**	**📰 **CompanyNews.tsx** → **Latest SEC & RSS news**

**	**•**	**📈 **CompanyVisualizations.tsx** → **Market cap, FDA approvals, & trials**

**	**•**	**🏆 **PipelineComparisonChart.tsx** → **Pipeline & clinical trial comparison**

**	**•**	**💰 **IPOInsights.tsx** → **IPO trends & market entry analysis**

---

**📑 Report Generation (report/)**

**📄 ****ReportBuilder.tsx** → **Generates & exports reports**

**	**•**	**✅ Users **select charts** to include

**	**•**	**📧 **Email reports** (optional)

**	**•**	**📊 **PDF/CSV export**

---

### **📌 Other Components**

**	**•**	**🛠 **AdminPanel.tsx** → (Admin-only features)

**	**•**	**🎉 **WelcomeModel.tsx** → Intro modal for new users

**	**•**	**📄 **about/About.tsx** → App overview & documentation

---

## **🛠 Improvements in the Pipeline**

**🔹 ****Enhanced ReportBuilder**

**	**•**	**📊 **Live Preview** → See selected charts in real-time

**	**•**	**🎨 **Customize Layouts** → Choose grid, stacked, or tabular formats

**	**•**	**📥 **Auto-save Reports** → Allow users to save **preset report templates**

**🔹 ****Improved Market Analysis**

**	**•**	**📉 **Sentiment Analysis** → Display positive/negative market sentiment

**	**•**	**📅 **Event-Based Tracking** → Track market reaction **before & after key events**

**🔹 ****Refined UI**

**	**•**	**🎨 **Dark Mode Support** (Future enhancement)

**	**•**	**🔄 **Better Animations & Loading States**

---
