function TeamSelect({ label, value, onChange, teams }) {
  return (
    <div className="form-group">
      <label htmlFor={label} className="input-label">
        {label}
      </label>
      <select id={label} value={value} onChange={onChange} className="select-control">
        <option value="">Select a team</option>
        {teams.map((team) => (
          <option key={team} value={team}>
            {team}
          </option>
        ))}
      </select>
    </div>
  );
}

export default TeamSelect;
