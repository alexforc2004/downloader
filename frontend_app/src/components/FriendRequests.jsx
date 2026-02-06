import React, { useEffect, useState } from 'react';
import { socialAPI } from '../api';

const FriendRequests = () => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchRequests = async () => {
        try {
            const res = await socialAPI.getFriendRequests();
            setRequests(res.data);
        } catch (err) {
            console.error('Failed to fetch requests');
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchRequests();
        const interval = setInterval(fetchRequests, 15000);
        return () => clearInterval(interval);
    }, []);

    const handleAccept = async (userId) => {
        try {
            await socialAPI.acceptFriendRequest(userId);
            fetchRequests();
        } catch (err) {
            alert('Failed to accept');
        }
    };

    if (loading) return <div className="card"><h3>Friend Requests</h3><p>Loading...</p></div>;

    return (
        <div className="card">
            <h3 style={{ marginBottom: '12px' }}>Friend Requests</h3>
            {requests.length === 0 ? (
                <p style={{ fontSize: '14px', color: 'gray' }}>No new requests</p>
            ) : (
                <div>
                    {requests.map(user => (
                        <div key={user.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                            <span style={{ fontWeight: '600' }}>{user.full_name}</span>
                            <button
                                className="primary"
                                style={{ padding: '6px 12px', fontSize: '12px' }}
                                onClick={() => handleAccept(user.id)}
                            >
                                Confirm
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FriendRequests;
