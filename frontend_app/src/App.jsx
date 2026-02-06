import React, { useState, useEffect } from 'react';
import './index.css';
import Login from './components/Login';
import Downloader from './components/Downloader';
import { authAPI } from './api';

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [view, setView] = useState(window.location.hash === '#downloader' ? 'downloader' : 'feed');

    useEffect(() => {
        const handleHashChange = () => {
            if (window.location.hash === '#downloader' || window.location.hash === '#downloader-only') {
                setView('downloader');
            } else {
                setView('feed');
            }
        };
        window.addEventListener('hashchange', handleHashChange);
        return () => window.removeEventListener('hashchange', handleHashChange);
    }, []);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', 'dark');
    }, []);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const res = await authAPI.getMe();
                setUser(res.data);
            } catch (err) {
                localStorage.removeItem('token');
            }
        }
        setLoading(false);
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    const isOnlyDownloader = window.location.hash === '#downloader-only';

    if (loading) return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            background: 'var(--bg-gaming)',
            color: 'var(--secondary-neon)',
            fontSize: '1.5rem',
            fontWeight: 'bold'
        }}>
            <div className="animate-pulse">Loading alexDownloader...</div>
        </div>
    );

    return (
        <div className="App">
            {!isOnlyDownloader && (
                <nav className="glass-card" style={{
                    padding: '0.8rem 2rem',
                    margin: '1rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    position: 'sticky',
                    top: '1rem',
                    zIndex: 100,
                    borderRadius: '15px'
                }}>
                    <h1 className="animate-pulse" style={{ fontSize: '24px', cursor: 'pointer', margin: 0 }} onClick={() => window.location.hash = 'downloader'}>alexDownloader</h1>
                    <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                        <button className={`gaming-btn ${view === 'downloader' ? 'active' : ''}`} onClick={() => window.location.hash = 'downloader'}>Downloader</button>
                    </div>
                    <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
                        {user && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <span className="glow-text">{user.full_name}</span>
                                <button className="gaming-btn" onClick={handleLogout} style={{ padding: '5px 10px', fontSize: '13px' }}>Logout</button>
                            </div>
                        )}
                    </div>
                </nav>
            )}

            <main className="container">
                {(view === 'downloader' || isOnlyDownloader || view === 'feed') ? (
                    <Downloader />
                ) : !user ? (
                    <div className="glass-card">
                        <Login onLoginSuccess={checkAuth} />
                    </div>
                ) : (
                    <div className="glass-card">
                        <div style={{ textAlign: 'center', padding: '2rem' }}>
                            <h2 className="glow-text">Feed Coming Soon</h2>
                            <p>We are currently focusing on giving you the best download experience!</p>
                            <button className="gaming-btn" onClick={() => window.location.hash = 'downloader'} style={{ marginTop: '1rem' }}>
                                Use Downloader
                            </button>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
