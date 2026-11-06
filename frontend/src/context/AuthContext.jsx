import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('nexoraiq_token'));
  const [workspaces, setWorkspaces] = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [activeDataset, setActiveDataset] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        // If no token exists, log in demo user automatically for frictionless evaluation
        let currentToken = token;
        if (!currentToken) {
          const res = await api.post('/auth/login', {
            email: 'demo@nexoraiq.com',
            password: 'demo1234'
          });
          currentToken = res.data.access_token;
          localStorage.setItem('nexoraiq_token', currentToken);
          setToken(currentToken);
          setUser(res.data.user);
        } else {
          const res = await api.get('/auth/me');
          setUser(res.data);
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  // Fetch workspaces when user is loaded
  useEffect(() => {
    if (!user) return;
    const fetchWorkspaces = async () => {
      try {
        const res = await api.get('/workspaces/');
        setWorkspaces(res.data);
        if (res.data.length > 0) {
          const current = res.data.find(w => w.id === user.workspace_id) || res.data[0];
          setActiveWorkspace(current);
        }
      } catch (err) {
        console.error('Error fetching workspaces:', err);
      }
    };
    fetchWorkspaces();
  }, [user]);

  // Fetch datasets when active workspace changes
  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchDatasets = async () => {
      try {
        const res = await api.get(`/datasets/?workspace_id=${activeWorkspace.id}`);
        setDatasets(res.data);
        if (res.data.length > 0) {
          setActiveDataset(res.data[0]);
        } else {
          setActiveDataset(null);
        }
      } catch (err) {
        console.error('Error fetching datasets:', err);
      }
    };
    fetchDatasets();
  }, [activeWorkspace]);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    localStorage.setItem('nexoraiq_token', res.data.access_token);
    setToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const register = async (email, password, full_name, organization_name) => {
    const res = await api.post('/auth/register', {
      email,
      password,
      full_name,
      organization_name
    });
    localStorage.setItem('nexoraiq_token', res.data.access_token);
    setToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('nexoraiq_token');
    setToken(null);
    setUser(null);
    setWorkspaces([]);
    setActiveWorkspace(null);
    setDatasets([]);
    setActiveDataset(null);
  };

  const switchWorkspace = (wsId) => {
    const ws = workspaces.find(w => w.id === wsId);
    if (ws) setActiveWorkspace(ws);
  };

  const switchDataset = (dsId) => {
    const ds = datasets.find(d => d.id === dsId);
    if (ds) setActiveDataset(ds);
  };

  const refreshDatasets = async () => {
    if (!activeWorkspace) return;
    const res = await api.get(`/datasets/?workspace_id=${activeWorkspace.id}`);
    setDatasets(res.data);
    if (res.data.length > 0 && !activeDataset) {
      setActiveDataset(res.data[0]);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      workspaces,
      activeWorkspace,
      datasets,
      activeDataset,
      loading,
      login,
      register,
      logout,
      switchWorkspace,
      switchDataset,
      refreshDatasets
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

