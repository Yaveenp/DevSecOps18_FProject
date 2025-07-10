import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

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
      const response = await fetch(`${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
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
          setFormData({ username: '', password: '', first_name: '', last_name: '' });
        }
      } else {
        setError(data.message || 'Authentication failed');
      }
    } catch (err) {
      console.error('Network error details:', err);
      setError(`Network error: ${err.message}. Make sure Flask backend is running on port 5050.`);
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
  const [analytics, setAnalytics] = useState(null);
  const [marketData, setMarketData] = useState([]);
  const [searchTicker, setSearchTicker] = useState('');
  const [tickerData, setTickerData] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showMarketOverview, setShowMarketOverview] = useState(false);
  const [editingStock, setEditingStock] = useState(null);

  // Add new stock form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newStock, setNewStock] = useState({
    ticker: '',
    quantity: '',
    buy_price: '',
    company_name: ''
  });

  // Use API_BASE for all API calls, set from env or fallback to relative
  const API_BASE = process.env.REACT_APP_API_URL || '';
  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

  // Fetch portfolio data from backend - GET /api/portfolio
  const fetchPortfolio = async () => {
    if (!isAuthenticated) return;
    
    setLoading(true);
    setError('');
    try {
      console.log('Fetching portfolio...');
      const response = await fetch(`/api/portfolio`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Portfolio response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Portfolio data received:', data);
        
        // Handle different response formats
        const portfolioItems = data.portfolio || data.investments || data || [];
        setStocks(Array.isArray(portfolioItems) ? portfolioItems : []);
        
        // Generate historical data
        const histData = generatePortfolioHistory(portfolioItems);
        setPortfolioData(histData);
      } else if (response.status === 401) {
        // Session expired
        console.log('Session expired, need to re-login');
        handleLogout();
      } else {
        const errorData = await response.json();
        console.error('Portfolio fetch error:', errorData);
        setError(`Failed to fetch portfolio: ${errorData.message || response.statusText}`);
      }
    } catch (err) {
      console.error('Network error:', err);
      setError(`Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fetch analytics - GET /api/portfolio/analytics
  const fetchAnalytics = async () => {
    if (!isAuthenticated) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/portfolio/analytics`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        console.error('Failed to fetch analytics');
      }
    } catch (error) {
      console.error('Analytics fetch error:', error);
    }
  };

  // Fetch market overview - GET /api/stocks/market
  const fetchMarketOverview = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/stocks/market`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMarketData(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch market data');
      }
    } catch (error) {
      console.error('Market data fetch error:', error);
    }
  };

  // Search for specific stock - GET /api/stocks/<ticker>
  const searchStock = async () => {
    if (!searchTicker) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/stocks/${searchTicker.toUpperCase()}`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTickerData(data);
      } else {
        setError(`Stock ${searchTicker} not found`);
        setTickerData(null);
      }
    } catch (error) {
      console.error('Stock search error:', error);
      setError(`Failed to search for ${searchTicker}`);
    }
  };

  // Add new stock - POST /api/portfolio
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
        setError('');
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to add stock');
      }
    } catch (err) {
      setError('Network error adding stock');
    }
  };

  // Update stock - PUT /api/portfolio/<investment_id>
  const handleUpdateStock = async () => {
    if (!editingStock) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/portfolio/${editingStock.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          quantity: parseFloat(editingStock.quantity),
          buy_price: parseFloat(editingStock.buy_price)
        })
      });

      if (response.ok) {
        setEditingStock(null);
        fetchPortfolio(); // Refresh portfolio
        setError('');
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to update stock');
      }
    } catch (err) {
      setError('Network error updating stock');
    }
  };

  // Remove stock - DELETE /api/portfolio/<investment_id>
  const removeStock = async (stockId) => {
    if (!window.confirm('Are you sure you want to remove this stock?')) return;
    
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

  // Generate portfolio history
  const generatePortfolioHistory = (stocksData) => {
    const data = [];
    const today = new Date();
    
    for (let i = 30; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      let totalValue = 0;
      if (Array.isArray(stocksData)) {
        stocksData.forEach(stock => {
          const randomChange = 1 + (Math.random() - 0.5) * 0.1;
          const value = (stock.quantity || 0) * (stock.buy_price || 0) * randomChange;
          totalValue += value;
        });
      }
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: totalValue
      });
    }
    
    return data;
  };

  // Handle login
  const handleLogin = (user) => {
    setUsername(user);
    setIsAuthenticated(true);
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/api/portfolio/signout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    setIsAuthenticated(false);
    setUsername('');
    setStocks([]);
    setPortfolioData([]);
    setAnalytics(null);
    setMarketData([]);
    setError('');
  };

  // Calculate totals with proper formulas
  useEffect(() => {
    if (stocks.length > 0) {
      // Total Value = Current Price × Number of Shares (for each stock)
      const totalVal = stocks.reduce((sum, stock) => {
        const currentPrice = stock.current_price || stock.buy_price || 0;
        const shares = stock.quantity || 0;
        return sum + (currentPrice * shares);
      }, 0);

      // Total Gain/Loss = (Current Price - Buy Price) × Number of Shares (for each stock)
      const totalGainLoss = stocks.reduce((sum, stock) => {
        const currentPrice = stock.current_price || stock.buy_price || 0;
        const buyPrice = stock.buy_price || 0;
        const shares = stock.quantity || 0;
        return sum + ((currentPrice - buyPrice) * shares);
      }, 0);

      setTotalValue(totalVal);
      setTotalGain(totalGainLoss);
    } else {
      setTotalValue(0);
      setTotalGain(0);
    }
  }, [stocks]);

  // Fetch data when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchPortfolio();
      fetchAnalytics();
      fetchMarketOverview();
    }
  }, [isAuthenticated]);

  // Handle manual refresh
  const handleManualRefresh = () => {
    setIsUpdating(true);
    fetchPortfolio();
    fetchAnalytics();
    fetchMarketOverview();
    setTimeout(() => setIsUpdating(false), 1000);
  };

  // If not authenticated, show login form
  if (!isAuthenticated) {
    return <AuthForm onLogin={handleLogin} />;
  }

  // Prepare data for charts
  const pieData = stocks.map(stock => ({
    name: stock.ticker,
    value: (stock.current_price || stock.buy_price || 0) * stock.quantity
  }));

  // Calculate portfolio return percentage
  const getPortfolioReturn = () => {
    if (stocks.length === 0) return 0;
    
    const totalInvestment = stocks.reduce((sum, stock) => {
      return sum + ((stock.buy_price || 0) * (stock.quantity || 0));
    }, 0);
    
    const totalCurrentValue = stocks.reduce((sum, stock) => {
      const currentPrice = stock.current_price || stock.buy_price || 0;
      return sum + (currentPrice * (stock.quantity || 0));
    }, 0);
    
    if (totalInvestment > 0) {
      return ((totalCurrentValue - totalInvestment) / totalInvestment) * 100;
    }
    return 0;
  };

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

        {/* Quick Actions Bar */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mb-6 flex gap-4 flex-wrap border border-white/20">
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
          >
            ➕ Add Stock
          </button>
          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
          >
            📊 {showAnalytics ? 'Hide' : 'Show'} Analytics
          </button>
          <button
            onClick={() => setShowMarketOverview(!showMarketOverview)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
          >
            🌍 {showMarketOverview ? 'Hide' : 'Show'} Market
          </button>
          <div className="flex gap-2 ml-auto">
            <input
              type="text"
              placeholder="Search ticker..."
              value={searchTicker}
              onChange={(e) => setSearchTicker(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchStock()}
              className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400"
            />
            <button
              onClick={searchStock}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
            >
              🔍 Search
            </button>
          </div>
        </div>

        {/* Stock Search Result */}
        {tickerData && (
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Stock Information: {tickerData.ticker}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-300 text-sm">Current Price</p>
                <p className="text-2xl font-bold text-white">${tickerData.current_price?.toFixed(2) || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Day Change</p>
                <p className={`text-2xl font-bold ${tickerData.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {tickerData.change >= 0 ? '+' : ''}{tickerData.change?.toFixed(2) || 0}%
                </p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Volume</p>
                <p className="text-2xl font-bold text-white">{tickerData.volume?.toLocaleString() || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Market Cap</p>
                <p className="text-2xl font-bold text-white">
                  {tickerData.market_cap ? `$${(tickerData.market_cap / 1000000000).toFixed(2)}B` : 'N/A'}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                setNewStock({ ...newStock, ticker: tickerData.ticker });
                setShowAddForm(true);
                setTickerData(null);
              }}
              className="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
            >
              Add to Portfolio
            </button>
          </div>
        )}

        {/* Market Overview */}
        {showMarketOverview && marketData.length > 0 && (
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Market Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {marketData.map((market, index) => (
                <div key={index} className="bg-white/10 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white">{market.name || market.ticker}</h4>
                  <p className="text-2xl font-bold text-white">{market.value?.toFixed(2) || market.price?.toFixed(2)}</p>
                  <p className={`text-sm ${market.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {market.change >= 0 ? '+' : ''}{market.change?.toFixed(2)}%
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Section */}
        {showAnalytics && analytics && (
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Portfolio Analytics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-300 text-sm">Best Performer</p>
                <p className="text-lg font-bold text-green-400">{analytics.best_performer?.ticker || 'N/A'}</p>
                <p className="text-sm text-green-300">
                  {analytics.best_performer?.return ? `+${analytics.best_performer.return}%` : ''}
                </p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Worst Performer</p>
                <p className="text-lg font-bold text-red-400">{analytics.worst_performer?.ticker || 'N/A'}</p>
                <p className="text-sm text-red-300">
                  {analytics.worst_performer?.return ? `${analytics.worst_performer.return}%` : ''}
                </p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Portfolio Volatility</p>
                <p className="text-lg font-bold text-white">{analytics.volatility?.toFixed(2) || '0.00'}%</p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Sharpe Ratio</p>
                <p className="text-lg font-bold text-white">{analytics.sharpe_ratio?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          </div>
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
                  {totalGain >= 0 ? '+' : ''}${Math.abs(totalGain).toLocaleString()}
                </p>
              </div>
              <span className="text-2xl">{totalGain >= 0 ? '📈' : '📉'}</span>
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Return %</p>
                <p className={`text-2xl font-bold ${getPortfolioReturn() >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {getPortfolioReturn() >= 0 ? '+' : ''}{getPortfolioReturn().toFixed(2)}%
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
              <span className="text-2xl">🗂️</span>
            </div>
          </div>
        </div>

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
                  name="Portfolio Value"
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

        {/* Add Stock Form Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-slate-800 rounded-xl p-6 border border-white/20 w-full max-w-md">
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
                  placeholder="Company Name (optional)"
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
                    onClick={() => {
                      setShowAddForm(false);
                      setNewStock({ ticker: '', quantity: '', buy_price: '', company_name: '' });
                    }}
                    className="flex-1 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Stock Holdings Table */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Stock Holdings</h3>
            <div className="flex items-center gap-2 text-sm text-gray-300">
              {loading ? (
                <>
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  Loading...
                </>
              ) : (
                <>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  Connected to Backend
                </>
              )}
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
                  {stocks.map((stock, index) => {
                    const currentPrice = stock.current_price || stock.buy_price || 0;
                    const buyPrice = stock.buy_price || 0;
                    const quantity = stock.quantity || 0;
                    const marketValue = currentPrice * quantity;
                    const gainLoss = (currentPrice - buyPrice) * quantity;
                    const gainPercent = buyPrice > 0 ? ((currentPrice - buyPrice) / buyPrice) * 100 : 0;
                    
                    return (
                      <tr key={stock.id || index} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                        <td className="py-3 text-white font-medium">{stock.ticker}</td>
                        <td className="py-3 text-gray-300">{stock.company_name || 'N/A'}</td>
                        <td className="py-3 text-right text-white">
                          {editingStock?.id === stock.id ? (
                            <input
                              type="number"
                              value={editingStock.quantity}
                              onChange={(e) => setEditingStock({...editingStock, quantity: e.target.value})}
                              className="w-20 px-2 py-1 bg-white/10 border border-white/20 rounded text-white"
                            />
                          ) : (
                            quantity
                          )}
                        </td>
                        <td className="py-3 text-right text-white">
                          {editingStock?.id === stock.id ? (
                            <input
                              type="number"
                              value={editingStock.buy_price}
                              onChange={(e) => setEditingStock({...editingStock, buy_price: e.target.value})}
                              className="w-24 px-2 py-1 bg-white/10 border border-white/20 rounded text-white"
                            />
                          ) : (
                            `${buyPrice.toFixed(2)}`
                          )}
                        </td>
                        <td className="py-3 text-right text-white">${currentPrice.toFixed(2)}</td>
                        <td className="py-3 text-right text-white">${marketValue.toFixed(2)}</td>
                        <td className={`py-3 text-right ${gainLoss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          ${Math.abs(gainLoss).toFixed(2)} ({gainPercent >= 0 ? '+' : ''}{gainPercent.toFixed(2)}%)
                        </td>
                        <td className="py-3 text-right">
                          {editingStock?.id === stock.id ? (
                            <div className="flex gap-2 justify-end">
                              <button
                                onClick={handleUpdateStock}
                                className="text-green-400 hover:text-green-300"
                              >
                                ✓
                              </button>
                              <button
                                onClick={() => setEditingStock(null)}
                                className="text-red-400 hover:text-red-300"
                              >
                                ✕
                              </button>
                            </div>
                          ) : (
                            <div className="flex gap-2 justify-end">
                              <button
                                onClick={() => setEditingStock({
                                  id: stock.id,
                                  quantity: stock.quantity,
                                  buy_price: stock.buy_price
                                })}
                                className="text-blue-400 hover:text-blue-300"
                              >
                                ✏️
                              </button>
                              <button
                                onClick={() => removeStock(stock.id)}
                                className="text-red-400 hover:text-red-300"
                              >
                                🗑️
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
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