import { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/pages.css';
import '../styles/cards.css';
import { simulateTournament } from '../services/api';

function TournamentSimulator() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSimulate = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await simulateTournament();
      setResult(data);
    } catch (fetchError) {
      setError(fetchError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page-section">
      <div className="section-header">
        <div>
          <p className="eyebrow">Tournament</p>
          <h2>FIFA World Cup Simulator</h2>
          <p>Run a full tournament simulation and see the champion, runner-up, and third place team.</p>
        </div>
      </div>

      <div className="form-panel">
        <button className="button button-primary" onClick={handleSimulate} disabled={loading}>
          {loading ? 'Simulating...' : 'Simulate FIFA World Cup'}
        </button>
      </div>

      {loading && <LoadingSpinner />}

      {error && <div className="error-banner">{error}</div>}

      {result && (
        <div className="tournament-grid">
          <div className="tournament-card tournament-champion">
            <h3>Champion</h3>
            <p>{result.champion}</p>
          </div>
          <div className="tournament-card tournament-runner">
            <h3>Runner Up</h3>
            <p>{result.runner_up}</p>
          </div>
          <div className="tournament-card tournament-third">
            <h3>Third Place</h3>
            <p>{result.third_place}</p>
          </div>
        </div>
      )}
    </section>
  );
}

export default TournamentSimulator;
