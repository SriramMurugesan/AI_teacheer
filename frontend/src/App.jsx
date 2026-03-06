import { useState, useCallback } from 'react';
import UploadPage from './components/UploadPage';
import ChatPage from './components/ChatPage';
import LearnPage from './components/LearnPage';

const TABS = [
    { id: 'upload', label: 'Upload', icon: '📄' },
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'learn', label: 'Learn', icon: '📚' },
];

export default function App() {
    const [activeTab, setActiveTab] = useState('upload');
    const [documents, setDocuments] = useState([]);

    const handleDocumentsChange = useCallback((docs) => {
        setDocuments(docs);
    }, []);

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="app-header__logo">
                    <span className="app-header__icon">🎓</span>
                    <div>
                        <h1 className="app-header__title">AI PDF Tutor</h1>
                        <span className="app-header__subtitle">Powered by RAG • Learn from any PDF</span>
                    </div>
                </div>

                <nav className="app-nav">
                    {TABS.map((tab) => (
                        <button
                            key={tab.id}
                            className={`app-nav__btn ${activeTab === tab.id ? 'app-nav__btn--active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            <span>{tab.icon}</span>
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </header>

            {/* Main Content */}
            <main className="app-main">
                {activeTab === 'upload' && (
                    <UploadPage onDocumentsChange={handleDocumentsChange} />
                )}
                {activeTab === 'chat' && (
                    <ChatPage documents={documents} />
                )}
                {activeTab === 'learn' && (
                    <LearnPage documents={documents} />
                )}
            </main>
        </div>
    );
}
