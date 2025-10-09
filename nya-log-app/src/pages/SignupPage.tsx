// nya-log-app/src/pages/SignupPage.tsx
import { useState } from "react";
import { supabase } from "../lib/supabaseClient";

export default function SignupPage() {
  const [form, setForm] = useState({
    initials: "",
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Check for duplicate initials
    const { data: existing } = await supabase
      .from("employees")
      .select("id")
      .eq("initials", form.initials);

    if (existing && existing.length > 0) {
      setError("These initials are already used. Please choose another.");
      return;
    }

    // Create user in Supabase Auth
    const { data, error: signupError } = await supabase.auth.signUp({
      email: form.email,
      password: form.password,
    });

    if (signupError) {
      setError(signupError.message);
      return;
    }

    // Insert employee record
    const { error: insertError } = await supabase.from("employees").insert({
      initials: form.initials,
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
    });

    if (insertError) {
      setError(insertError.message);
    } else {
      setSuccess("Account created successfully! Please check your email for confirmation.");
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="bg-white shadow-lg p-8 rounded-lg w-96">
        <h1 className="text-2xl font-semibold mb-6 text-center">Create Account</h1>
        <form onSubmit={handleSignup} className="space-y-3">
          {["initials", "first_name", "last_name", "email", "password"].map((key) => (
            <div key={key}>
              <label className="block text-sm font-medium mb-1 capitalize">{key.replace("_", " ")}</label>
              <input
                type={key === "password" ? "password" : "text"}
                required={key !== "last_name"}
                value={(form as any)[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                className="border w-full p-2 rounded"
              />
            </div>
          ))}
          {error && <p className="text-red-600 text-sm">{error}</p>}
          {success && <p className="text-green-600 text-sm">{success}</p>}
          <button className="bg-green-600 text-white w-full py-2 rounded hover:bg-green-700">
            Sign Up
          </button>
        </form>

        <div className="text-sm mt-4 text-center">
          <a href="/login" className="text-blue-600 hover:underline">Back to login</a>
        </div>
      </div>
    </div>
  );
}
