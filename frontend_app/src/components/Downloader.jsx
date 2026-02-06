import React, { useState } from 'react';
import { downloaderAPI } from '../api';

const Downloader = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [info, setInfo] = useState(null);
    const [error, setError] = useState('');
    const [downloading, setDownloading] = useState(false);

    const handleFetchInfo = async (e) => {
        if (e) e.preventDefault();
        if (!url) return;
        setLoading(true);
        setError('');
        setInfo(null);
        try {
            const res = await downloaderAPI.fetchInfo(url);
            setInfo(res.data);
        } catch (err) {
            setError('Failed to fetch media info. check the URL.');
            console.error(err);
        }
        setLoading(false);
    };

    const handleDownload = async (formatType) => {
        setDownloading(true);
        setError('');
        try {
            const res = await downloaderAPI.download(url, formatType);

            // Extract filename from content-disposition
            const contentDisposition = res.headers['content-disposition'] || res.headers['Content-Disposition'];
            let filename = `alexDownload_${Date.now()}`;

            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/i);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                    try {
                        filename = decodeURIComponent(filename);
                    } catch (e) { }
                }
            } else {
                filename += (formatType === 'audio' ? '.mp3' : '.mp4');
            }

            const blob = new Blob([res.data], { type: res.headers['content-type'] });
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);
        } catch (err) {
            console.error(err);
            // Try to extract error message from blob
            if (err.response && err.response.data instanceof Blob) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorData = JSON.parse(reader.result);
                        setError(`Download failed: ${errorData.detail || 'Unknown error'}`);
                    } catch (e) {
                        setError('Download failed. The video might be restricted or too large.');
                    }
                };
                reader.readAsText(err.response.data);
            } else {
                setError('Download failed. Please check your connection or try another video.');
            }
        }
        setDownloading(false);
    };

    return (
        <div className="glass-card animate-fadeIn" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h2 className="animate-pulse" style={{ textAlign: 'center', fontSize: '2rem' }}>Alex Downloader</h2>
            <p style={{ textAlign: 'center', color: 'var(--secondary-neon)', marginBottom: '2rem', fontWeight: 600 }}>
                Premium Media Extraction Hub
            </p>

            <form onSubmit={handleFetchInfo} style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <input
                    type="text"
                    className="gaming-input"
                    placeholder="Enter YouTube, Instagram, or TikTok URL..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />
                <button
                    type="submit"
                    className="gaming-btn"
                    disabled={loading || !url}
                >
                    {loading ? 'Scanning...' : 'Preview'}
                </button>
            </form>

            {error && <p style={{ color: 'var(--danger-neon)', textAlign: 'center', fontWeight: 'bold' }}>{error}</p>}

            {info && (
                <div className="glass-card" style={{ marginTop: '20px', border: '1px solid var(--secondary-neon)', padding: '2rem' }}>
                    <div style={{ display: 'flex', gap: '30px', alignItems: 'flex-start', flexWrap: 'wrap', justifyContent: 'center' }}>
                        <img
                            src={info.thumbnail}
                            alt={info.title}
                            style={{ width: '100%', maxWidth: '300px', borderRadius: '12px', boxShadow: '0 0 20px rgba(0,255,255,0.3)' }}
                        />
                        <div style={{ flex: '1 1 300px', textAlign: 'left' }}>
                            <h3 style={{
                                fontSize: '1.4rem',
                                margin: '0 0 10px 0',
                                textTransform: 'none',
                                background: 'none',
                                textShadow: '0 0 10px rgba(0, 255, 255, 0.5)',
                                color: 'white',
                                WebkitTextFillColor: 'white'
                            }}>
                                {info.title}
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>{info.uploader}</p>

                            <div style={{ display: 'flex', gap: '15px' }}>
                                <button
                                    className="gaming-btn"
                                    onClick={() => handleDownload('video')}
                                    disabled={downloading}
                                    style={{ flex: 1 }}
                                >
                                    {downloading ? 'Processing...' : 'Video (MP4)'}
                                </button>
                                <button
                                    className="gaming-btn"
                                    onClick={() => handleDownload('audio')}
                                    disabled={downloading}
                                    style={{ flex: 1, filter: 'hue-rotate(60deg)' }}
                                >
                                    {downloading ? 'Extracting...' : 'Audio (MP3)'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Downloader;
