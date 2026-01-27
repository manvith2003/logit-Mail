import React from 'react';
import { LogIn } from 'lucide-react';

const Login = () => {
  const handleGoogleLogin = () => {
    // Redirect to backend Google Login endpoint
    window.location.href = 'http://localhost:8000/api/v1/auth/login/google';
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">Magic Mail AI</h1>
        <p className="text-gray-600 text-center mb-8">Sign in to manage your emails intelligently</p>
        
        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 transition-colors duration-200 font-medium"
        >
          <LogIn size={20} />
          Sign in with Google
        </button>
      </div>
    </div>
  );
};

export default Login;
