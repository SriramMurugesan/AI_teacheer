import { useState, useRef, useCallback } from 'react';
import { uploadPDF, listDocuments, deleteDocument } from '../api';

export default function UploadPage({ onDocumentsChange }) {
    const [documents, setDocuments] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState('');
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const refreshDocs = useCallback(async () => {
        try {
            const docs = await listDocuments();
            setDocuments(docs);
            onDocumentsChange?.(docs);
        } catch {
            // Server might not be ready yet
        }
    }, [onDocumentsChange]);

    // Load on first render
    useState(() => { refreshDocs(); });

    const handleUpload = async (file) => {
        if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
            setProgress('⚠️ Please select a PDF file');
            return;
        }

        setUploading(true);
        setProgress('📤 Uploading and processing...');

        try {
            const result = await uploadPDF(file);
            setProgress(`✅ ${result.message}`);
            await refreshDocs();
        } catch (err) {
            setProgress(`❌ ${err.message}`);
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (docId) => {
        try {
            await deleteDocument(docId);
            await refreshDocs();
        } catch {
            // ignore
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);
        const file = e.dataTransfer?.files?.[0];
        if (file) handleUpload(file);
    };

    return (
        <div style={{ display: 'grid', gap: '1.5rem' }}>
            {/* Upload Zone */}
            <div
                className={`upload-zone ${dragActive ? 'upload-zone--active' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
            >
                <span className="upload-zone__icon">📄</span>
                <h2 className="upload-zone__title">
                    {dragActive ? 'Drop your PDF here!' : 'Upload a PDF Document'}
                </h2>
                <p className="upload-zone__subtitle">
                    Drag & drop or click to browse • PDF files only
                </p>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    onChange={(e) => handleUpload(e.target.files?.[0])}
                />
            </div>

            {/* Progress */}
            {(uploading || progress) && (
                <div className="upload-progress">
                    {uploading && (
                        <div className="upload-progress__bar-container">
                            <div className="upload-progress__bar" style={{ width: '80%' }} />
                        </div>
                    )}
                    <p className="upload-progress__text">{progress}</p>
                </div>
            )}

            {/* Document List */}
            {documents.length > 0 && (
                <div className="card">
                    <div className="card__header">
                        <div className="card__icon">📚</div>
                        <div>
                            <h3 className="card__title">Your Documents</h3>
                            <p className="card__description">{documents.length} document{documents.length !== 1 ? 's' : ''} loaded</p>
                        </div>
                    </div>

                    <div className="doc-list">
                        {documents.map((doc) => (
                            <div key={doc.doc_id} className="doc-item">
                                <div className="doc-item__info">
                                    <span className="doc-item__icon">📄</span>
                                    <div>
                                        <div className="doc-item__name">{doc.filename}</div>
                                        <div className="doc-item__meta">{doc.num_chunks} chunks • ID: {doc.doc_id}</div>
                                    </div>
                                </div>
                                <div className="doc-item__actions">
                                    <span className="badge badge--success">Ready</span>
                                    <button
                                        className="btn btn--danger btn--sm"
                                        onClick={() => handleDelete(doc.doc_id)}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Info */}
            <div className="info-banner">
                <span className="info-banner__icon">💡</span>
                <span>Upload a PDF, then switch to <strong>Chat</strong> to ask questions, or <strong>Learn</strong> to generate lessons and quizzes.</span>
            </div>
        </div>
    );
}
