import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';
import '../styles/cards.css';

function ChampionChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Champion Probability Forecast</h3>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2f4f2f" />
          <XAxis dataKey="team" stroke="#ffffff" tick={{ fill: '#ffffff' }} />
          <YAxis stroke="#ffffff" tick={{ fill: '#ffffff' }} tickFormatter={(value) => `${value}%`} />
          <Tooltip formatter={(value) => `${value}%`} cursor={{ fill: 'rgba(255,255,255,0.08)' }} />
          <Bar dataKey="probability" fill="#2ecc71" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ChampionChart;
