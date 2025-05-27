import React from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * RoleGuard component for conditional rendering based on user roles
 * 
 * Props:
 * - roles: array of roles that can view the content (e.g., ['ADMIN', 'MODERATOR'])
 * - requireAll: boolean, if true requires all roles, if false requires any role (default: false)
 * - fallback: component to render when user doesn't have required role
 * - children: content to render when user has required role
 */
const RoleGuard = ({ 
  roles = [], 
  requireAll = false, 
  fallback = null, 
  children 
}) => {
  const { user, hasRole, isAdmin, isModerator } = useAuth();

  // If no user is logged in, don't show anything
  if (!user || !user.profile) {
    return fallback;
  }

  // Helper function to check if user has required roles
  const hasRequiredRoles = () => {
    if (roles.length === 0) {
      return true; // No specific roles required
    }

    const userHasRoles = roles.map(role => {
      switch (role.toUpperCase()) {
        case 'ADMIN':
          return isAdmin();
        case 'MODERATOR':
          return isModerator();
        case 'USER':
          return hasRole('USER');
        default:
          return hasRole(role);
      }
    });

    return requireAll 
      ? userHasRoles.every(hasRole => hasRole)
      : userHasRoles.some(hasRole => hasRole);
  };

  return hasRequiredRoles() ? children : fallback;
};

export default RoleGuard;