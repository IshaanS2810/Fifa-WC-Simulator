import { NavLink } from 'react-router-dom';
import '../styles/navbar.css';

function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-brand">FIFA World Cup Simulator</div>
      <nav className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Home
        </NavLink>
        <NavLink to="/predict" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Match Predictor
        </NavLink>
        <NavLink to="/tournament" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Tournament Simulator
        </NavLink>
        <NavLink to="/monte-carlo" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Monte Carlo
        </NavLink>
      </nav>
    </header>
  );
}

export default Navbar;
