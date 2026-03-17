import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import LoginForm from "../components/LoginForm";
import CreateIssueForm from "../components/CreateIssueForm";
import ProjectsSidebar from "../components/ProjectsSidebar";
import IssuesToolbar from "../components/IssuesToolbar";
import IssuesList from "../components/IssuesList";
import IssuesPagination from "../components/IssuesPagination";
import IssueDetailsPanel from "../components/IssueDetailsPanel";
import ProjectActivityPanel from "../components/ProjectActivityPanel";
import Toast from "../components/Toast";

import {
  getToken,
  removeToken,
  saveToken,
  fetchCurrentUser,
} from "../services/auth";
import {
  fetchProjects,
  createProject,
  deleteProject,
} from "../services/projectService";
import {
  fetchIssues,
  createIssue,
  updateIssue,
  deleteIssue,
} from "../services/issueService";
import {
  fetchComments,
  createComment,
  updateComment,
  deleteComment,
} from "../services/commentService";
import {
  fetchProjectMembers,
  addProjectMember,
  updateProjectMemberRole,
  removeProjectMember,
} from "../services/memberService";
import { fetchProjectActivity } from "../services/activityService";
import {
  fetchProjectLabels,
  createLabel,
  deleteLabel,
  fetchIssueLabels,
  attachLabel,
  removeLabel,
} from "../services/labelService";

import {
  getStatusLabel,
  getStatusColor,
  getPriorityColor,
  normalizeProjectMember,
} from "../utils/issueUi";

