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

export default function App() {
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
          {/* <Route path="/demo" element={<DemoMode />} /> */}
        </Routes>
      </div>
    </Router>
  );
}