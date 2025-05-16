import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Pages
import Home from './pages/Home';
import ArtworkList from './pages/ArtworkList';
import ArtworkDetail from './pages/ArtworkDetail';
import Login from './pages/Login';
import Register from './pages/Register';

// Components
import Navbar from './components/Navbar';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // In a real app, we would check if the user is already logged in
  useEffect(() => {
    // Simulating a session check
    const checkSession = async () => {
      try {
        // This would be an API call to check the session
        // Example: const response = await authAPI.checkSession();
        
        // For the demo, we'll check localStorage for a user session
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('Session check failed', error);
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    // Store in localStorage for demo purposes (in a real app, this would be handled by cookies)
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    // In a real app, this would also call an API endpoint to logout
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app-container">
        <Navbar user={user} onLogout={handleLogout} />
        
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/artworks" element={<ArtworkList />} />
            <Route path="/artworks/:id" element={<ArtworkDetail />} />
            <Route 
              path="/login" 
              element={user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />} 
            />
            <Route 
              path="/register" 
              element={user ? <Navigate to="/" /> : <Register onLogin={handleLogin} />} 
            />
            
            {/* Protected routes */}
            <Route 
              path="/profile" 
              element={user ? <div>Profile Page (To be implemented)</div> : <Navigate to="/login" />} 
            />
            <Route 
              path="/my-artworks" 
              element={user ? <div>My Artworks Page (To be implemented)</div> : <Navigate to="/login" />} 
            />
            <Route 
              path="/upload" 
              element={user ? <div>Upload Artwork Page (To be implemented)</div> : <Navigate to="/login" />} 
            />
            <Route 
              path="/notifications" 
              element={user ? <div>Notifications Page (To be implemented)</div> : <Navigate to="/login" />} 
            />
            <Route 
              path="/settings" 
              element={user ? <div>Settings Page (To be implemented)</div> : <Navigate to="/login" />} 
            />
            
            {/* Fallback for unknown routes */}
            <Route path="*" element={<div className="container mt-5 text-center"><h2>Page Not Found</h2></div>} />
          </Routes>
        </main>
        
        <footer className="bg-dark text-light mt-5 py-4">
          <div className="container">
            <div className="row">
              <div className="col-md-6">
                <h5>Art Critique</h5>
                <p>A community platform for artists to share work and receive constructive feedback.</p>
              </div>
              <div className="col-md-3">
                <h5>Links</h5>
                <ul className="list-unstyled">
                  <li><a href="/" className="text-light">Home</a></li>
                  <li><a href="/artworks" className="text-light">Browse Artworks</a></li>
                  <li><a href="/login" className="text-light">Login</a></li>
                </ul>
              </div>
              <div className="col-md-3">
                <h5>Connect</h5>
                <ul className="list-unstyled">
                  <li><a href="#" className="text-light">About Us</a></li>
                  <li><a href="#" className="text-light">Contact</a></li>
                  <li><a href="#" className="text-light">Privacy Policy</a></li>
                </ul>
              </div>
            </div>
            <div className="row mt-3">
              <div className="col-12 text-center">
                <p className="mb-0">&copy; {new Date().getFullYear()} Art Critique. All rights reserved.</p>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;