function IssueTrackerPage() {
  const navigate = useNavigate();
  const params = useParams();

  const [token, setToken] = useState(getToken());
  const [currentUser, setCurrentUser] = useState(null);

  const [projects, setProjects] = useState([]);
  const [issues, setIssues] = useState([]);
  const [members, setMembers] = useState([]);
  const [comments, setComments] = useState([]);
  const [activity, setActivity] = useState([]);
  const [projectLabels, setProjectLabels] = useState([]);
  const [issueLabels, setIssueLabels] = useState([]);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [assignedToMeOnly, setAssignedToMeOnly] = useState(false);

  const [projectsLoading, setProjectsLoading] = useState(false);
  const [issuesLoading, setIssuesLoading] = useState(false);
  const [membersLoading, setMembersLoading] = useState(false);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [activityLoading, setActivityLoading] = useState(false);
  const [labelsLoading, setLabelsLoading] = useState(false);

  const [issueUpdateLoading, setIssueUpdateLoading] = useState(false);
  const [issueDeleteLoading, setIssueDeleteLoading] = useState(false);
  const [commentSubmitting, setCommentSubmitting] = useState(false);
  const [commentActionLoading, setCommentActionLoading] = useState(false);

  const [issuesTotal, setIssuesTotal] = useState(0);
  const [issuesLimit, setIssuesLimit] = useState(3);
  const [issuesOffset, setIssuesOffset] = useState(0);

  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCreateProjectForm, setShowCreateProjectForm] = useState(false);

  const [isEditingIssue, setIsEditingIssue] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");

  const [toast, setToast] = useState(null);

  const selectedProjectId = params.projectId ? Number(params.projectId) : null;
  const selectedIssueId = params.issueId ? Number(params.issueId) : null;

  const selectedProject =
    projects.find((project) => project.id === selectedProjectId) || null;

  const isSelectedProjectOwner =
    selectedProject && currentUser
      ? selectedProject.owner_id === currentUser.id
      : false;

  const currentUserMembership =
    members.find((member) => member.userId === currentUser?.id) || null;

  const canManageMembers =
    currentUserMembership?.role === "owner" ||
    currentUserMembership?.role === "admin";

  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      const matchesSearch =
        issue.title.toLowerCase().includes(search.toLowerCase()) ||
        (issue.description || "").toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "all" || issue.status === statusFilter;

      const matchesPriority =
        priorityFilter === "all" || issue.priority === priorityFilter;

      const matchesAssignedToMe =
        !assignedToMeOnly || issue.assignee_id === currentUser?.id;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesPriority &&
        matchesAssignedToMe
      );
    });
  }, [
    issues,
    search,
    statusFilter,
    priorityFilter,
    assignedToMeOnly,
    currentUser,
  ]);

  const activeIssue =
    filteredIssues.find((issue) => issue.id === selectedIssueId) ||
    filteredIssues[0] ||
    null;

  function showToast(type, message) {
    setToast({ type, message });
  }

  function closeToast() {
    setToast(null);
  }

  function handleLoginSuccess(newToken) {
    saveToken(newToken);
    setToken(newToken);
  }

  function handleLogout() {
    removeToken();
    setToken("");
    setCurrentUser(null);
    setProjects([]);
    setIssues([]);
    setMembers([]);
    setComments([]);
    setActivity([]);
    setProjectLabels([]);
    setIssueLabels([]);
    setSearch("");
    setStatusFilter("all");
    setPriorityFilter("all");
    setAssignedToMeOnly(false);
    setIssuesTotal(0);
    setIssuesLimit(3);
    setIssuesOffset(0);
    setError("");
    setShowCreateForm(false);
    setShowCreateProjectForm(false);
    setIsEditingIssue(false);
    setEditTitle("");
    setEditDescription("");
    navigate("/login", { replace: true });
  }

  function replaceIssueInState(updatedIssue) {
    setIssues((currentIssues) =>
      currentIssues.map((issue) =>
        issue.id === updatedIssue.id ? updatedIssue : issue
      )
    );
  }

  function handlePreviousPage() {
    const newOffset = Math.max(0, issuesOffset - issuesLimit);
    setIssuesOffset(newOffset);
  }

  function handleNextPage() {
    const newOffset = issuesOffset + issuesLimit;
    if (newOffset >= issuesTotal) return;
    setIssuesOffset(newOffset);
  }

  async function loadCurrentUser() {
    try {
      const user = await fetchCurrentUser();
      setCurrentUser(user);
    } catch (err) {
      console.error(err);
      setCurrentUser(null);
    }
  }

  async function loadProjects() {
    try {
      setProjectsLoading(true);
      setError("");

      const data = await fetchProjects();
      setProjects(data);

      if (data.length > 0) {
        const hasValidSelectedProject = data.some(
          (project) => project.id === selectedProjectId
        );

        if (!hasValidSelectedProject) {
          navigate(`/projects/${data[0].id}`, { replace: true });
        }
      } else {
        setIssues([]);
      }
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Could not load projects.";
      setError(message);
    } finally {
      setProjectsLoading(false);
    }
  }

  async function loadIssues(
    projectId,
    customOffset = issuesOffset,
    customLimit = issuesLimit
  ) {
    try {
      setIssuesLoading(true);
      setError("");

      const data = await fetchIssues(projectId, {
        limit: customLimit,
        offset: customOffset,
      });

      const fetchedIssues = data.items || [];

      setIssues(fetchedIssues);
      setIssuesTotal(data.total || 0);
      setIssuesLimit(data.limit || customLimit);
      setIssuesOffset(data.offset || customOffset);

      if (fetchedIssues.length > 0) {
        const hasValidSelectedIssue = fetchedIssues.some(
          (issue) => issue.id === selectedIssueId
        );

        if (!hasValidSelectedIssue) {
          navigate(`/projects/${projectId}/issues/${fetchedIssues[0].id}`, {
            replace: true,
          });
        }
      } else {
        navigate(`/projects/${projectId}`, { replace: true });
      }
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Could not load issues.";
      setError(message);
    } finally {
      setIssuesLoading(false);
    }
  }

  async function loadMembers(projectId) {
    try {
      setMembersLoading(true);

      const data = await fetchProjectMembers(projectId);
      const normalizedMembers = (data || []).map(normalizeProjectMember);

      setMembers(normalizedMembers);
    } catch (err) {
      console.error(err);
      setMembers([]);
    } finally {
      setMembersLoading(false);
    }
  }

  async function loadComments(projectId, issueId) {
    try {
      setCommentsLoading(true);

      const data = await fetchComments(projectId, issueId);
      setComments(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      console.error(err);
      setComments([]);
    } finally {
      setCommentsLoading(false);
    }
  }

  async function loadActivity(projectId) {
    try {
      setActivityLoading(true);

      const data = await fetchProjectActivity(projectId);
      setActivity(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setActivity([]);
    } finally {
      setActivityLoading(false);
    }
  }

  async function loadProjectLabels(projectId) {
    try {
      const data = await fetchProjectLabels(projectId);
      setProjectLabels(data || []);
    } catch (err) {
      console.error(err);
      setProjectLabels([]);
    }
  }

  async function loadIssueLabels(projectId, issueId) {
    try {
      setLabelsLoading(true);

      const data = await fetchIssueLabels(projectId, issueId);
      setIssueLabels(data || []);
    } catch (err) {
      console.error(err);
      setIssueLabels([]);
    } finally {
      setLabelsLoading(false);
    }
  }

  async function handleCreateProject(projectData) {
    try {
      const createdProject = await createProject(projectData);

      await loadProjects();

      setShowCreateProjectForm(false);
      navigate(`/projects/${createdProject.id}`);
      showToast("success", "Project created successfully.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not create project.";

      showToast("error", message);
      throw err;
    }
  }

  async function handleDeleteProject() {
    if (!selectedProjectId || !selectedProject) return;

    if (!isSelectedProjectOwner) {
      showToast("error", "Only the project owner can delete the project.");
      return;
    }

    const confirmed = window.confirm(
      `Delete project "${selectedProject.name}"? This will permanently remove the project and its related data.`
    );

    if (!confirmed) return;

    try {
      await deleteProject(selectedProjectId);

      showToast("success", "Project deleted.");

      const updatedProjects = projects.filter(
        (project) => project.id !== selectedProjectId
      );

      setProjects(updatedProjects);
      setIssues([]);
      setMembers([]);
      setComments([]);
      setActivity([]);
      setProjectLabels([]);
      setIssueLabels([]);
      setShowCreateForm(false);
      setIsEditingIssue(false);
      setEditTitle("");
      setEditDescription("");

      if (updatedProjects.length > 0) {
        navigate(`/projects/${updatedProjects[0].id}`);
      } else {
        navigate("/login");
      }
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not delete project.";

      showToast("error", message);
    }
  }

  async function handleCreateIssue(issueData) {
    if (!selectedProjectId) return;

    try {
      const createdIssue = await createIssue(selectedProjectId, issueData);
      const data = await fetchIssues(selectedProjectId, {
        limit: issuesLimit,
        offset: issuesOffset,
      });
      const fetchedIssues = data.items || [];

      setIssues(fetchedIssues);
      setIssuesTotal(data.total || 0);
      setIssuesLimit(data.limit || issuesLimit);
      setIssuesOffset(data.offset || issuesOffset);

      if (fetchedIssues.length > 0) {
        const newSelected =
          fetchedIssues.find((issue) => issue.id === createdIssue?.id) ||
          fetchedIssues[0];

        navigate(`/projects/${selectedProjectId}/issues/${newSelected.id}`);
      } else {
        navigate(`/projects/${selectedProjectId}`);
      }

      setShowCreateForm(false);
      await loadActivity(selectedProjectId);
      showToast("success", "Issue created successfully.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not create issue.";

      setError(message);
      showToast("error", message);
    }
  }

  async function handleIssueFieldUpdate(field, value) {
    if (!selectedProjectId || !activeIssue) return;

    try {
      setIssueUpdateLoading(true);
      setError("");

      const updatedIssue = await updateIssue(selectedProjectId, activeIssue.id, {
        [field]: value,
      });

      replaceIssueInState(updatedIssue);
      await loadActivity(selectedProjectId);
      showToast("success", "Issue updated.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not update issue.";

      setError(message);
      showToast("error", message);
    } finally {
      setIssueUpdateLoading(false);
    }
  }

  async function handleAssigneeChange(value) {
    if (!selectedProjectId || !activeIssue) return;

    const assigneeId = value === "" ? null : Number(value);

    try {
      setIssueUpdateLoading(true);
      setError("");

      const updatedIssue = await updateIssue(selectedProjectId, activeIssue.id, {
        assignee_id: assigneeId,
      });

      replaceIssueInState(updatedIssue);
      await loadActivity(selectedProjectId);
      showToast("success", "Assignee updated.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not update assignee.";

      setError(message);
      showToast("error", message);
    } finally {
      setIssueUpdateLoading(false);
    }
  }

  function startEditingIssue() {
    if (!activeIssue) return;

    setEditTitle(activeIssue.title);
    setEditDescription(activeIssue.description || "");
    setIsEditingIssue(true);
  }

  function cancelEditingIssue() {
    setIsEditingIssue(false);
    setEditTitle("");
    setEditDescription("");
  }

  async function saveIssueEdits() {
    if (!selectedProjectId || !activeIssue) return;

    try {
      setIssueUpdateLoading(true);
      setError("");

      const updatedIssue = await updateIssue(selectedProjectId, activeIssue.id, {
        title: editTitle,
        description: editDescription,
      });

      replaceIssueInState(updatedIssue);
      setIsEditingIssue(false);
      await loadActivity(selectedProjectId);
      showToast("success", "Issue details updated.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not update issue.";

      setError(message);
      showToast("error", message);
    } finally {
      setIssueUpdateLoading(false);
    }
  }

  async function handleDeleteIssue() {
    if (!selectedProjectId || !activeIssue) return;

    const confirmed = window.confirm(
      `Delete issue "${activeIssue.title}"? This cannot be undone.`
    );

    if (!confirmed) return;

    try {
      setIssueDeleteLoading(true);
      setError("");

      const deletedIssueId = activeIssue.id;

      await deleteIssue(selectedProjectId, deletedIssueId);
      setComments([]);
      setIssueLabels([]);
      await loadActivity(selectedProjectId);
      showToast("success", "Issue deleted.");

      setIssues((currentIssues) => {
        const updatedIssues = currentIssues.filter(
          (issue) => issue.id !== deletedIssueId
        );

        if (updatedIssues.length > 0) {
          navigate(
            `/projects/${selectedProjectId}/issues/${updatedIssues[0].id}`
          );
        } else {
          navigate(`/projects/${selectedProjectId}`);
        }

        return updatedIssues;
      });

      setIsEditingIssue(false);
      setEditTitle("");
      setEditDescription("");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not delete issue.";

      setError(message);
      showToast("error", message);
    } finally {
      setIssueDeleteLoading(false);
    }
  }

  async function handleCreateComment(content) {
    if (!selectedProjectId || !activeIssue) return;

    try {
      setCommentSubmitting(true);

      await createComment(selectedProjectId, activeIssue.id, content);
      await loadComments(selectedProjectId, activeIssue.id);
      await loadActivity(selectedProjectId);
      showToast("success", "Comment added.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not add comment.";

      showToast("error", message);
      throw err;
    } finally {
      setCommentSubmitting(false);
    }
  }

  async function handleUpdateComment(commentId, body) {
    if (!selectedProjectId || !activeIssue) return;

    try {
      setCommentActionLoading(true);

      await updateComment(selectedProjectId, activeIssue.id, commentId, body);
      await loadComments(selectedProjectId, activeIssue.id);
      await loadActivity(selectedProjectId);
      showToast("success", "Comment updated.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not update comment.";

      showToast("error", message);
      throw err;
    } finally {
      setCommentActionLoading(false);
    }
  }

  async function handleDeleteComment(commentId) {
    if (!selectedProjectId || !activeIssue) return;

    const confirmed = window.confirm("Delete this comment?");

    if (!confirmed) return;

    try {
      setCommentActionLoading(true);

      await deleteComment(selectedProjectId, activeIssue.id, commentId);
      await loadComments(selectedProjectId, activeIssue.id);
      await loadActivity(selectedProjectId);
      showToast("success", "Comment deleted.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not delete comment.";

      showToast("error", message);
      throw err;
    } finally {
      setCommentActionLoading(false);
    }
  }

  async function handleAddMember(memberData) {
    if (!selectedProjectId) return;

    try {
      await addProjectMember(selectedProjectId, memberData);
      await loadMembers(selectedProjectId);
      await loadActivity(selectedProjectId);
      showToast("success", "Project member added.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not add project member.";

      showToast("error", message);
      throw err;
    }
  }

  async function handleUpdateMemberRole(userId, role) {
    if (!selectedProjectId) return;

    try {
      await updateProjectMemberRole(selectedProjectId, userId, role);
      await loadMembers(selectedProjectId);
      await loadActivity(selectedProjectId);
      showToast("success", "Member role updated.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not update member role.";

      showToast("error", message);
    }
  }

  async function handleRemoveMember(userId) {
    if (!selectedProjectId) return;

    const confirmed = window.confirm("Remove this member from the project?");

    if (!confirmed) return;

    try {
      await removeProjectMember(selectedProjectId, userId);
      await loadMembers(selectedProjectId);
      await loadActivity(selectedProjectId);
      showToast("success", "Member removed.");
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not remove member.";

      showToast("error", message);
    }
  }

  async function handleCreateLabel(labelData) {
    if (!selectedProjectId) return;

    try {
      await createLabel(selectedProjectId, labelData);
      await loadProjectLabels(selectedProjectId);
      await loadActivity(selectedProjectId);
      showToast("success", "Label created.");
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Could not create label.";
      showToast("error", message);
      throw err;
    }
  }

  async function handleDeleteLabel(labelId) {
    if (!selectedProjectId) return;

    const confirmed = window.confirm("Delete this label?");

    if (!confirmed) return;

    try {
      await deleteLabel(selectedProjectId, labelId);
      await loadProjectLabels(selectedProjectId);

      if (activeIssue) {
        await loadIssueLabels(selectedProjectId, activeIssue.id);
      }

      await loadActivity(selectedProjectId);
      showToast("success", "Label deleted.");
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Could not delete label.";
      showToast("error", message);
    }
  }

  async function handleAddLabel(labelId) {
    if (!selectedProjectId || !activeIssue) return;

    try {
      await attachLabel(selectedProjectId, activeIssue.id, labelId);
      await loadIssueLabels(selectedProjectId, activeIssue.id);
      await loadActivity(selectedProjectId);
      showToast("success", "Label added to issue.");
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Could not add label.";
      showToast("error", message);
    }
  }

  async function handleRemoveLabel(labelId) {
    if (!selectedProjectId || !activeIssue) return;

    try {
      await removeLabel(selectedProjectId, activeIssue.id, labelId);
      await loadIssueLabels(selectedProjectId, activeIssue.id);
      await loadActivity(selectedProjectId);
      showToast("success", "Label removed from issue.");
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Could not remove label.";
      showToast("error", message);
    }
  }

  useEffect(() => {
    if (!toast) return;

    const timeout = setTimeout(() => {
      setToast(null);
    }, 3000);

    return () => clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    if (!token) {
      setCurrentUser(null);
      return;
    }

    loadCurrentUser();
  }, [token]);

  useEffect(() => {
    if (!token) return;
    loadProjects();
  }, [token, selectedProjectId]);

  useEffect(() => {
    if (!token || !selectedProjectId) return;
    loadIssues(selectedProjectId, issuesOffset, issuesLimit);
  }, [token, selectedProjectId, issuesOffset, issuesLimit]);

  useEffect(() => {
    if (!token || !selectedProjectId) {
      setMembers([]);
      return;
    }

    loadMembers(selectedProjectId);
  }, [token, selectedProjectId]);

  useEffect(() => {
    if (!token || !selectedProjectId || !selectedIssueId) {
      setComments([]);
      return;
    }

    loadComments(selectedProjectId, selectedIssueId);
  }, [token, selectedProjectId, selectedIssueId]);

  useEffect(() => {
    if (!token || !selectedProjectId) {
      setActivity([]);
      return;
    }

    loadActivity(selectedProjectId);
  }, [token, selectedProjectId]);

  useEffect(() => {
    if (!selectedProjectId) return;
    loadProjectLabels(selectedProjectId);
  }, [selectedProjectId]);

  useEffect(() => {
    if (!selectedProjectId || !selectedIssueId) {
      setIssueLabels([]);
      return;
    }

    loadIssueLabels(selectedProjectId, selectedIssueId);
  }, [selectedProjectId, selectedIssueId]);

  useEffect(() => {
    setIsEditingIssue(false);
    setEditTitle("");
    setEditDescription("");
  }, [selectedIssueId]);

  useEffect(() => {
    setIsEditingIssue(false);
    setEditTitle("");
    setEditDescription("");
    setComments([]);
    setIssueLabels([]);
    setAssignedToMeOnly(false);
    setIssuesOffset(0);
  }, [selectedProjectId]);

  if (!token) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div
      style={{
        fontFamily: "Arial, sans-serif",
        minHeight: "100vh",
        background: "#f8fafc",
      }}
    >
      <Toast toast={toast} onClose={closeToast} />

      <header
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid #e2e8f0",
          background: "white",
          fontWeight: "bold",
          fontSize: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>Issue Tracker</span>
        <button
          onClick={handleLogout}
          style={{
            padding: "8px 12px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            background: "white",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </header>

      <div style={{ display: "flex", Height: "calc(100vh - 57px)", overflow: "hidden", }}>
        <ProjectsSidebar
          projects={projects}
          projectsLoading={projectsLoading}
          selectedProjectId={selectedProjectId}
          onSelectProject={(projectId) => navigate(`/projects/${projectId}`)}
          showCreateProjectForm={showCreateProjectForm}
          onToggleCreateProjectForm={() =>
            setShowCreateProjectForm((prev) => !prev)
          }
          onCreateProject={handleCreateProject}
          selectedProject={selectedProject}
          canDeleteSelectedProject={isSelectedProjectOwner}
          onDeleteProject={handleDeleteProject}
          members={members}
          membersLoading={membersLoading}
          canManageMembers={canManageMembers}
          currentUser={currentUser}
          onAddMember={handleAddMember}
          onUpdateMemberRole={handleUpdateMemberRole}
          onRemoveMember={handleRemoveMember}
          projectLabels={projectLabels}
          onCreateLabel={handleCreateLabel}
          onDeleteLabel={handleDeleteLabel}
        />

        <main style={{ flex: 1, padding: "24px" }}>
          <IssuesToolbar
            showCreateForm={showCreateForm}
            selectedProjectId={selectedProjectId}
            issuesLoading={issuesLoading}
            onToggleCreateForm={() => setShowCreateForm((prev) => !prev)}
            onRefresh={() =>
              selectedProjectId &&
              loadIssues(selectedProjectId, issuesOffset, issuesLimit)
            }
            search={search}
            statusFilter={statusFilter}
            priorityFilter={priorityFilter}
            assignedToMeOnly={assignedToMeOnly}
            onSearchChange={setSearch}
            onStatusFilterChange={setStatusFilter}
            onPriorityFilterChange={setPriorityFilter}
            onAssignedToMeChange={setAssignedToMeOnly}
          />

          {showCreateForm && (
            <CreateIssueForm
              onCreate={handleCreateIssue}
              disabled={!selectedProjectId}
            />
          )}

          <IssuesList
            issuesLoading={issuesLoading}
            error={error}
            filteredIssues={filteredIssues}
            onSelectIssue={(issue) =>
              navigate(`/projects/${selectedProjectId}/issues/${issue.id}`)
            }
            getStatusColor={getStatusColor}
            getStatusLabel={getStatusLabel}
            getPriorityColor={getPriorityColor}
          />

          <IssuesPagination
            total={issuesTotal}
            limit={issuesLimit}
            offset={issuesOffset}
            onPrevious={handlePreviousPage}
            onNext={handleNextPage}
          />

          <ProjectActivityPanel
            activity={activity}
            loading={activityLoading}
          />
        </main>

        <IssueDetailsPanel
          activeIssue={activeIssue}
          isEditingIssue={isEditingIssue}
          editTitle={editTitle}
          editDescription={editDescription}
          setEditTitle={setEditTitle}
          setEditDescription={setEditDescription}
          startEditingIssue={startEditingIssue}
          cancelEditingIssue={cancelEditingIssue}
          saveIssueEdits={saveIssueEdits}
          handleDeleteIssue={handleDeleteIssue}
          handleIssueFieldUpdate={handleIssueFieldUpdate}
          handleAssigneeChange={handleAssigneeChange}
          issueUpdateLoading={issueUpdateLoading}
          issueDeleteLoading={issueDeleteLoading}
          members={members}
          membersLoading={membersLoading}
          comments={comments}
          commentsLoading={commentsLoading}
          commentSubmitting={commentSubmitting}
          commentActionLoading={commentActionLoading}
          handleCreateComment={handleCreateComment}
          handleUpdateComment={handleUpdateComment}
          handleDeleteComment={handleDeleteComment}
          issueLabels={issueLabels}
          projectLabels={projectLabels}
          labelsLoading={labelsLoading}
          handleAddLabel={handleAddLabel}
          handleRemoveLabel={handleRemoveLabel}
        />
      </div>
    </div>
  );
}

export default IssueTrackerPage;