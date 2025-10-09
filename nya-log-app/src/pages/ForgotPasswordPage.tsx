// nya-log-app/src/pages/ForgotPasswordPage.tsx
import { useState } from "react";
import { supabase } from "../lib/supabaseClient";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleReset(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: "http://localhost:5173/reset-password",
    });
    if (error) setError(error.message);
    else setMessage("Password reset email sent. Check your inbox.");
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="bg-white shadow-lg p-8 rounded-lg w-96">
        <h1 className="text-2xl font-semibold mb-6 text-center">Forgot Password</h1>
        <form onSubmit={handleReset} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              className="border w-full p-2 rounded"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          {message && <p className="text-green-600 text-sm">{message}</p>}
          <button className="bg-blue-600 text-white w-full py-2 rounded hover:bg-blue-700">
            Send Reset Link
          </button>
        </form>

        <div className="text-sm mt-4 text-center">
          <a href="/login" className="text-blue-600 hover:underline">Back to login</a>
        </div>
      </div>
    </div>
  );
}
