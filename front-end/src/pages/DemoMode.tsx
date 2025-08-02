import React from 'react';
import { Link } from 'react-router-dom';

const DemoMode: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-black to-purple-500 flex items-center justify-center">
      <div className="text-center text-white max-w-2xl mx-auto p-8">
        <h1 className="text-4xl font-bold mb-6">🎨 STYLUX AI Fashion Assistant</h1>
        
        <div className="bg-yellow-600 text-white p-4 rounded-lg mb-8">
          <p className="font-semibold">Demo Mode - Authentication Disabled</p>
          <p className="text-sm mt-2">
            The app is running without authentication. You can still test the AI chatbot!
          </p>
        </div>

        <div className="space-y-4">
          <Link 
            to="/chatbot"
            className="block bg-purple-600 text-white px-8 py-4 rounded-lg hover:bg-purple-700 transition-colors text-lg font-semibold"
          >
            🚀 Try the AI Fashion Chatbot
          </Link>
          
          <Link 
            to="/"
            className="block bg-gray-600 text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition-colors"
          >
            🏠 Go to Homepage
          </Link>
        </div>

        <div className="mt-8 text-gray-300 text-sm">
          <p>💡 To enable full authentication features:</p>
          <p>1. Get your Clerk key from <a href="https://dashboard.clerk.com/" className="text-purple-400 underline">dashboard.clerk.com</a></p>
          <p>2. Add it to <code className="bg-gray-800 px-2 py-1 rounded">front-end/.env.local</code></p>
        </div>
      </div>
    </div>
  );
};

export default DemoMode; 