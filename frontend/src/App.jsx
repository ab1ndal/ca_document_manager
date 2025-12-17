import React, { useEffect, useState } from "react";
import MainPage from "./pages/MainPage";
import LoginPage from "./pages/LoginPage";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [loginInProgress, setLoginInProgress] = useState(false);
  const [loginError, setLoginError] = useState("");

  const checkAuthStatus = async () => {
    setCheckingAuth(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/status`);
      if (res.ok) {
        const data = await res.json();
        console.log(data)
        setIsLoggedIn(Boolean(data.logged_in));
        console.log(`isLoggedIn: ${isLoggedIn}`)
      } else {
        setIsLoggedIn(false);
      }
    } catch (err) {
      setLoginError(err.message || "Failed to check Auth Status")
      console.log(`Error: ${err}`)
      setIsLoggedIn(false);
    } finally {
      setCheckingAuth(false);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const handleLogin = async () => {
    setLoginError("");
    try {
      console.log("Logging in....")
      setLoginInProgress(true);
      const res = await fetch(`${API_BASE}/api/login`, { method: "POST" });
      if (!res.ok) {
        throw new Error("Login failed. Please try again.");
      }

      const statusRes = await fetch(`${API_BASE}/api/auth/status`);
      if (!statusRes.ok) {
        throw new Error("Unable to confirm login status.");
      }
      const statusData = await statusRes.json();
      const logged = Boolean(statusData.logged_in);
      setIsLoggedIn(logged);
      if (!logged) {
        throw new Error("Authentication token missing or invalid.");
      }
    } catch (err) {
      console.log(`Error: ${err}`)
      setLoginError(err.message || "Unable to login right now.");
      setIsLoggedIn(false);
    } finally {
      setLoginInProgress(false);
      setCheckingAuth(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("aps_token");
    setIsLoggedIn(false);
  };

  const handleAuthFailure = () => {
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return (
      <LoginPage
        onLogin={handleLogin}
        loading={loginInProgress}
        error={loginError}
      />
    );
  }

  return (
    <MainPage
      isLoggedIn={isLoggedIn}
      onLogin={handleLogin}
      onLogout={handleLogout}
      loginInProgress={loginInProgress}
      onAuthFailure={handleAuthFailure}
    />
  );
}

export default App;
