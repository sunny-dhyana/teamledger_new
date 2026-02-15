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
            <div className="mb-4">
              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                Shared Note
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{note.title}</h1>
            <div className="text-sm text-gray-500 mb-6">
              Last updated: {new Date(note.updated_at).toLocaleString()}
            </div>
            <div className="prose max-w-none">
              <div className="text-gray-800 whitespace-pre-wrap">{note.content}</div>
            </div>
          </div>
        ) : null}
      </div>
    </Layout>
  );
};

export default SharedNote;
