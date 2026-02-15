# TeamLedger Frontend

React + TypeScript + Vite frontend for TeamLedger application.

## Features

- **Authentication**: Login and Registration
- **Organizations**: Create, join, and switch between organizations
- **Projects**: Create and manage projects
- **Notes**: Create, edit, and share notes within projects
- **API Keys**: Generate and manage API keys for programmatic access
- **Background Jobs**: Track export job status
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```
   The app will be available at http://localhost:3000

3. **Build for production**:
   ```bash
   npm run build
   ```
   The built files will be in the `dist` directory.

## Integration with Backend

The frontend is configured to proxy API requests to the backend running on port 8000 during development (see `vite.config.ts`).

For production, the backend serves the built frontend from the same port (8000) using FastAPI's static file mounting.

## Tech Stack

- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Zustand**: State management
- **Tailwind CSS**: Styling

## Project Structure

```
src/
├── api/           # API service layer
├── components/    # Reusable components
├── pages/         # Page components
├── store/         # Zustand stores
├── types/         # TypeScript types
├── utils/         # Utility functions
├── App.tsx        # Main app component
├── main.tsx       # Entry point
└── index.css      # Global styles
```

## Available Pages

- `/` - Home/Landing page
- `/login` - User login
- `/register` - User registration
- `/dashboard` - Main dashboard
- `/organizations` - Organization management
- `/projects` - Project list
- `/projects/:id` - Project detail with notes
- `/api-keys` - API key management
- `/shared/:token` - Public shared note view
