import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Authentication Component
const AuthForm = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/portfolio/signin' : '/api/portfolio/signup';
      const response = await fetch(`http://localhost:5050${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        if (isLogin) {
          onLogin(formData.username);
        } else {
          setError('Registration successful! Please sign in.');
          setIsLogin(true);
        }
      } else {
        setError(data.message || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error. Make sure the Flask backend is running on port 5050.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20 w-full max-w-md">
        <h2 className="text-3xl font-bold text-white mb-6 text-center">
          {isLogin ? 'Sign In' : 'Sign Up'}
        </h2>
        
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-2 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className="block text-gray-300 mb-2">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              placeholder="Enter password"
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-gray-300 mb-2">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter first name"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2">Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter last name"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
              setFormData({ username: '', password: '', first_name: '', last_name: '' });
            }}
            className="text-blue-400 hover:text-blue-300 transition-colors"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
};

// Main Portfolio Dashboard Component
const PortfolioDashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [portfolioData, setPortfolioData] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [totalValue, setTotalValue] = useState(0);
  const [totalGain, setTotalGain] = useState(0);
  const [isUpdating, setIsUpdating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Add new stock form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newStock, setNewStock] = useState({
    ticker: '',
    quantity: '',
    buy_price: '',
    company_name: ''
  });

  const API_BASE = 'http://localhost:5050';

  // Fetch portfolio data from backend
  const fetchPortfolio = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/portfolio`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.portfolio) {
          setStocks(data.portfolio);
        }
      } else {
        setError('Failed to fetch portfolio data');
      }
    } catch (err) {
      setError('Network error fetching portfolio');
    } finally {
      setLoading(false);
    }
  };

  // Add new stock
  const handleAddStock = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/api/portfolio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ticker: newStock.ticker.toUpperCase(),
          quantity: parseFloat(newStock.quantity),
          buy_price: parseFloat(newStock.buy_price),
          company_name: newStock.company_name
        })
      });

      if (response.ok) {
        setNewStock({ ticker: '', quantity: '', buy_price: '', company_name: '' });
        setShowAddForm(false);
        fetchPortfolio(); // Refresh portfolio
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to add stock');
      }
    } catch (err) {
      setError('Network error adding stock');
    }
  };

  // Remove stock
  const removeStock = async (stockId) => {
    try {
      const response = await fetch(`${API_BASE}/api/portfolio/${stockId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        fetchPortfolio(); // Refresh portfolio
      } else {
        setError('Failed to remove stock');
      }
    } catch (err) {
      setError('Network error removing stock');
    }
  };

  // Handle login
  const handleLogin = (user) => {
    setUsername(user);
    setIsAuthenticated(true);
  };

  // Handle logout
  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername('');
    setStocks([]);
    setPortfolioData([]);
  };

  // Generate historical portfolio data (simulation)
  useEffect(() => {
    if (isAuthenticated) {
      const generateHistoricalData = () => {
        const data = [];
        const startValue = 50000;
        let currentValue = startValue;
        
        for (let i = 30; i >= 0; i--) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          
          const dailyChange = (Math.random() - 0.48) * 0.03;
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
      fetchPortfolio(); // Fetch real portfolio data
    }
  }, [isAuthenticated]);

  // Calculate totals
  useEffect(() => {
    if (stocks.length > 0) {
      const total = stocks.reduce((sum, stock) => sum + (stock.value || 0), 0);
      const totalInvestment = stocks.reduce((sum, stock) => sum + (stock.buy_price * stock.quantity), 0);
      setTotalValue(total);
      setTotalGain(total - totalInvestment);
    }
  }, [stocks]);

  // Handle manual refresh
  const handleManualRefresh = () => {
    setIsUpdating(true);
    fetchPortfolio();
    setTimeout(() => setIsUpdating(false), 1000);
  };

  // If not authenticated, show login form
  if (!isAuthenticated) {
    return <AuthForm onLogin={handleLogin} />;
  }

  const pieData = stocks.map(stock => ({
    name: stock.ticker,
    value: stock.value || 0
  }));

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Portfolio Dashboard</h1>
              <p className="text-gray-300">Welcome back, {username}! Real-time portfolio tracking and analytics</p>
            </div>
            <div className="flex gap-4">
              <button
                onClick={handleManualRefresh}
                className={`flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${isUpdating ? 'animate-pulse' : ''}`}
              >
                🔄 Refresh
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-2 rounded-lg mb-4">
            {error}
            <button onClick={() => setError('')} className="ml-2 text-red-300 hover:text-red-100">×</button>
          </div>
        )}

        {loading && (
          <div className="text-center text-white mb-4">Loading portfolio data...</div>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total Value</p>
                <p className="text-2xl font-bold text-white">${totalValue.toLocaleString()}</p>
              </div>
              <span className="text-2xl">💰</span>
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
              <span className="text-2xl">{totalGain >= 0 ? '📈' : '📉'}</span>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Return %</p>
                <p className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {totalValue > 0 ? ((totalGain / (totalValue - totalGain)) * 100).toFixed(2) : '0.00'}%
                </p>
              </div>
              <span className="text-2xl">📊</span>
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
                  onClick={() => setShowAddForm(true)}
                  className="px-2 py-1 bg-green-600 rounded hover:bg-green-700 transition-colors text-white"
                >
                  + Add Stock
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Add Stock Form Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 w-full max-w-md">
              <h3 className="text-xl font-bold text-white mb-4">Add New Stock</h3>
              <form onSubmit={handleAddStock} className="space-y-4">
                <input
                  type="text"
                  placeholder="Ticker (e.g., AAPL)"
                  value={newStock.ticker}
                  onChange={(e) => setNewStock({...newStock, ticker: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400"
                  required
                />
                <input
                  type="text"
                  placeholder="Company Name"
                  value={newStock.company_name}
                  onChange={(e) => setNewStock({...newStock, company_name: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400"
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Quantity"
                  value={newStock.quantity}
                  onChange={(e) => setNewStock({...newStock, quantity: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400"
                  required
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Buy Price"
                  value={newStock.buy_price}
                  onChange={(e) => setNewStock({...newStock, buy_price: e.target.value})}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400"
                  required
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Add Stock
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
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
              Connected to Backend
            </div>
          </div>
          
          {stocks.length === 0 ? (
            <div className="text-center text-gray-300 py-8">
              <p>No stocks in your portfolio yet.</p>
              <button
                onClick={() => setShowAddForm(true)}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Your First Stock
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left text-gray-300 pb-2">Symbol</th>
                    <th className="text-left text-gray-300 pb-2">Name</th>
                    <th className="text-right text-gray-300 pb-2">Shares</th>
                    <th className="text-right text-gray-300 pb-2">Buy Price</th>
                    <th className="text-right text-gray-300 pb-2">Current Price</th>
                    <th className="text-right text-gray-300 pb-2">Market Value</th>
                    <th className="text-right text-gray-300 pb-2">Gain/Loss</th>
                    <th className="text-right text-gray-300 pb-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {stocks.map((stock, index) => (
                    <tr key={stock.id || index} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                      <td className="py-3 text-white font-medium">{stock.ticker}</td>
                      <td className="py-3 text-gray-300">{stock.company_name || 'N/A'}</td>
                      <td className="py-3 text-right text-white">{stock.quantity}</td>
                      <td className="py-3 text-right text-white">${stock.buy_price?.toFixed(2) || '0.00'}</td>
                      <td className="py-3 text-right text-white">${stock.current_price?.toFixed(2) || '0.00'}</td>
                      <td className="py-3 text-right text-white">${stock.value?.toFixed(2) || '0.00'}</td>
                      <td className={`py-3 text-right ${(stock.gain || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ${stock.gain?.toFixed(2) || '0.00'} ({stock.change_percent?.toFixed(2) || '0.00'}%)
                      </td>
                      <td className="py-3 text-right">
                        <button
                          onClick={() => removeStock(stock.id)}
                          className="px-2 py-1 bg-red-600 rounded hover:bg-red-700 transition-colors text-white"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioDashboard;