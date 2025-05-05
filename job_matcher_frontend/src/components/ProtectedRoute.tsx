import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
  const { user, isLoading } = useAuth();

  // If user is not logged in, redirect to login page

  if (isLoading) {
    return null; // Optionally, you can show a loading spinner or message
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // If user is logged in, render the requested component
  return <Outlet />;
};

export default ProtectedRoute;