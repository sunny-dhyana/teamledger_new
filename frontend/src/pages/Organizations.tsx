import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import ProtectedRoute from '../components/ProtectedRoute';
import Modal from '../components/Modal';
import { useAuthStore } from '../store/authStore';
import { organizationsApi } from '../api/organizations';
import { Organization } from '../types';

const Organizations: React.FC = () => {
  const { currentOrg, setCurrentOrg, setAuth, token } = useAuthStore();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const [inviteToken, setInviteToken] = useState('');
  const [, setSelectedOrgForInvite] = useState<string | null>(null);
  const [generatedInviteToken, setGeneratedInviteToken] = useState<string | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    try {
      const response = await organizationsApi.list();
      if (response.success && response.data) {
        setOrganizations(response.data);
      }
    } catch (error) {
      console.error('Failed to load organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await organizationsApi.create(newOrgName);
      if (response.success) {
        setIsCreateModalOpen(false);
        setNewOrgName('');
        loadOrganizations();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create organization');
    }
  };

  const handleSwitchOrganization = async (orgId: string) => {
    try {
      const response = await organizationsApi.switch(orgId);
      if (response.success && response.data) {
        const org = organizations.find(o => o.id === orgId);
        if (org) {
          setCurrentOrg(org);
          if (token) {
            setAuth(response.data.access_token, useAuthStore.getState().user!);
          }
          navigate('/dashboard');
        }
      }
    } catch (error) {
      console.error('Failed to switch organization:', error);
    }
  };

  const handleGenerateInvite = async (orgId: string) => {
    try {
      const response = await organizationsApi.generateInvite(orgId);
      if (response.success && response.data) {
        setGeneratedInviteToken(response.data.invite_token);
        setSelectedOrgForInvite(orgId);
      }
    } catch (error) {
      console.error('Failed to generate invite:', error);
    }
  };

  const handleJoinOrganization = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await organizationsApi.joinOrganization(inviteToken);
      if (response.success) {
        setIsJoinModalOpen(false);
        setInviteToken('');
        loadOrganizations();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to join organization');
    }
  };

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Organizations</h1>
            <div className="space-x-2">
              <button
                onClick={() => setIsJoinModalOpen(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                Join Organization
              </button>
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Create Organization
              </button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : organizations.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500 mb-4">You don't have any organizations yet.</p>
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="text-blue-600 hover:underline"
              >
                Create your first organization
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {organizations.map((org) => (
                <div key={org.id} className="bg-white p-6 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-semibold">{org.name}</h3>
                    {currentOrg?.id === org.id && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mb-4">Slug: {org.slug}</p>
                  <div className="space-y-2">
                    {currentOrg?.id !== org.id && (
                      <button
                        onClick={() => handleSwitchOrganization(org.id)}
                        className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                      >
                        Switch to this Org
                      </button>
                    )}
                    <button
                      onClick={() => handleGenerateInvite(org.id)}
                      className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 text-sm"
                    >
                      Generate Invite Link
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Create Organization Modal */}
          <Modal
            isOpen={isCreateModalOpen}
            onClose={() => {
              setIsCreateModalOpen(false);
              setError('');
            }}
            title="Create New Organization"
          >
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
            )}
            <form onSubmit={handleCreateOrganization}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
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

          {/* Join Organization Modal */}
          <Modal
            isOpen={isJoinModalOpen}
            onClose={() => {
              setIsJoinModalOpen(false);
              setError('');
            }}
            title="Join Organization"
          >
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>
            )}
            <form onSubmit={handleJoinOrganization}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Invite Token
                </label>
                <input
                  type="text"
                  value={inviteToken}
                  onChange={(e) => setInviteToken(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter invite token"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsJoinModalOpen(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  Join
                </button>
              </div>
            </form>
          </Modal>

          {/* Invite Token Display Modal */}
          <Modal
            isOpen={!!generatedInviteToken}
            onClose={() => {
              setGeneratedInviteToken(null);
              setSelectedOrgForInvite(null);
            }}
            title="Invite Token Generated"
          >
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Share this token with others to invite them to your organization:
              </p>
              <div className="bg-gray-100 p-3 rounded-md break-all font-mono text-sm">
                {generatedInviteToken}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedInviteToken!);
                  alert('Token copied to clipboard!');
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

export default Organizations;
