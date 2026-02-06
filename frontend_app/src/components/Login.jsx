import React, { useState } from 'react';
import { authAPI } from '../api';

const Login = ({ onLoginSuccess }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: '',
        full_name: ''
    });
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                const params = new URLSearchParams();
                params.append('username', formData.username);
                params.append('password', formData.password);
                const res = await authAPI.login(params);
                localStorage.setItem('token', res.data.access_token);
                onLoginSuccess();
            } else {
                await authAPI.register(formData);
                setIsLogin(true);
                alert('Registration successful! Please login.');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred');
        }
    };

    return (
        <div className="card" style={{ maxWidth: '450px', margin: '40px auto' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '24px' }}>{isLogin ? 'Log in to SocialApp' : 'Create an Account'}</h2>
            {error && <p style={{ color: 'var(--error-color)', fontSize: '14px', marginBottom: '12px', textAlign: 'center' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                {!isLogin && (
                    <>
                        <div className="input-group">
                            <input
                                type="text"
                                placeholder="Full Name"
                                required
                                onChange={e => setFormData({ ...formData, full_name: e.target.value })}
                            />
                        </div>
                        <div className="input-group">
                            <input
                                type="email"
                                placeholder="Email Address"
                                required
                                onChange={e => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>
                    </>
                )}
                <div className="input-group">
                    <input
                        type="text"
                        placeholder="Username"
                        required
                        onChange={e => setFormData({ ...formData, username: e.target.value })}
                    />
                </div>
                <div className="input-group">
                    <input
                        type="password"
                        placeholder="Password"
                        required
                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                    />
                </div>
                <button type="submit" className="primary" style={{ width: '100%', padding: '14px', fontSize: '16px' }}>
                    {isLogin ? 'Log In' : 'Sign Up'}
                </button>
            </form>
            <hr style={{ margin: '24px 0', borderColor: 'var(--border-color)' }} />
            <button
                style={{ width: '100%', backgroundColor: 'var(--accent-color)', color: 'white', padding: '14px' }}
                onClick={() => setIsLogin(!isLogin)}
            >
                {isLogin ? 'Create New Account' : 'Already have an account?'}
            </button>
        </div>
    );
};

export default Login;
