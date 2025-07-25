// scenes/logout/Logout.jsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Logout = ({ setIsLoggedIn }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // Clear user info from localStorage
    localStorage.removeItem("userId");
    localStorage.removeItem("userName");
    localStorage.removeItem("userEmail");

    // Optionally, if your backend has a logout API, call it here to clear cookies

    // Reset login state
    setIsLoggedIn(false);

    // Redirect to login page
    navigate("/login", { replace: true });
  }, [navigate, setIsLoggedIn]);

  return <div>Logging out...</div>; // or a spinner/loading indicator
};

export default Logout;
