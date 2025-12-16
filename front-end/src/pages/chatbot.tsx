import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import './chatbot.css'

// Define types for messages
interface Message {
  sender: "user" | "bot";
  text: string;
  timestamp: string;
}

interface ChatRequest {
  message: string;
  conversation_history: Array<{
    sender: string;
    text: string;
    timestamp: string;
  }>;
}

interface ChatResponse {
  response: string;
  suggested_options?: string[];
}

const Chatbot: React.FC = () => {
  const [userInput, setUserInput] = useState<string>("");
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scroll to the bottom on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleSendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    const newMessage: Message = {
      sender: "user",
      text: userInput,
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatHistory((prevHistory) => [...prevHistory, newMessage]);
    setUserInput("");
    setIsLoading(true);

    try {
      // Convert chat history to the format expected by the backend
      const conversationHistory = chatHistory.map(msg => ({
        sender: msg.sender,
        text: msg.text,
        timestamp: msg.timestamp
      }));

      const requestData: ChatRequest = {
        message: userInput,
        conversation_history: conversationHistory
      };

      const response = await axios.post<ChatResponse>(
        `${import.meta.env.VITE_API_URL || "https://stylux-ai-15.onrender.com"}/chat`,
        requestData,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 30000 // 30 second timeout
        }
      );

      const botMessage: Message = {
        sender: "bot",
        text: response.data.response,
        timestamp: new Date().toLocaleTimeString(),
      };

      setChatHistory((prevHistory) => [...prevHistory, botMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
      const errorMessage: Message = {
        sender: "bot",
        text: "Sorry, I'm having trouble connecting to the fashion assistant. Please try again later.",
        timestamp: new Date().toLocaleTimeString(),
      };
      setChatHistory((prevHistory) => [...prevHistory, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat">
      {/* Chat Container */}
      <div className="ch">
        <div className="flex-1 p-6 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">STYLUX AI Assistant</h2>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto bg-transparent rounded-lg p-4 max-h-96">
            {chatHistory.length === 0 && (
              <div className="text-center text-gray-400 mb-4">
                <p>👋 Hi! I'm STYLUX, your AI fashion assistant.</p>
                <p className="text-sm mt-2">Tell me about your style preferences, skin tone, or what you're looking for!</p>
              </div>
            )}

            {chatHistory.map((msg, index) => (
              <div key={index} className={`mb-4 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
                <div
                  className={`inline-block p-3 rounded-lg max-w-[80%] ${msg.sender === "user"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-700 text-gray-300"
                    }`}
                >
                  {msg.text}
                </div>
                <div className={`text-xs text-gray-500 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
                  {msg.timestamp}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="text-left mb-4">
                <div className="inline-block p-3 rounded-lg bg-gray-700 text-gray-300">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-500"></div>
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef}></div>
          </div>

          {/* Input Section */}
          <div className="flex items-center space-x-4 mt-4">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message STYLUX..."
              disabled={isLoading}
              className="flex-1 p-3 rounded-lg bg-purple-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !userInput.trim()}
              className="bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
