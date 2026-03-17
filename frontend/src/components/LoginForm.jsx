import { useState } from "react";
import api from "../api/client";

function LoginForm({ onLoginSuccess, onShowRegister }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      onLoginSuccess(response.data.access_token);
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        setError("Invalid username or password.");
      } else if (err.response?.status === 422) {
        setError("Login request format is invalid.");
      } else {
        setError("Could not connect to backend.");
      }
    }
  }

  return (
    <div
      style={{
        maxWidth: "420px",
        margin: "60px auto",
        padding: "24px",
        background: "white",
        borderRadius: "16px",
        boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
        border: "1px solid #e2e8f0",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          marginTop: 0,
          marginBottom: "8px",
          color: "#0f172a",
        }}
      >
        Issue Tracker V-2.0
      </h1>

      <p
        style={{
          textAlign: "center",
          marginTop: 0,
          marginBottom: "28px",
          color: "#64748b",
        }}
      >
        Sign in to manage projects and issues
      </p>

      <h2 style={{ marginBottom: "20px", color: "#0f172a" }}>Login</h2>

      <form onSubmit={handleSubmit}>
        <label
          htmlFor="username"
          style={{
            display: "block",
            marginBottom: "8px",
            fontWeight: "600",
            color: "#0f172a",
          }}
        >
          Username
        </label>

        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={{
            width: "100%",
            boxSizing: "border-box",
            padding: "12px 14px",
            marginBottom: "16px",
            border: "1px solid #cbd5e1",
            borderRadius: "10px",
            fontSize: "16px",
          }}
        />

        <label
          htmlFor="password"
          style={{
            display: "block",
            marginBottom: "8px",
            fontWeight: "600",
            color: "#0f172a",
          }}
        >
          Password
        </label>

        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{
            width: "100%",
            boxSizing: "border-box",
            padding: "12px 14px",
            marginBottom: "16px",
            border: "1px solid #cbd5e1",
            borderRadius: "10px",
            fontSize: "16px",
          }}
        />

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "12px",
            background: "#0f172a",
            color: "white",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            fontWeight: "600",
            cursor: "pointer",
            marginBottom: "16px",
          }}
        >
          Login
        </button>
      </form>

      <p style={{ margin: 0, color: "#475569" }}>
        Don't have an account?{" "}
        <button
          type="button"
          onClick={onShowRegister}
          style={{
            background: "none",
            border: "none",
            color: "#2563eb",
            cursor: "pointer",
            padding: 0,
            fontSize: "inherit",
          }}
        >
          Create one
        </button>
      </p>

      {error ? (
        <p style={{ color: "crimson", marginTop: "16px", marginBottom: 0 }}>
          {error}
        </p>
      ) : null}
    </div>
  );
}

export default LoginForm;