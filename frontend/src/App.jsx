import { Routes, Route, Navigate } from "react-router-dom";
import IssueTrackerPage from "./pages/IssueTrackerPage";
import RegisterForm from "./components/RegisterForm";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<IssueTrackerPage />} />
      <Route path="/register" element={<RegisterForm />} />
      <Route path="/projects/:projectId" element={<IssueTrackerPage />} />
      <Route
        path="/projects/:projectId/issues/:issueId"
        element={<IssueTrackerPage />}
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;