import { useState, useEffect } from 'react';
import { generateLesson, generateQuiz } from '../api';

export default function LearnPage({ documents }) {
    const [selectedDoc, setSelectedDoc] = useState('');
    const [topic, setTopic] = useState('');
    const [difficulty, setDifficulty] = useState('beginner');
    const [numQuestions, setNumQuestions] = useState(5);
    const [output, setOutput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState('lesson'); // 'lesson' | 'quiz'

    useEffect(() => {
        if (documents.length > 0 && !selectedDoc) {
            setSelectedDoc(documents[0].doc_id);
        }
    }, [documents, selectedDoc]);

    const handleGenerate = async () => {
        if (!selectedDoc || loading) return;
        setLoading(true);
        setOutput('');

        try {
            if (mode === 'lesson') {
                const res = await generateLesson(selectedDoc, topic, difficulty);
                setOutput(res.lesson);
            } else {
                const res = await generateQuiz(selectedDoc, topic, numQuestions, difficulty);
                setOutput(res.quiz);
            }
        } catch (err) {
            setOutput(`❌ Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (documents.length === 0) {
        return (
            <div className="chat">
                <div className="chat__empty">
                    <span className="chat__empty-icon">📚</span>
                    <span className="chat__empty-text">No documents uploaded yet</span>
                    <span className="chat__empty-hint">Upload a PDF first to generate lessons & quizzes</span>
                </div>
            </div>
        );
    }

    return (
        <div className="panel">
            {/* Mode Selector */}
            <div style={{ display: 'flex', gap: '0.25rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)', padding: '4px', width: 'fit-content' }}>
                <button
                    className={`app-nav__btn ${mode === 'lesson' ? 'app-nav__btn--active' : ''}`}
                    onClick={() => { setMode('lesson'); setOutput(''); }}
                >
                    📚 Lesson
                </button>
                <button
                    className={`app-nav__btn ${mode === 'quiz' ? 'app-nav__btn--active' : ''}`}
                    onClick={() => { setMode('quiz'); setOutput(''); }}
                >
                    📝 Quiz
                </button>
            </div>

            {/* Controls */}
            <div className="card">
                <div className="panel__controls">
                    <div className="panel__field">
                        <label className="panel__label">Document</label>
                        <select
                            className="panel__select"
                            value={selectedDoc}
                            onChange={(e) => setSelectedDoc(e.target.value)}
                        >
                            {documents.map((doc) => (
                                <option key={doc.doc_id} value={doc.doc_id}>
                                    {doc.filename}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="panel__field">
                        <label className="panel__label">Topic (optional)</label>
                        <input
                            className="panel__input"
                            type="text"
                            placeholder="e.g., Operating Systems"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                        />
                    </div>

                    <div className="panel__field">
                        <label className="panel__label">Difficulty</label>
                        <select
                            className="panel__select"
                            value={difficulty}
                            onChange={(e) => setDifficulty(e.target.value)}
                        >
                            <option value="beginner">🟢 Beginner</option>
                            <option value="intermediate">🟡 Intermediate</option>
                            <option value="advanced">🔴 Advanced</option>
                        </select>
                    </div>

                    {mode === 'quiz' && (
                        <div className="panel__field">
                            <label className="panel__label">Questions</label>
                            <select
                                className="panel__select"
                                value={numQuestions}
                                onChange={(e) => setNumQuestions(Number(e.target.value))}
                            >
                                {[3, 5, 10, 15, 20].map((n) => (
                                    <option key={n} value={n}>{n} questions</option>
                                ))}
                            </select>
                        </div>
                    )}

                    <button
                        className="btn btn--primary btn--lg"
                        onClick={handleGenerate}
                        disabled={loading || !selectedDoc}
                        style={{ alignSelf: 'flex-end' }}
                    >
                        {loading ? (
                            <>
                                <span className="spinner" />
                                Generating...
                            </>
                        ) : (
                            <>
                                {mode === 'lesson' ? '📚 Generate Lesson' : '📝 Generate Quiz'}
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Output */}
            <div className={`panel__output ${!output ? 'panel__output--empty' : ''}`}>
                {output || (
                    mode === 'lesson'
                        ? 'Your AI-generated lesson will appear here...'
                        : 'Your AI-generated quiz will appear here...'
                )}
            </div>
        </div>
    );
}
