import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import MatchPredictor from './pages/MatchPredictor';
import TournamentSimulator from './pages/TournamentSimulator';
import MonteCarloDashboard from './pages/MonteCarloDashboard';
import './styles/pages.css';

function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="page-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/predict" element={<MatchPredictor />} />
          <Route path="/tournament" element={<TournamentSimulator />} />
          <Route path="/monte-carlo" element={<MonteCarloDashboard />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
