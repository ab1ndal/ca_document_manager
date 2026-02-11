import React, { useEffect, useState } from "react";
import MainPage from "./pages/MainPage";
import LoginPage from "./pages/LoginPage";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [loginInProgress, setLoginInProgress] = useState(false);
  const [loginError, setLoginError] = useState("");

  const checkAuthStatus = async (retries = 1) => {
    setCheckingAuth(true);
    try {
      const sessionId = localStorage.getItem("session_id");
      const res = await fetch(`${API_BASE}/api/auth/status`,{
        headers: {
          "X-Session-Id": sessionId 
        } 
      });
      if (res.ok) {
        const data = await res.json();
        if (data.logged_in){
          setIsLoggedIn(true);
          return;
        }
      }
      if (retries > 0) {
      setTimeout(() => checkAuthStatus(retries - 1), 500);
      return;
    }
    setIsLoggedIn(false);
    } catch (err) {
      setLoginError(err.message || "Failed to check Auth Status")
      console.log(`Error: ${err}`)
      setIsLoggedIn(false);
    } finally {
      setCheckingAuth(false);
    }
  };

  useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const sessionId = params.get("session_id");

  if (sessionId) {
    localStorage.setItem("session_id", sessionId);
    window.history.replaceState({}, "", window.location.pathname);
  }
  }, []);


  useEffect(() => {
    checkAuthStatus();
  }, []);

  const handleLogin = async () => {
    setLoginError("");
    window.location.href = `${API_BASE}/api/login`;
  };

  const handleLogout = async () => {
    try {
      const sessionId = localStorage.getItem("session_id");
      await fetch(`${API_BASE}/api/logout`, { 
        method: "POST", 
        headers: {
          "X-Session-Id": sessionId 
        } 
      });
      localStorage.removeItem("session_id");
    } catch (_) {
      // ignore network errors on logout
    }
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
