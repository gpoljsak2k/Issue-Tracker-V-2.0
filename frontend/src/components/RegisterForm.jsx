import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createUser } from "../services/userService";

function RegisterForm() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      await createUser({
        email: email.trim(),
        username: username.trim(),
        password,
      });

      setSuccess("Account created successfully. You can now log in.");

      setEmail("");
      setUsername("");
      setPassword("");

      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not create account.";

      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: "420px",
        margin: "80px auto",
        background: "white",
        padding: "24px",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
      }}
    >
      <h2 style={{ marginBottom: "16px" }}>Create Account</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={submitting}
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
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={submitting}
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
            disabled={submitting}
            style={{
              width: "100%",
              padding: "10px 12px",
              boxSizing: "border-box",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
            }}
          />
          <p style={{ fontSize: "12px", color: "#64748b", marginTop: "6px" }}>
            Must include uppercase, lowercase, number, and special character.
          </p>
        </div>

        <button
          type="submit"
          disabled={submitting}
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
          {submitting ? "Creating account..." : "Create Account"}
        </button>
      </form>

      {error && (
        <p style={{ color: "crimson", marginTop: "12px" }}>{error}</p>
      )}

      {success && (
        <p style={{ color: "green", marginTop: "12px" }}>{success}</p>
      )}

      <p style={{ marginTop: "16px", fontSize: "14px", color: "#475569" }}>
        Already have an account?{" "}
        <button
          type="button"
          onClick={() => navigate("/login")}
          style={{
            border: "none",
            background: "transparent",
            color: "#2563eb",
            cursor: "pointer",
            padding: 0,
            fontSize: "14px",
          }}
        >
          Log in
        </button>
      </p>
    </div>
  );
}

export default RegisterForm;