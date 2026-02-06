import React from 'react';
import { socialAPI } from '../api';

const Post = ({ post }) => {
    const handleReact = async (type) => {
        try {
            await socialAPI.reactToPost({ post_id: post.id, type });
        } catch (err) {
            console.error('Reaction failed');
        }
    };

    return (
        <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    backgroundColor: '#ddd',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    color: 'var(--primary-color)'
                }}>
                    U
                </div>
                <div>
                    <div style={{ fontWeight: '600' }}>User {post.user_id}</div>
                    <div style={{ fontSize: '12px', color: 'gray' }}>{new Date(post.created_at).toLocaleString()}</div>
                </div>
            </div>
            <p style={{ marginBottom: '16px', lineHeight: '1.5' }}>{post.content}</p>
            {post.image_url && <img src={post.image_url} alt="post" style={{ width: '100%', borderRadius: '8px', marginBottom: '16px' }} />}
            <hr style={{ borderColor: 'var(--border-color)', marginBottom: '8px' }} />
            <div style={{ display: 'flex', gap: '8px' }}>
                <button style={{ flex: 1, background: 'none', color: 'var(--text-color)' }} onClick={() => handleReact('like')}>👍 Like</button>
                <button style={{ flex: 1, background: 'none', color: 'var(--text-color)' }}>💬 Comment</button>
                <button style={{ flex: 1, background: 'none', color: 'var(--text-color)' }}>↗️ Share</button>
            </div>
        </div>
    );
};

export default Post;
