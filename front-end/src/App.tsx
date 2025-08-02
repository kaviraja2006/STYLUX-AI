import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import DemoHome from "./pages/DemoHome";
import Message from "./pages/messages";
import Generatedpage from "./pages/generatedpage";
import Signup from "./pages/signup";
import Tryfor from "./pages/tryforfree";
import Login from "./pages/login";
import AuthPage from "./pages/Auth";
import Dashboard from "./pages/dashboard";
import Chatbot from "./pages/chatbot";
import DemoMode from "./pages/DemoMode";
import "./app.css";

// Check if Clerk is available and properly configured
const isClerkAvailable = () => {
  try {
    const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
    return PUBLISHABLE_KEY && 
           PUBLISHABLE_KEY !== "your_clerk_key_here" && 
           PUBLISHABLE_KEY.startsWith("pk_");
  } catch {
    return false;
  }
};

export default function App() {
  const clerkAvailable = isClerkAvailable();

  if (!clerkAvailable) {
    // Demo mode - no Clerk components
    return (
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-gradient-to-br from-black via-black to-purple-500">
          <header>
            <div className="p-4 text-center">
              <div className="bg-yellow-600 text-white px-6 py-2 rounded-lg">
                Demo Mode - Authentication Disabled
              </div>
            </div>
          </header>

          <Routes>
            <Route path="/" element={<DemoHome />} />
            <Route path="/chatbot" element={<Chatbot />} />
            <Route path="/messages" element={<Message />} />
            <Route path="/generated-page" element={<Generatedpage />} />
            <Route path="/sign-up" element={<Signup />} />
            <Route path="/try" element={<Tryfor />} />
            <Route path="/login" element={<Login />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </div>
      </Router>
    );
  }

  // Full mode with Clerk authentication
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gradient-to-br from-black via-black to-purple-500">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="/messages" element={<Message />} />
          <Route path="/generated-page" element={<Generatedpage />} />
          <Route path="/sign-up" element={<Signup />} />
          <Route path="/try" element={<Tryfor />} />
          <Route path="/login" element={<Login />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}