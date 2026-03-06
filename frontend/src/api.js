/**
 * API helper — all backend communication in one place.
 */

const API_BASE = '/api';

/**
 * Upload a PDF file.
 * @param {File} file
 * @returns {Promise<{doc_id: string, filename: string, num_chunks: number, message: string}>}
 */
export async function uploadPDF(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
}

/**
 * List all uploaded documents.
 */
export async function listDocuments() {
    const res = await fetch(`${API_BASE}/documents`);
    return res.json();
}

/**
 * Delete a document.
 */
export async function deleteDocument(docId) {
    const res = await fetch(`${API_BASE}/documents/${docId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');
    return res.json();
}

/**
 * Ask a question (non-streaming).
 */
export async function askQuestion(docId, question) {
    const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId, question }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Chat failed');
    }
    return res.json();
}

/**
 * Ask a question with streaming (SSE).
 * @param {string} docId
 * @param {string} question
 * @param {(token: string) => void} onToken
 * @param {() => void} onDone
 */
export async function streamQuestion(docId, question, onToken, onDone) {
    const res = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId, question }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.token) onToken(data.token);
                    if (data.done) onDone?.();
                    if (data.error) throw new Error(data.error);
                } catch (e) {
                    if (e.message !== 'Unexpected end of JSON input') throw e;
                }
            }
        }
    }
    onDone?.();
}

/**
 * Generate a lesson.
 */
export async function generateLesson(docId, topic = '', difficulty = 'beginner') {
    const res = await fetch(`${API_BASE}/lesson`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId, topic, difficulty }),
    });
    if (!res.ok) throw new Error('Lesson generation failed');
    return res.json();
}

/**
 * Generate a quiz.
 */
export async function generateQuiz(docId, topic = '', numQuestions = 5, difficulty = 'beginner') {
    const res = await fetch(`${API_BASE}/quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId, topic, num_questions: numQuestions, difficulty }),
    });
    if (!res.ok) throw new Error('Quiz generation failed');
    return res.json();
}

/**
 * Health check.
 */
export async function healthCheck() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
}
