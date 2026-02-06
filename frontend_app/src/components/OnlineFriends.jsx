import React, { useEffect, useState } from 'react';

const OnlineFriends = ({ userId }) => {
    const [friends, setFriends] = useState([]);

    useEffect(() => {
        if (!userId) return;

        const socket = new WebSocket(`ws://localhost:8000/ws/${userId}`);

        socket.onopen = () => console.log('WebSocket connected');
        socket.onmessage = (event) => {
            // Handle updates if backend sends them
        };

        return () => socket.close();
    }, [userId]);

    return (
        <div className="card">
            <h3 style={{ marginBottom: '12px' }}>Online Friends</h3>
            <div>
                {friends.length === 0 ? (
                    <p style={{ fontSize: '14px', color: 'gray' }}>Your friends list is currently offline or empty.</p>
                ) : (
                    friends.map(friend => (
                        <div key={friend.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#2dba4e' }}></div>
                            <span style={{ fontWeight: '500' }}>{friend.full_name}</span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default OnlineFriends;
