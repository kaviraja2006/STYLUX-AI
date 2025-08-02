import React from "react";
import ReactDOM from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import App from "./App";
import "./index.css"; 

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

// Check if the key is a placeholder or missing
const isPlaceholderKey = !PUBLISHABLE_KEY || 
                        PUBLISHABLE_KEY === "your_clerk_key_here" || 
                        !PUBLISHABLE_KEY.startsWith("pk_");

if (isPlaceholderKey) {
  console.warn("⚠️ Clerk authentication is not configured. Running in demo mode.");
  console.warn("💡 To enable authentication, get your key from: https://dashboard.clerk.com/");
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {isPlaceholderKey ? (
      // Run without Clerk authentication
      <App />
    ) : (
      // Run with Clerk authentication
      <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
        <App />
      </ClerkProvider>
    )}
  </React.StrictMode>
);