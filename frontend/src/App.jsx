import { useState } from "react";
import "./App.css";


function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [repositoryId, setRepositoryId] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [answer, setAnswer] = useState("");

  const quickQueries = [
    {
      icon: "◈",
      text: "Explain the architecture",
      value: "Explain the architecture of this project.",
    },
    {
      icon: "🐞",
      text: "Find potential bugs",
      value: "Find potential bugs in this project.",
    },
    {
      icon: "🛡",
      text: "Check security issues",
      value: "Check this project for security vulnerabilities.",
    },
    {
      icon: "</>",
      text: "Review code quality",
      value: "Review the code quality of this project.",
    },
    {
      icon: "⚗",
      text: "Find functions needing tests",
      value: "Find functions that need unit tests.",
    },
  ];

   // File upload handler
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) {
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".zip")) {
      setError("Please select a ZIP file.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setRepositoryId(null);
    setResults([]);
    setError("");
  };

  const handleAnalyze = async () => {
  if (!file) {
    alert("Please upload your repository first.");
    return;
  }

  if (!query.trim()) {
    alert("Please enter your question.");
    return;
  }

  setLoading(true);
  setError("");

  try {
    let currentRepositoryId = repositoryId;

    /*
     * Upload and index only if we don't
     * already have a repository ID.
     */

    if (!currentRepositoryId) {

      const formData = new FormData();

      formData.append(
        "file",
        file
      );

      const uploadResponse = await fetch(
        "http://127.0.0.1:8000/api/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const uploadData =
        await uploadResponse.json();

      if (!uploadResponse.ok) {

        throw new Error(
          uploadData.detail ||
          "Repository upload failed."
        );
      }

      currentRepositoryId =
        uploadData.repository_id;

      setRepositoryId(
        currentRepositoryId
      );

      console.log(
        "Repository indexed:",
        uploadData
      );
    }

    /*
     * Query ChromaDB
     */

    const queryResponse = await fetch(
      "http://127.0.0.1:8000/api/rag/query",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          repository_id:
            currentRepositoryId,

          question:
            query,

          top_k: 5,
        }),
      }
    );

    const queryData =
      await queryResponse.json();
      setAnswer(
      queryData.answer || ""
      );

      setResults(
      queryData.results || []
      );

    if (!queryResponse.ok) {

      throw new Error(
        queryData.detail ||
        "RAG query failed."
      );
    }

    setResults(
      queryData.results || []
    );

    console.log(
      "Retrieved chunks:",
      queryData.results
    );

  } catch (err) {

    console.error(err);

    setError(
      err.message ||
      "Something went wrong."
    );

  } finally {

    setLoading(false);
  }
};

  return (
    <div className="app">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-logo">
            &lt;/&gt;
          </div>

          <div>
            <h2>
              AI Codebase <span>Intelligence</span>
            </h2>

            <p>Understand. Analyze. Improve.</p>
          </div>
        </div>

        <nav className="sidebar-nav">

          <a className="nav-item active">
            <span>⌂</span>
            Home
          </a>

          <a className="nav-item">
            <span>▣</span>
            Repositories
          </a>

          <a className="nav-item">
            <span>◴</span>
            Analysis History
          </a>

          <a className="nav-item">
            <span>◈</span>
            Code Review
          </a>

          <a className="nav-item">
            <span>♢</span>
            Security Scan
          </a>

          <a className="nav-item">
            <span>◉</span>
            AI Chat
          </a>

          <a className="nav-item">
            <span>⚙</span>
            Settings
          </a>

        </nav>

        {/* System status */}

        <div className="system-status">

          <div className="status-title">
            SYSTEM STATUS
          </div>

          <div className="system-online">
            <span className="online-dot"></span>
            All Systems Operational
          </div>

          <div className="status-card">

            <div className="status-row">
              <div className="status-icon purple">
                ✦
              </div>

              <div>
                <span>AI Engine</span>
                <small>Online</small>
              </div>

              <b className="green-dot"></b>
            </div>

            <div className="status-row">
              <div className="status-icon blue">
                ≋
              </div>

              <div>
                <span>Vector Database</span>
                <small>Connected</small>
              </div>
            </div>

            <div className="status-row">
              <div className="status-icon green">
                ◈
              </div>

              <div>
                <span>Security Scanner</span>
                <small>Ready</small>
              </div>
            </div>

          </div>

        </div>

      </aside>

      {/* ================= MAIN ================= */}

      <main className="main">

        {/* Top bar */}

        <header className="topbar">

          <div className="breadcrumb">
            Workspace / Home
          </div>

          <div className="top-actions">

            <button className="icon-button">
              ☾
            </button>

            <button className="icon-button notification">
              ♧
              <span>3</span>
            </button>

            <button className="new-analysis">
              ✦ New Analysis
            </button>

            <div className="avatar">
              AI
            </div>

          </div>

        </header>

        {/* ================= HERO ================= */}

        <section className="hero">

          <div className="hero-content">

            <div className="hero-badge">
              <span>⚡</span>
              RAG-POWERED CODE INTELLIGENCE
            </div>

            <h1>
              Understand your
              <br />
              <strong>entire codebase</strong>
              <br />
              with AI
            </h1>

            <p>
              Upload your repository and let AI analyze, explain,
              review, find bugs and answer anything about your code.
            </p>

            <div className="hero-buttons">

              <button
                className="primary-button"
                onClick={() =>
                  document.getElementById("repository-upload").click()
                }
              >
                ↑ Upload Repository
              </button>

              <button className="secondary-button">
                ▶ Try Demo
              </button>

            </div>

          </div>

          <div className="hero-visual">

            <div className="code-laptop">

              <div className="laptop-screen">

                <div className="code-line purple-line"></div>
                <div className="code-line blue-line"></div>
                <div className="code-line green-line"></div>
                <div className="code-line purple-line small"></div>
                <div className="code-line blue-line"></div>
                <div className="code-line green-line small"></div>

              </div>

              <div className="laptop-base"></div>

            </div>

            <div className="floating-icon github">
              ◉
            </div>

            <div className="floating-icon react">
              ⚛
            </div>

            <div className="floating-icon node">
              JS
            </div>

            <div className="floating-icon terminal">
              &gt;_
            </div>

          </div>

        </section>

        {/* ================= STATS ================= */}

        <section className="stats">

          <Stat
            icon="◉"
            value="Code RAG"
            label="Semantic Retrieval"
          />

          <Stat
            icon="⚡"
            value="AST"
            label="Code Understanding"
          />

          <Stat
            icon="◈"
            value="Reranking"
            label="Better Context"
          />

          <Stat
            icon="◷"
            value="Local LLM"
            label="Privacy Focused"
          />

          <Stat
            icon="✦"
            value="AI Agents"
            label="Intelligent Analysis"
          />

        </section>

        {/* ================= WORKSPACE ================= */}

        <section className="workspace">

          <div className="workspace-left">

            {/* Tabs */}

            <div className="workspace-tabs">

              <button className="workspace-tab active">
                ↑ Repository Upload
              </button>

              <button className="workspace-tab">
                💬 AI Chat
              </button>

              <button className="workspace-tab">
                &lt;/&gt; Code Review
              </button>

              <button className="workspace-tab">
                🛡 Security
              </button>

            </div>

            <div className="workspace-content">

              {/* Upload */}

              <div className="upload-section">

                <label
                  className="upload-box"
                  htmlFor="repository-upload"
                >

                  <input
                    id="repository-upload"
                    type="file"
                    accept=".zip"
                    onChange={handleFileChange}
                  />

                  <div className="upload-icon-large">
                    ↑
                  </div>

                  {file ? (
                    <>
                      <h3>{file.name}</h3>
                      <p className="file-success">
                        ✓ Repository selected
                      </p>
                    </>
                  ) : (
                    <>
                      <h3>
                        Drag & Drop your repository ZIP
                      </h3>

                      <p>
                        or click to browse files
                      </p>
                    </>
                  )}

                  <small>
                    Supports .zip files up to 500MB
                  </small>

                </label>

              </div>

              {/* Quick queries */}

              <div className="quick-query-section">

                <h3>Quick Queries</h3>

                <p>
                  Start analyzing your repository
                </p>

                <div className="quick-query-list">

                  {quickQueries.map((item) => (
                    <button
                      key={item.text}
                      className="quick-query"
                      onClick={() => setQuery(item.value)}
                    >

                      <span className="query-icon">
                        {item.icon}
                      </span>

                      <span>
                        {item.text}
                      </span>

                      <b>›</b>

                    </button>
                  ))}

                </div>

              </div>

            </div>

            {/* Chat input */}

            <div className="chat-input-container">

              <span className="sparkle">
                ✦
              </span>

              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask anything about your codebase..."
              />

              <button onClick={handleAnalyze}>
                ✦ Ask AI
              </button>

            </div>

          </div>

          {/* ================= AI INSIGHTS ================= */}

          <aside className="insights">

            <div className="insights-header">

              <div>
                <span className="brain-icon">
                  ◈
                </span>

                <h2>AI Insights</h2>
              </div>

              <span className="live">
                ● Live
              </span>

            </div>

            {/* Health */}

            <div className="health-card">

              <div className="health-score">
                92
              </div>

              <div>
                <h3>Code Health</h3>
                <strong>Excellent</strong>
              </div>

            </div>

            <div className="issue-summary">

              <div>
                <span>✓</span>
                12 Issues Found
              </div>

              <div>
                <span>✓</span>
                4 Security Alerts
              </div>

              <div>
                <span>✓</span>
                8 Quality Warnings
              </div>

            </div>

            <h3 className="top-insights-title">
              Top Insights
            </h3>

            <Insight
              icon="🛡"
              title="Security"
              text="2 potential vulnerabilities in authentication module"
              type="security"
            />

            <Insight
              icon="&lt;/&gt;"
              title="Code Quality"
              text="Low test coverage in 3 components"
              type="quality"
            />

            <Insight
              icon="⚡"
              title="Performance"
              text="Inefficient database queries detected"
              type="performance"
            />

          </aside>

        </section>

        {/* ================= RAG RESULTS ================= */}
        <RAGResults
          results={results}
          loading={loading}
          error={error}
          answer={answer}
        />

        {/* ================= FEATURES ================= */}

        <section className="feature-grid">

          <Feature
            icon="◈"
            title="Code RAG Search"
            description="Find relevant code with semantic understanding."
            color="purple"
          />

          <Feature
            icon="🛡"
            title="Security Analysis"
            description="Detect vulnerabilities and security risks."
            color="green"
          />

          <Feature
            icon="&lt;/&gt;"
            title="AI Code Review"
            description="Get intelligent feedback and suggestions."
            color="blue"
          />

          <Feature
            icon="🚀"
            title="Smart Developer"
            description="Save time and code with confidence."
            color="orange"
          />

        </section>

        {/* ================= TECH STACK ================= */}



        {/* Footer */}

        <footer>
          <span>
            © 2026 AI Codebase Intelligence
          </span>

          <div>
            <a>Privacy</a>
            <a>Terms</a>
            <a>Documentation</a>
            <a>GitHub</a>
          </div>
        </footer>

      </main>

    </div>
  );
}


