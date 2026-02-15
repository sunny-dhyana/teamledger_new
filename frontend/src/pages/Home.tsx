import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuthStore } from '../store/authStore';

const Home: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <Layout>
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to TeamLedger
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          A lightweight multi-tenant SaaS platform for managing organizations, projects, and notes.
        </p>
        {!user ? (
          <div className="space-x-4">
            <Link
              to="/register"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="inline-block bg-gray-200 text-gray-900 px-6 py-3 rounded-md font-medium hover:bg-gray-300"
            >
              Login
            </Link>
          </div>
        ) : (
          <Link
            to="/dashboard"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>
        )}
      </div>
    </Layout>
  );
};

export default Home;
