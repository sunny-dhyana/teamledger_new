import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import ProtectedRoute from '../components/ProtectedRoute';
import Modal from '../components/Modal';
import { useAuthStore } from '../store/authStore';
import { apiKeysApi } from '../api/apiKeys';
import { APIKey } from '../types';

const APIKeys: React.FC = () => {
  const { currentOrg } = useAuthStore();
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [keyName, setKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>(['read']);
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [error, setError] = useState('');

  const availableScopes = ['read', 'write', 'admin'];

  useEffect(() => {
    if (currentOrg) {
      loadAPIKeys();
    }
  }, [currentOrg]);

  const loadAPIKeys = async () => {
    try {
      const response = await apiKeysApi.list();
      if (response.success && response.data) {
        setApiKeys(response.data);
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAPIKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await apiKeysApi.create(keyName, selectedScopes);
      if (response.success && response.data) {
        setCreatedKey(response.data.key!);
        setIsModalOpen(false);
        setKeyName('');
        setSelectedScopes(['read']);
        loadAPIKeys();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create API key');
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) return;

    try {
      const response = await apiKeysApi.revoke(keyId);
      if (response.success) {
        loadAPIKeys();
      }
    } catch (error) {
      console.error('Failed to revoke API key:', error);
    }
  };

  const toggleScope = (scope: string) => {
    if (selectedScopes.includes(scope)) {
      setSelectedScopes(selectedScopes.filter(s => s !== scope));
    } else {
      setSelectedScopes([...selectedScopes, scope]);
    }
  };

  if (!currentOrg) {
    return (
      <ProtectedRoute>
        <Layout>
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No Organization Selected
            </h2>
            <p className="text-gray-600 mb-4">
              Please select an organization to manage API keys.
            </p>
            <Link
              to="/organizations"
              className="text-blue-600 hover:underline font-medium"
            >
              Go to Organizations
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
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Create API Key
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : apiKeys.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500 mb-4">You don't have any API keys yet.</p>
              <button
                onClick={() => setIsModalOpen(true)}
                className="text-blue-600 hover:underline"
              >
                Create your first API key
              </button>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Key Prefix
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Scopes
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {apiKeys.map((key) => (
                    <tr key={key.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {key.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <code className="bg-gray-100 px-2 py-1 rounded">{key.key_prefix}...</code>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex space-x-1">
                          {key.scopes.map((scope) => (
                            <span
                              key={scope}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {scope}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            key.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {key.is_active ? 'Active' : 'Revoked'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(key.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {key.is_active && (
                          <button
                            onClick={() => handleRevokeKey(key.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Create API Key Modal */}
          <Modal
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
              setError('');
            }}
            title="Create New API Key"
          >
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
            )}
            <form onSubmit={handleCreateAPIKey}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Name
                </label>
                <input
                  type="text"
                  value={keyName}
                  onChange={(e) => setKeyName(e.target.value)}
                  required
                  placeholder="e.g., Production API Key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scopes
                </label>
                <div className="space-y-2">
                  {availableScopes.map((scope) => (
                    <label key={scope} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedScopes.includes(scope)}
                        onChange={() => toggleScope(scope)}
                        className="mr-2"
                      />
                      <span className="text-sm">{scope}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={selectedScopes.length === 0}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                >
                  Create
                </button>
              </div>
            </form>
          </Modal>

          {/* Display Created Key Modal */}
          <Modal
            isOpen={!!createdKey}
            onClose={() => setCreatedKey(null)}
            title="API Key Created"
          >
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800 font-medium mb-2">
                  Important: Save this key now!
                </p>
                <p className="text-sm text-yellow-700">
                  This is the only time you'll see this key. Store it securely.
                </p>
              </div>
              <div className="bg-gray-100 p-3 rounded-md break-all font-mono text-sm">
                {createdKey}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(createdKey!);
                  alert('API key copied to clipboard!');
                }}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Copy to Clipboard
              </button>
            </div>
          </Modal>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default APIKeys;