/* ================= RAG RESULTS ================= */

function RAGResults({ results, loading, error, answer }) {
  if (loading) {
    return (
      <section className="rag-results">
        <div className="rag-status">
          <span className="loader"></span>
          Analyzing your codebase...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rag-results">
        <div className="rag-error">❌ {error}</div>
      </section>
    );
  }

  if (!answer && (!results || results.length === 0)) {
    return null;
  }

  return (
    <section className="rag-results">
      {answer && (
        <div className="ai-answer">
          <div className="answer-header">
            <span className="results-badge">AI ANALYSIS</span>
            <h2>AI Answer</h2>
          </div>
          <div className="answer-content">{answer}</div>
        </div>
      )}

      {results && results.length > 0 && (
        <>
          <div className="results-header">
            <div>
              <span className="results-badge">RAG RESULTS</span>
              <h2>Relevant Code</h2>
            </div>
            <span>{results.length} sources</span>
          </div>

          {results.map((result, index) => (
            <div className="result-card" key={`${result.file_path}-${index}`}>
              <div className="result-top">
                <div>
                  <strong>{result.file_path}</strong>
                  <span>Lines {result.start_line}-{result.end_line}</span>
                </div>
                <span className="result-number">#{index + 1}</span>
              </div>

              <pre>
                <code>{result.text}</code>
              </pre>
            </div>
          ))}
        </>
      )}
    </section>
  );
}


/* ================= COMPONENTS ================= */

function Stat({ icon, value, label }) {
  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <strong>{value}</strong>
        <span>{label}</span>
      </div>

    </div>
  );
}


function Insight({
  icon,
  title,
  text,
  type,
}) {
  return (
    <div className={`insight-item ${type}`}>

      <div className="insight-icon">
        {icon}
      </div>

      <div>
        <h4>{title}</h4>
        <p>{text}</p>
      </div>

      <span className="arrow">
        ›
      </span>

    </div>
  );
}


function Feature({
  icon,
  title,
  description,
  color,
}) {
  return (
    <div className={`feature-card ${color}`}>

      <div className="feature-icon">
        {icon}
      </div>

      <div>
        <h3>{title}</h3>
        <p>{description}</p>
        <a>Learn More →</a>
      </div>

    </div>
  );
}


function Tech({ name, icon }) {
  return (
    <div className="tech">

      <span>
        {icon}
      </span>

      <small>
        {name}
      </small>

    </div>
  );
}

export default App;