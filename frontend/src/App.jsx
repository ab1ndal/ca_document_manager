import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  async function callPython() {
    const result = await window.pywebview.api.greet("Abhinav");
    setMessage(result);
    console.log("Received from Python:", result);
  }

  return (
    <div>
      <h1>CA Manager</h1>
      <button onClick={callPython}>Call Python</button>
      <p>{message}</p>
    </div>
  );
}

export default App;
