import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { notesApi } from '../api/notes';
import { Note } from '../types';

const SharedNote: React.FC = () => {
  const { shareToken } = useParams<{ shareToken: string }>();
  const [note, setNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (shareToken) {
      loadSharedNote();
    }
  }, [shareToken]);

  const loadSharedNote = async () => {
    try {
      const response = await notesApi.getSharedNote(shareToken!);
      if (response.success && response.data) {
        setNote(response.data);
      } else {
        setError('Note not found or link has been revoked');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load shared note');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!note) return;

    setSaving(true);
    try {
      const response = await notesApi.updateSharedNote(shareToken!, editContent);
      if (response.success && response.data) {
        setNote(response.data);
        setIsEditing(false);
        // updated_at will be updated from response
      }
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to save note');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-bold text-red-900 mb-2">Error</h2>
            <p className="text-red-700">{error}</p>
          </div>
        ) : note ? (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="mb-4 flex justify-between items-center">
              <div>
                <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2">
                  Shared Note
                </span>
                {note.share_access_level === 'edit' && (
                  <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                    Edit Access
                  </span>
                )}
              </div>
              {note.share_access_level === 'edit' && !isEditing && (
                <button
                  onClick={() => {
                    setEditContent(note.content);
                    setIsEditing(true);
                  }}
                  className="text-white bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                >
                  Edit Note
                </button>
              )}
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-4">{note.title}</h1>
            <div className="text-sm text-gray-500 mb-6">
              Last updated: {new Date(note.updated_at).toLocaleString()}
            </div>

            {isEditing ? (
              <div className="space-y-4">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="w-full h-64 p-4 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="prose max-w-none">
                <div className="text-gray-800 whitespace-pre-wrap">{note.content}</div>
              </div>
            )}
          </div>
        ) : null}
      </div>
    </Layout>
  );
};

export default SharedNote;
