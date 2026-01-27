import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import { ToastProvider } from './context/ToastContext';

function App() {
  return (
    <Router>
      <ToastProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Login />} /> {/* Default to Login for now */}
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </ToastProvider>
    </Router>
  );
}

export default App;
