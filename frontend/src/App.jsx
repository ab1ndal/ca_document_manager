import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  async function callPython() {
    const result = await fetch("http://localhost:8000/greet/Abhinav");
    const data = await result.json();
    setMessage(data.message);
    console.log("Received from Python:", data);
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
