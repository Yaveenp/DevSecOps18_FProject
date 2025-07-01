import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity, RefreshCw, Plus, Minus } from 'lucide-react';

interface PortfolioHistoryEntry {
  date: string;
  value: number;
  gain: number;
  gainPercent: string;
}

const PortfolioDashboard = () => {
  const [portfolioData, setPortfolioData] = useState<PortfolioHistoryEntry[]>([]);
  const [stocks, setStocks] = useState([
    { symbol: 'AAPL', name: 'Apple Inc.', shares: 10, price: 150.25, change: 2.45, changePercent: 1.66 },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', shares: 5, price: 2750.80, change: -15.20, changePercent: -0.55 },
    { symbol: 'MSFT', name: 'Microsoft Corp.', shares: 8, price: 420.15, change: 8.30, changePercent: 2.01 },
    { symbol: 'TSLA', name: 'Tesla Inc.', shares: 12, price: 185.50, change: -3.75, changePercent: -1.98 },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', shares: 6, price: 3180.45, change: 25.60, changePercent: 0.81 }
  ]);
  const [totalValue, setTotalValue] = useState(0);
  const [totalGain, setTotalGain] = useState(0);
  const [isUpdating, setIsUpdating] = useState(false);

  // Generate historical portfolio data
  useEffect(() => {
    const generateHistoricalData = () => {
      const data = [];
      const startValue = 50000;
      let currentValue = startValue;
      
      for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        // Simulate realistic portfolio growth with some volatility
        const dailyChange = (Math.random() - 0.48) * 0.03; // Slight upward bias
        currentValue = currentValue * (1 + dailyChange);
        
        data.push({
          date: date.toLocaleDateString(),
          value: Math.round(currentValue),
          gain: Math.round(currentValue - startValue),
          gainPercent: ((currentValue - startValue) / startValue * 100).toFixed(2)
        });
      }
      return data;
    };

    setPortfolioData(generateHistoricalData());
  }, []);

  // Calculate total portfolio value and gain
  useEffect(() => {
    const total = stocks.reduce((sum, stock) => sum + (stock.shares * stock.price), 0);
    const initialValue = 50000; // Assuming initial investment
    setTotalValue(total);
    setTotalGain(total - initialValue);
  }, [stocks]);

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStocks(prevStocks => 
        prevStocks.map(stock => {
          const priceChange = (Math.random() - 0.5) * 2; // Random change between -1 and 1
          const newPrice = Math.max(stock.price + priceChange, 0.01);
          const changePercent = ((newPrice - stock.price) / stock.price * 100);
          
          return {
            ...stock,
            price: parseFloat(newPrice.toFixed(2)),
            change: parseFloat(priceChange.toFixed(2)),
            changePercent: parseFloat(changePercent.toFixed(2))
          };
        })
      );
    }, 3000); // Update every 3 seconds

    return () => clearInterval(interval);
  }, []);

  const handleManualRefresh = () => {
    setIsUpdating(true);
    setTimeout(() => setIsUpdating(false), 1000);
  };

  const addStock = () => {
    const newStock = {
      symbol: 'NEW',
      name: 'New Stock',
      shares: 1,
      price: 100.00,
      change: 0,
      changePercent: 0
    };
    setStocks([...stocks, newStock]);
  };

  const removeStock = (index) => {
    setStocks(stocks.filter((_, i) => i !== index));
  };

  const pieData = stocks.map(stock => ({
    name: stock.symbol,
    value: stock.shares * stock.price,
    color: `hsl(${Math.random() * 360}, 70%, 50%)`
  }));

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Portfolio Dashboard</h1>
              <p className="text-gray-300">Real-time portfolio tracking and analytics</p>
            </div>
            <button
              onClick={handleManualRefresh}
              className={`flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${isUpdating ? 'animate-pulse' : ''}`}
            >
              <RefreshCw className={`w-4 h-4 ${isUpdating ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </header>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total Value</p>
                <p className="text-2xl font-bold text-white">${totalValue.toLocaleString()}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-400" />
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total Gain/Loss</p>
                <p className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${totalGain.toLocaleString()}
                </p>
              </div>
              {totalGain >= 0 ? 
                <TrendingUp className="w-8 h-8 text-green-400" /> : 
                <TrendingDown className="w-8 h-8 text-red-400" />
              }
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Return %</p>
                <p className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {((totalGain / 50000) * 100).toFixed(2)}%
                </p>
              </div>
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Holdings</p>
                <p className="text-2xl font-bold text-white">{stocks.length}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={addStock}
                  className="p-1 bg-green-600 rounded hover:bg-green-700 transition-colors"
                >
                  <Plus className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Portfolio Growth Chart */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Portfolio Growth</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={portfolioData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }} 
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#8B5CF6" 
                  strokeWidth={3}
                  dot={{ fill: '#8B5CF6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Portfolio Allocation */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Portfolio Allocation</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Stock Holdings Table */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Stock Holdings</h3>
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              Live Updates
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-300 pb-2">Symbol</th>
                  <th className="text-left text-gray-300 pb-2">Name</th>
                  <th className="text-right text-gray-300 pb-2">Shares</th>
                  <th className="text-right text-gray-300 pb-2">Price</th>
                  <th className="text-right text-gray-300 pb-2">Change</th>
                  <th className="text-right text-gray-300 pb-2">Market Value</th>
                  <th className="text-right text-gray-300 pb-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {stocks.map((stock, index) => (
                  <tr key={index} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                    <td className="py-3 text-white font-medium">{stock.symbol}</td>
                    <td className="py-3 text-gray-300">{stock.name}</td>
                    <td className="py-3 text-right text-white">{stock.shares}</td>
                    <td className="py-3 text-right text-white">${stock.price.toFixed(2)}</td>
                    <td className={`py-3 text-right ${stock.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                    </td>
                    <td className="py-3 text-right text-white">${(stock.shares * stock.price).toFixed(2)}</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => removeStock(index)}
                        className="p-1 bg-red-600 rounded hover:bg-red-700 transition-colors"
                      >
                        <Minus className="w-4 h-4 text-white" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioDashboard;