import { useState, useRef, useEffect } from 'react';
import { streamQuestion } from '../api';

export default function ChatPage({ documents }) {
    const [selectedDoc, setSelectedDoc] = useState('');
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Auto-select first document
    useEffect(() => {
        if (documents.length > 0 && !selectedDoc) {
            setSelectedDoc(documents[0].doc_id);
        }
    }, [documents, selectedDoc]);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        const question = input.trim();
        if (!question || !selectedDoc || loading) return;

        setInput('');
        setMessages((prev) => [...prev, { role: 'user', content: question }]);
        setLoading(true);

        // Add empty assistant message that we'll stream into
        const assistantIdx = messages.length + 1;
        setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

        try {
            await streamQuestion(
                selectedDoc,
                question,
                (token) => {
                    setMessages((prev) => {
                        const updated = [...prev];
                        const last = updated[updated.length - 1];
                        if (last?.role === 'assistant') {
                            updated[updated.length - 1] = { ...last, content: last.content + token };
                        }
                        return updated;
                    });
                },
                () => setLoading(false),
            );
        } catch (err) {
            setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                    role: 'assistant',
                    content: `❌ Error: ${err.message}`,
                };
                return updated;
            });
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (documents.length === 0) {
        return (
            <div className="chat">
                <div className="chat__empty">
                    <span className="chat__empty-icon">📄</span>
                    <span className="chat__empty-text">No documents uploaded yet</span>
                    <span className="chat__empty-hint">Upload a PDF first to start chatting</span>
                </div>
            </div>
        );
    }

    return (
        <div className="chat">
            {/* Document Selector */}
            <div className="chat__doc-selector">
                <label>📄 Document:</label>
                <select
                    value={selectedDoc}
                    onChange={(e) => setSelectedDoc(e.target.value)}
                >
                    {documents.map((doc) => (
                        <option key={doc.doc_id} value={doc.doc_id}>
                            {doc.filename} ({doc.num_chunks} chunks)
                        </option>
                    ))}
                </select>
            </div>

            {/* Messages */}
            <div className="chat__messages">
                {messages.length === 0 ? (
                    <div className="chat__empty">
                        <span className="chat__empty-icon">💬</span>
                        <span className="chat__empty-text">Ask anything about your document</span>
                        <span className="chat__empty-hint">I'll find relevant sections and explain like a teacher</span>
                    </div>
                ) : (
                    messages.map((msg, i) => (
                        <div key={i} className={`message message--${msg.role}`}>
                            {msg.role === 'assistant' && msg.content === '' ? (
                                <>
                                    <span className="message__dot" />
                                    <span className="message__dot" />
                                    <span className="message__dot" />
                                </>
                            ) : (
                                msg.content
                            )}
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="chat__input-container">
                <textarea
                    ref={inputRef}
                    className="chat__input"
                    rows={1}
                    placeholder="Ask a question about your document..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                />
                <button
                    className="chat__send-btn"
                    onClick={handleSend}
                    disabled={!input.trim() || loading || !selectedDoc}
                    aria-label="Send message"
                >
                    ➤
                </button>
            </div>
        </div>
    );
}
