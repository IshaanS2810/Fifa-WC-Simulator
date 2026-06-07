import { useState } from 'react';
import TeamSelect from '../components/TeamSelect';
import MatchResultCard from '../components/MatchResultCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { predictMatch } from '../services/api';
import '../styles/pages.css';

const teams = [
  'Argentina',
  'Brazil',
  'France',
  'England',
  'Spain',
  'Germany',
  'Portugal',
  'Netherlands',
  'Belgium',
  'Croatia',
  'Morocco',
  'Japan',
  'Mexico',
  'USA',
  'Uruguay'
];

function MatchPredictor() {
  const [homeTeam, setHomeTeam] = useState('Argentina');
  const [awayTeam, setAwayTeam] = useState('France');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam || homeTeam === awayTeam) {
      setError('Please choose two different teams to compare.');
      setResult(null);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await predictMatch(homeTeam, awayTeam);
      setResult(data);
    } catch (fetchError) {
      setError(fetchError.message || 'Prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  const getWinner = () => {
    if (!result?.outcome) return '';

    const {
      win_probability,
      draw_probability,
      loss_probability
    } = result.outcome;

    if (
      draw_probability >
      Math.max(win_probability, loss_probability)
    ) {
      return 'Draw';
    }

    return win_probability > loss_probability
      ? result.home_team
      : result.away_team;
  };

  const getResultText = () => {
    if (!result?.outcome) return '';

    const {
      win_probability,
      draw_probability,
      loss_probability
    } = result.outcome;

    if (
      draw_probability >
      Math.max(win_probability, loss_probability)
    ) {
      return 'Draw';
    }

    return win_probability > loss_probability
      ? `${result.home_team} Win`
      : `${result.away_team} Win`;
  };

  return (
    <section className="page-section">
      <div className="section-header">
        <div>
          <p className="eyebrow">Predictor</p>
          <h2>Match Prediction</h2>
          <p>
            Choose two teams, compare their chances,
            and discover which side is more likely to win.
          </p>
        </div>
      </div>

      <div className="form-panel">
        <div className="input-grid">
          <TeamSelect
            label="Home Team"
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
            teams={teams}
          />

          <TeamSelect
            label="Away Team"
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
            teams={teams}
          />
        </div>

        <button
          className="button button-primary"
          onClick={handlePredict}
          disabled={loading}
        >
          {loading ? 'Predicting...' : 'Predict Match'}
        </button>
      </div>

      {loading && <LoadingSpinner />}

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {result && result.outcome && (
        <div className="result-panel">
          <MatchResultCard
            homeTeam={result.home_team}
            awayTeam={result.away_team}
            probabilities={{
              home_win: result.outcome.win_probability,
              draw: result.outcome.draw_probability,
              away_win: result.outcome.loss_probability
            }}
            winner={getWinner()}
            result={getResultText()}
          />
        </div>
      )}
    </section>
  );
}

export default MatchPredictor;