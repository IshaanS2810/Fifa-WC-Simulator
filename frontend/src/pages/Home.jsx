import { useNavigate } from 'react-router-dom';
import '../styles/pages.css';

function Home() {
  const navigate = useNavigate();

  return (
    <section className="home-page">
      <div className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Football prediction studio</p>
          <h1>FIFA World Cup Simulator</h1>
          <p className="hero-description">
            AI-powered football match prediction and tournament simulation platform.
            Explore head-to-head forecasts, full cup runs, and Monte Carlo championship probabilities.
          </p>
          <div className="hero-actions">
            <button className="button button-primary" onClick={() => navigate('/predict')}>
              Predict Match
            </button>
            <button className="button button-secondary" onClick={() => navigate('/tournament')}>
              Simulate Tournament
            </button>
            <button className="button button-outline" onClick={() => navigate('/monte-carlo')}>
              Monte Carlo Forecast
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-card">
            <div className="hero-stat">
              <span className="hero-number">92%</span>
              <span className="hero-label">Prediction Confidence</span>
            </div>
            <div className="hero-stat">
              <span className="hero-number">32 Teams</span>
              <span className="hero-label">Global powerhouses</span>
            </div>
            <div className="hero-stat">
              <span className="hero-number">1 Goal</span>
              <span className="hero-label">Clear tournament vision</span>
            </div>
          </div>
        </div>
      </div>
      <div className="feature-grid">
        <article className="feature-card">
          <h2>Match Predictor</h2>
          <p>Compare top nations, check win/draw/away probabilities, and discover the predicted winner.</p>
        </article>
        <article className="feature-card">
          <h2>Tournament Simulator</h2>
          <p>Run a full FIFA World Cup simulation and display the champion, runner up, and third place finishers.</p>
        </article>
        <article className="feature-card">
          <h2>Monte Carlo Forecast</h2>
          <p>Quantify champion chances through Monte Carlo analysis and surface the top title contenders.</p>
        </article>
      </div>
    </section>
  );
}

export default Home;
