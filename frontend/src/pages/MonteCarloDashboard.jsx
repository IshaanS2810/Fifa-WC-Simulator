import { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ChampionChart from '../components/ChampionChart';
import { runMonteCarlo } from '../services/api';
import '../styles/pages.css';
import '../styles/cards.css';

function MonteCarloDashboard() {
  const [iterations, setIterations] = useState(100);
  const [probabilities, setProbabilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (iterations < 10) {
      setError('Please enter at least 10 iterations.');
      return;
    }

    setLoading(true);
    setError('');
    setSummary(null);

    try {
      const data = await runMonteCarlo(Number(iterations));
      const sorted = Object.entries(data.champion_probabilities || {})
        .map(([team, probability]) => ({ team, probability: Math.round(probability * 100) }))
        .sort((a, b) => b.probability - a.probability)
        .slice(0, 10);

      setProbabilities(sorted);
      setSummary({ iterations: data.iterations, champion: sorted[0]?.team || 'N/A' });
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
          <p className="eyebrow">Forecast</p>
          <h2>Monte Carlo Dashboard</h2>
          <p>Run multiple simulations to estimate champion probabilities for the top teams.</p>
        </div>
      </div>

      <div className="form-panel form-inline">
        <label htmlFor="iterations" className="input-label">
          Iterations
        </label>
        <input
          id="iterations"
          type="number"
          min="10"
          value={iterations}
          onChange={(e) => setIterations(e.target.value)}
          className="text-input"
        />
        <button className="button button-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Running...' : 'Run Simulation'}
        </button>
      </div>

      {loading && <LoadingSpinner />}
      {error && <div className="error-banner">{error}</div>}

      {summary && (
        <div className="summary-block">
          <p>Iterations: {summary.iterations}</p>
          <p>Top projected champion: {summary.champion}</p>
        </div>
      )}

      {probabilities.length > 0 ? (
        <ChampionChart data={probabilities} />
      ) : (
        !loading && <div className="empty-state">Run the simulation to display champion probabilities.</div>
      )}
    </section>
  );
}

export default MonteCarloDashboard;
