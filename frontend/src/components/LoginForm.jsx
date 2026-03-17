import api from "../api/client";
import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function LoginForm({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    async function handleSubmit(e) {
      e.preventDefault();
      setError("");

      try {
        const response = await api.post("/auth/login", {
          username,
          password,
        });

        const token = response.data.access_token;
        // ostala logika
      } catch (error) {
        setError("Could not connect to backend.");
      }
    }

      onLoginSuccess(response.data.access_token);
    } catch (err) {
      console.error(err);

      if (err.response) {
        setError(err.response.data?.detail || "Login failed.");
      } else {
        setError("Could not connect to backend.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: "400px",
        margin: "80px auto",
        background: "white",
        padding: "24px",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
      }}
    >
        <div style={{ textAlign: "center", marginBottom: "24px" }}>
          <h1
            style={{
              margin: 0,
              fontSize: "28px",
              fontWeight: "700",
              color: "#0f172a",
            }}
          >
            Issue Tracker V-2.0
          </h1>
          <p
            style={{
              marginTop: "8px",
              marginBottom: 0,
              color: "#64748b",
              fontSize: "14px",
            }}
          >
            Sign in to manage projects and issues
          </p>
        </div>

        <h2 style={{ marginBottom: "16px", fontSize: "20px" }}>Login</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px 12px",
              boxSizing: "border-box",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
            }}
          />
        </div>

        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px 12px",
              boxSizing: "border-box",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "10px 12px",
            borderRadius: "8px",
            border: "none",
            background: "#0f172a",
            color: "white",
            cursor: "pointer",
          }}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

        <p style={{ marginTop: "16px", fontSize: "14px", color: "#475569" }}>
          Don&apos;t have an account?{" "}
          <button
            type="button"
            onClick={() => navigate("/register")}
            style={{
              border: "none",
              background: "transparent",
              color: "#2563eb",
              cursor: "pointer",
              padding: 0,
              fontSize: "14px",
            }}
          >
            Create one
          </button>
        </p>

      {error && (
        <p style={{ color: "crimson", marginTop: "12px" }}>{error}</p>
      )}
    </div>
  );
}

export default LoginForm;