import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-red-50 p-10 font-sans">
          <div className="max-w-2xl w-full bg-white rounded-xl shadow-2xl overflow-hidden border border-red-200">
            <div className="bg-red-600 px-6 py-4">
               <h1 className="text-white text-xl font-bold flex items-center gap-2">
                 ⚠️ Something went wrong.
               </h1>
            </div>
            <div className="p-8">
              <p className="text-gray-700 mb-4">The application crashed. Here is the error message:</p>
              
              <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto mb-6">
                 <code className="text-red-400 font-mono text-sm block">
                   {this.state.error && this.state.error.toString()}
                 </code>
                 {this.state.errorInfo && (
                    <pre className="text-gray-500 text-xs mt-2">
                        {this.state.errorInfo.componentStack}
                    </pre>
                 )}
              </div>

              <div className="flex justify-end gap-3">
                 <button 
                    onClick={() => window.location.href = '/login'}
                    className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-800 font-medium transition-colors"
                 >
                    Go to Login
                 </button>
                 <button 
                    onClick={() => window.location.reload()}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-medium transition-colors"
                 >
                    Reload Page
                 </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
