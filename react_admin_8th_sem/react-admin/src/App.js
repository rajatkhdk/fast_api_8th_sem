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
    const userId = localStorage.getItem("userId");
    setIsLoggedIn(!!userId); // ensures state reflects login status on refresh
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
              {/* Public Route */}
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

              {/* Logout Route */}
              <Route
                path="/logout"
                element={<Logout setIsLoggedIn={setIsLoggedIn} />}
              />

              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  isLoggedIn ? <Dashboard /> : <Navigate to="/login" replace />
                }
              />
              <Route
                path="/team"
                element={
                  isLoggedIn ? <Team /> : <Navigate to="/login" replace />
                }
              />
              <Route
                path="/update/:id"
                element={
                  isLoggedIn ? (
                    <UpdateUserPage />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
            </Routes>
          </main>
        </div>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;
