import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuthStore } from '../store/authStore';
import { organizationsApi } from '../api/organizations';
import { projectsApi } from '../api/projects';
import { Organization, Project } from '../types';

const Dashboard: React.FC = () => {
  const { currentOrg } = useAuthStore();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [currentOrg]);

  const loadData = async () => {
    try {
      const orgsResponse = await organizationsApi.list();
      if (orgsResponse.success && orgsResponse.data) {
        setOrganizations(orgsResponse.data);
      }

      if (currentOrg) {
        const projectsResponse = await projectsApi.list();
        if (projectsResponse.success && projectsResponse.data) {
          setProjects(projectsResponse.data);
        }
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Organizations</h2>
                  <Link
                    to="/organizations"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    View All
                  </Link>
                </div>
                {organizations.length === 0 ? (
                  <p className="text-gray-500">No organizations yet</p>
                ) : (
                  <ul className="space-y-2">
                    {organizations.slice(0, 5).map((org) => (
                      <li key={org.id} className="flex justify-between items-center">
                        <span>{org.name}</span>
                        {currentOrg?.id === org.id && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            Active
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Projects</h2>
                  <Link
                    to="/projects"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    View All
                  </Link>
                </div>
                {!currentOrg ? (
                  <p className="text-gray-500">Please select an organization first</p>
                ) : projects.length === 0 ? (
                  <p className="text-gray-500">No projects yet</p>
                ) : (
                  <ul className="space-y-2">
                    {projects.slice(0, 5).map((project) => (
                      <li key={project.id}>
                        <Link
                          to={`/projects/${project.id}`}
                          className="text-blue-600 hover:underline"
                        >
                          {project.name}
                        </Link>
                        <p className="text-sm text-gray-500">{project.status}</p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}

          {!currentOrg && organizations.length > 0 && (
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                Please select an organization to start working with projects and notes.
              </p>
              <Link
                to="/organizations"
                className="text-yellow-900 underline font-medium"
              >
                Go to Organizations
              </Link>
            </div>
          )}
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default Dashboard;
