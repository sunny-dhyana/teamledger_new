import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../components/Layout';
import ProtectedRoute from '../components/ProtectedRoute';
import Modal from '../components/Modal';
import { projectsApi } from '../api/projects';
import { notesApi } from '../api/notes';
import { jobsApi } from '../api/jobs';
import { Project, Note } from '../types';

const ProjectDetail: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [isNoteModalOpen, setIsNoteModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [projectStatus, setProjectStatus] = useState('');
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [shareAccessLevel, setShareAccessLevel] = useState<'view' | 'edit'>('view');
  const [shareNote, setShareNote] = useState<Note | null>(null);
  const [isShareConfigModalOpen, setIsShareConfigModalOpen] = useState(false);
  const [exportJobId, setExportJobId] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (projectId) {
      loadProjectData();
    }
  }, [projectId]);

  const loadProjectData = async () => {
    try {
      const [projectResponse, notesResponse] = await Promise.all([
        projectsApi.get(projectId!),
        notesApi.list(projectId!),
      ]);

      if (projectResponse.success && projectResponse.data) {
        setProject(projectResponse.data);
        setProjectName(projectResponse.data.name);
        setProjectDescription(projectResponse.data.description);
        setProjectStatus(projectResponse.data.status);
      }

      if (notesResponse.success && notesResponse.data) {
        setNotes(notesResponse.data);
      }
    } catch (error) {
      console.error('Failed to load project data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await notesApi.create(projectId!, noteTitle, noteContent);
      if (response.success) {
        setIsNoteModalOpen(false);
        setNoteTitle('');
        setNoteContent('');
        loadProjectData();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create note');
    }
  };

  const handleUpdateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedNote) return;

    try {
      const response = await notesApi.update(projectId!, selectedNote.id, {
        title: noteTitle,
        content: noteContent,
      });
      if (response.success) {
        setIsEditModalOpen(false);
        setSelectedNote(null);
        setNoteTitle('');
        setNoteContent('');
        loadProjectData();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update note');
    }
  };

  const handleUpdateProject = async () => {
    setError('');

    try {
      const response = await projectsApi.update(projectId!, {
        name: projectName,
        description: projectDescription,
        status: projectStatus,
      });
      if (response.success) {
        loadProjectData();
        alert('Project updated successfully!');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update project');
    }
  };

  const openShareConfigModal = (note: Note) => {
    setShareNote(note);
    setShareAccessLevel('view'); // Default
    setIsShareConfigModalOpen(true);
  };

  const handleGenerateShareLink = async () => {
    if (!shareNote) return;

    try {
      const response = await notesApi.generateShareLink(projectId!, shareNote.id, shareAccessLevel);
      if (response.success && response.data) {
        setShareUrl(response.data.share_url);
        setIsShareConfigModalOpen(false);
        setShareNote(null);
        loadProjectData(); // Reload to update UI
      }
    } catch (error) {
      console.error('Failed to generate share link:', error);
      alert('Failed to generate share link');
    }
  };

  const handleRevokeShareLink = async (noteId: string) => {
    try {
      const response = await notesApi.revokeShareLink(projectId!, noteId);
      if (response.success) {
        loadProjectData();
        alert('Share link revoked successfully!');
      }
    } catch (error) {
      console.error('Failed to revoke share link:', error);
    }
  };

  const handleExportProject = async () => {
    try {
      const response = await projectsApi.export(projectId!);
      if (response.success && response.data) {
        setExportJobId(response.data.id);
        alert(`Export job started! Job ID: ${response.data.id}`);
      }
    } catch (error) {
      console.error('Failed to export project:', error);
    }
  };

  const handleCheckJobStatus = async () => {
    if (!exportJobId) return;

    try {
      const response = await jobsApi.get(exportJobId);
      if (response.success && response.data) {
        alert(`Job Status: ${response.data.status}\n${response.data.result_path || 'Processing...'}`);
      }
    } catch (error) {
      console.error('Failed to check job status:', error);
    }
  };

  const openEditModal = (note: Note) => {
    setSelectedNote(note);
    setNoteTitle(note.title);
    setNoteContent(note.content);
    setIsEditModalOpen(true);
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <Layout>
          <div className="text-center py-12">Loading...</div>
        </Layout>
      </ProtectedRoute>
    );
  }

  if (!project) {
    return (
      <ProtectedRoute>
        <Layout>
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Project Not Found</h2>
            <Link to="/projects" className="text-blue-600 hover:underline">
              Back to Projects
            </Link>
          </div>
        </Layout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <div className="mb-6">
            <Link to="/projects" className="text-blue-600 hover:underline mb-2 inline-block">
              &larr; Back to Projects
            </Link>
          </div>

          {/* Project Details */}
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Project Details</h1>
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={projectStatus}
                  onChange={(e) => setProjectStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleUpdateProject}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Update Project
              </button>
              <button
                onClick={handleExportProject}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                Export Project
              </button>
              {exportJobId && (
                <button
                  onClick={handleCheckJobStatus}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
                >
                  Check Export Status
                </button>
              )}
            </div>
          </div>

          {/* Notes Section */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900">Notes</h2>
              <button
                onClick={() => setIsNoteModalOpen(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Create Note
              </button>
            </div>

            {notes.length === 0 ? (
              <p className="text-gray-500">No notes yet. Create your first note!</p>
            ) : (
              <div className="space-y-4">
                {notes.map((note) => (
                  <div key={note.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-semibold">{note.title}</h3>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => openEditModal(note)}
                          className="text-blue-600 hover:underline text-sm"
                        >
                          Edit
                        </button>
                        {note.is_shared ? (
                          <button
                            onClick={() => handleRevokeShareLink(note.id)}
                            className="text-red-600 hover:underline text-sm"
                          >
                            Revoke Share
                          </button>
                        ) : (
                          <button
                            onClick={() => openShareConfigModal(note)}
                            className="text-green-600 hover:underline text-sm"
                          >
                            Share
                          </button>
                        )}
                      </div>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{note.content}</p>
                    <div className="mt-2 text-xs text-gray-500">
                      Version {note.version} • {new Date(note.updated_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Create Note Modal */}
          <Modal
            isOpen={isNoteModalOpen}
            onClose={() => {
              setIsNoteModalOpen(false);
              setError('');
            }}
            title="Create New Note"
          >
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
            )}
            <form onSubmit={handleCreateNote}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <textarea
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  required
                  rows={5}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsNoteModalOpen(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Create
                </button>
              </div>
            </form>
          </Modal>

          {/* Edit Note Modal */}
          <Modal
            isOpen={isEditModalOpen}
            onClose={() => {
              setIsEditModalOpen(false);
              setSelectedNote(null);
              setError('');
            }}
            title="Edit Note"
          >
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
            )}
            <form onSubmit={handleUpdateNote}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <textarea
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  required
                  rows={5}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Update
                </button>
              </div>
            </form>
          </Modal>

          {/* Share URL Modal */}
          <Modal
            isOpen={!!shareUrl}
            onClose={() => setShareUrl(null)}
            title="Share Link Generated"
          >
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Share this link with others to give them public access to the note:
              </p>
              <div className="bg-gray-100 p-3 rounded-md break-all text-sm">
                {shareUrl}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(shareUrl!);
                  alert('Link copied to clipboard!');
                }}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Copy to Clipboard
              </button>
            </div>
          </Modal>

          {/* Share Configuration Modal */}
          <Modal
            isOpen={isShareConfigModalOpen}
            onClose={() => {
              setIsShareConfigModalOpen(false);
              setShareNote(null);
            }}
            title="Share Note"
          >
            <div className="space-y-4">
              <p className="text-gray-600">
                Configure sharing settings for <strong>{shareNote?.title}</strong>.
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Access Level</label>
                <select
                  value={shareAccessLevel}
                  onChange={(e) => setShareAccessLevel(e.target.value as 'view' | 'edit')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="view">View Only (Read access)</option>
                  <option value="edit">Edit (Who has link can edit)</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {shareAccessLevel === 'view'
                    ? 'Users with the link can only view the note content.'
                    : 'Users with the link can view and edit the note content anonymously.'}
                </p>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <button
                  onClick={() => setIsShareConfigModalOpen(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateShareLink}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  Generate Link
                </button>
              </div>
            </div>
          </Modal>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default ProjectDetail;
