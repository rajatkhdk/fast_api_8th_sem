import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = ({ setIsLoggedIn }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const response = await fetch("https://ada93a08cb4d.ngrok-free.app/api/Auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.message || "Login failed");
      }

      const message = data.message?.toLowerCase();
      if (!message.includes("admin login successful")) {
        setErrorMsg("Only admin users are allowed to log in.");
        return;
      }

      // Save to localStorage
      localStorage.setItem("userId", data.userId || data.UserId);
      localStorage.setItem("userName", data.name || data.Name);
      localStorage.setItem("userEmail", data.email || data.Email);
      localStorage.setItem("isAdmin", "true");

      // Trigger re-render in App
      setIsLoggedIn(true);

      // Navigate to dashboard
      navigate("/");
    } catch (err) {
      setErrorMsg(err.message);
      console.error("Login error:", err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100 px-4">
      <div className="w-full max-w-md">
        <form
          onSubmit={handleLogin}
          className="bg-white shadow-lg rounded-lg p-10 w-full space-y-6"
          style={{ boxShadow: "0 8px 20px rgba(0,0,0,0.1)" }}
        >
          <h2 className="text-3xl font-extrabold text-center text-blue-700 tracking-wide">
            Admin Login
          </h2>

          {errorMsg && (
            <div className="text-red-600 bg-red-100 border border-red-300 px-4 py-2 rounded-md text-sm">
              {errorMsg}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block mb-2 font-semibold text-gray-700">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@example.com"
              required
              className="w-full px-4 py-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
            />
          </div>

          <div>
            <label htmlFor="password" className="block mb-2 font-semibold text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              className="w-full px-4 py-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 rounded-md font-semibold transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
