import '../styles/cards.css';

function MatchResultCard({
  homeTeam,
  awayTeam,
  probabilities = {},
  winner,
  result
}) {

  return (
    <div className="result-card">
      <div className="result-header">
        <div>
          <h3>{homeTeam} vs {awayTeam}</h3>
          <p className="result-subtitle">Predicted result: {result}</p>
        </div>
        <div className="winner-pill">Winner: {winner}</div>
      </div>
      <div className="probability-grid">
        {stats.map((stat) => (
          <div key={stat.label} className="probability-row">
            <div className="probability-label">
              {stat.label}
              <span>{Math.round(stat.value * 100)}%</span>
            </div>
            <div className="meter">
              <div className="meter-fill" style={{ width: `${stat.value * 100}%`, backgroundColor: stat.color }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MatchResultCard;
