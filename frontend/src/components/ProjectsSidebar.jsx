import CreateProjectForm from "./CreateProjectForm";
import ProjectMembersPanel from "./ProjectMembersPanel";
import ProjectLabelsPanel from "./ProjectLabelsPanel";

function ProjectsSidebar({
  projects = [],
  projectsLoading = false,
  selectedProjectId = null,
  onSelectProject,
  showCreateProjectForm = false,
  onToggleCreateProjectForm,
  onCreateProject,
  selectedProject = null,
  canDeleteSelectedProject = false,
  onDeleteProject,
  members = [],
  membersLoading = false,
  canManageMembers = false,
  currentUser = null,
  onAddMember,
  onUpdateMemberRole,
  onRemoveMember,
  projectLabels = [],
  onCreateLabel,
  onDeleteLabel,
}) {
  return (
    <aside
      style={{
        width: "320px",
        boxSizing: "border-box",
        overflowY: "auto",
        maxHeight: "calc(100vh - 57px)",
        borderRight: "1px solid #e2e8f0",
        background: "white",
        padding: "16px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "12px",
          gap: "8px",
        }}
      >
        <h2 style={{ fontSize: "16px", margin: 0 }}>Projects</h2>

        <button
          onClick={onToggleCreateProjectForm}
          style={{
            padding: "6px 10px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            background: "white",
            cursor: "pointer",
            fontSize: "13px",
          }}
        >
          {showCreateProjectForm ? "Close" : "New"}
        </button>
      </div>

      {showCreateProjectForm && (
        <CreateProjectForm
          onCreate={onCreateProject}
          onCancel={onToggleCreateProjectForm}
        />
      )}

      {selectedProject && canDeleteSelectedProject && (
        <button
          onClick={onDeleteProject}
          style={{
            width: "100%",
            marginBottom: "12px",
            padding: "10px 12px",
            borderRadius: "8px",
            border: "1px solid #fecaca",
            background: "#fef2f2",
            color: "#b91c1c",
            cursor: "pointer",
            fontSize: "13px",
            fontWeight: "600",
          }}
        >
          Delete Project
        </button>
      )}

      {projectsLoading && (
        <p style={{ color: "#475569", fontSize: "14px" }}>
          Loading projects...
        </p>
      )}

      {!projectsLoading && projects.length === 0 && (
        <p style={{ color: "#475569", fontSize: "14px" }}>
          No projects found.
        </p>
      )}

      {projects.map((project) => {
        const isActive = project.id === selectedProjectId;

        return (
          <button
            key={project.id}
            onClick={() => onSelectProject?.(project.id)}
            style={{
              width: "100%",
              textAlign: "left",
              padding: "12px",
              background: isActive ? "#dbeafe" : "#f1f5f9",
              borderRadius: "8px",
              marginBottom: "8px",
              border: isActive
                ? "1px solid #93c5fd"
                : "1px solid transparent",
              cursor: "pointer",
            }}
          >
            <div style={{ fontWeight: "600" }}>{project.key}</div>
            <div style={{ fontSize: "14px", color: "#475569" }}>
              {project.name}
            </div>
          </button>
        );
      })}

      <ProjectMembersPanel
        selectedProject={selectedProject}
        members={members}
        membersLoading={membersLoading}
        canManageMembers={canManageMembers}
        currentUser={currentUser}
        onAddMember={onAddMember}
        onUpdateRole={onUpdateMemberRole}
        onRemoveMember={onRemoveMember}
      />
      <ProjectLabelsPanel
        selectedProject={selectedProject}
        projectLabels={projectLabels}
        onCreateLabel={onCreateLabel}
        onDeleteLabel={onDeleteLabel}
      />
    </aside>
  );
}

export default ProjectsSidebar;