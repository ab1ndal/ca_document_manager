import React, { useState } from "react";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Temporary handler, we will wire this to the backend in a later step
  const handleLoginClick = () => {
    // For now, just toggle the state to mock login
    setIsLoggedIn(true);
  };

  return (
    <div className="appRoot">
      <header className="appHeader">
        <div className="appTitleBlock">
          <h1 className="appTitle">CA Document Manager</h1>
          <p className="appSubtitle">
            UCSF RFI Viewer
          </p>
        </div>

        <div className="appHeaderRight">
          <div className="loginStatus">
            <span
              className={
                isLoggedIn ? "statusDot statusDotOnline" : "statusDot statusDotOffline"
              }
            />
            <span className="statusText">
              {isLoggedIn ? "Connected to Autodesk" : "Not connected"}
            </span>
          </div>
          <button
            className="primaryButton"
            onClick={handleLoginClick}
            disabled={isLoggedIn}
          >
            {isLoggedIn ? "Signed in" : "Sign in to Autodesk"}
          </button>
        </div>
      </header>

      <main className="appMain">
        <section className="controlsPanel">
          <h2 className="panelTitle">Filters</h2>
          <p className="panelDescription">
            In the next steps, you will add fields for search terms and
            date or time in Pacific Time here.
          </p>
          {/* TODO: search inputs, date and time pickers */}
        </section>

        <section className="resultsPanel">
          <div className="resultsHeader">
            <h2 className="panelTitle">RFIs</h2>
            <button className="secondaryButton" disabled>
              Export to Excel
            </button>
          </div>
          <div className="resultsPlaceholder">
            <p>
              RFIs will be displayed here in an AG Grid table once we connect
              the backend API.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
