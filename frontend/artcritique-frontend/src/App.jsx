import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Pages
import Home from './pages/Home';
import Gallery from './pages/Gallery';
import ArtworkList from './pages/ArtworkList';
import ArtworkDetail from './pages/ArtworkDetail';
import ArtworkUpload from './pages/ArtworkUpload';
import Login from './pages/Login';
import Register from './pages/Register';

// Components
import Navbar from './components/Navbar';
import ProfilePage from './components/ProfilePage';
import ArtworkForm from './components/ArtworkForm';

// Authentication Context
import { AuthProvider, useAuth } from './context/AuthContext';

// Protected Route wrapper component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    // Store the current location to redirect back after login
    sessionStorage.setItem('redirect_after_login', window.location.pathname);
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Main App Routes component that uses the auth context
const AppRoutes = () => {
  const { user, loading, isAuthenticated, logout } = useAuth();
  
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
    <div className="app-container">
      <Navbar user={user} isAuthenticated={isAuthenticated} onLogout={logout} />
      
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/artworks" element={<ArtworkList />} />
          <Route path="/artworks/:id" element={<ArtworkDetail />} />
          <Route 
            path="/login" 
            element={isAuthenticated ? <Navigate to="/" /> : <Login />} 
          />
          <Route 
            path="/register" 
            element={isAuthenticated ? <Navigate to="/" /> : <Register />} 
          />
          
          {/* Protected routes */}
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile/:username" 
            element={<ProfilePage />} 
          />
          <Route 
            path="/my-artworks" 
            element={
              <ProtectedRoute>
                <div className="container mt-5">
                  <h2>My Artworks</h2>
                  <p>Here you'll see all the artwork you've uploaded</p>
                </div>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/upload" 
            element={
              <ProtectedRoute>
                <ArtworkForm mode="create" />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/artwork/:id/edit" 
            element={
              <ProtectedRoute>
                <ArtworkForm mode="edit" />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/notifications" 
            element={
              <ProtectedRoute>
                <div className="container mt-5">
                  <h2>Notifications</h2>
                  <p>Check your latest notifications</p>
                </div>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <div className="container mt-5">
                  <h2>Account Settings</h2>
                  <p>Manage your account preferences</p>
                </div>
              </ProtectedRoute>
            } 
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
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;