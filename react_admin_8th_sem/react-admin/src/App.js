import { useState, useEffect } from "react";
import { ColorModeContext, useMode } from "./theme";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { Routes, Route, Navigate } from "react-router-dom";

import Topbar from "./scenes/global/Topbar";
import Dashboard from "./scenes/dashboard";
import Sidebar from "./scenes/global/Sidebar";
import Team from "./scenes/team";
import UpdateUserPage from "./scenes/updateUserPage";
import LoginPage from "./scenes/login/login";
import Logout from "./scenes/logout/Logout";

function App() {
  const [theme, colorMode] = useMode();
  const [isSidebar, setIsSidebar] = useState(true);

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if user info exists in localStorage to set logged in state
    const userId = localStorage.getItem("userId");
    if (userId) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div className="app">
          {isLoggedIn && <Sidebar isSidebar={isSidebar} />}
          <main className="content">
            {isLoggedIn && <Topbar />}

            <Routes>
  {/* Public route */}
  <Route
    path="/login"
    element={
      isLoggedIn ? (
        <Navigate to="/" replace />
      ) : (
        <LoginPage setIsLoggedIn={setIsLoggedIn} />
      )
    }
  />

  {/* Logout route */}
  <Route
    path="/logout"
    element={<Logout setIsLoggedIn={setIsLoggedIn} />}
  />

  {/* Protected routes */}
  <Route
    path="/"
    element={isLoggedIn ? <Dashboard /> : <Navigate to="/login" replace />}
  />
  <Route
    path="/team"
    element={isLoggedIn ? <Team /> : <Navigate to="/login" replace />}
  />
  <Route
    path="/update/:id"
    element={isLoggedIn ? <UpdateUserPage /> : <Navigate to="/login" replace />}
  />
</Routes>
          </main>
        </div>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;
