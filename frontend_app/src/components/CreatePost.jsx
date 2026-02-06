import React, { useState } from 'react';
import { socialAPI } from '../api';

const CreatePost = ({ onPostCreated }) => {
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!content.trim()) return;
        setLoading(true);
        try {
            await socialAPI.createPost({ content });
            setContent('');
            onPostCreated();
        } catch (err) {
            alert('Failed to post');
        }
        setLoading(false);
    };

    return (
        <div className="card" style={{ marginBottom: '20px' }}>
            <form onSubmit={handleSubmit}>
                <textarea
                    placeholder="What's on your mind?"
                    style={{
                        width: '100%',
                        border: 'none',
                        padding: '12px',
                        backgroundColor: 'var(--bg-main)',
                        color: 'var(--text-color)',
                        borderRadius: '8px',
                        outline: 'none',
                        resize: 'none',
                        minHeight: '100px',
                        fontSize: '16px'
                    }}
                    value={content}
                    onChange={e => setContent(e.target.value)}
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
                    <button type="submit" className="primary" disabled={loading || !content.trim()} style={{ padding: '8px 24px' }}>
                        {loading ? 'Posting...' : 'Post'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CreatePost;
