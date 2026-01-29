import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import { ToastProvider } from './context/ToastContext';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Login />} /> {/* Default to Login for now */}
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </ToastProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
