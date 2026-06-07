import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  }
});

export async function predictMatch(homeTeam, awayTeam) {
  try {

    const response = await api.post(
      '/api/simulate-match',
      {
        home_team: homeTeam,
        away_team: awayTeam
      }
    );

    return response.data;

  } catch (error) {

    console.error(error);

    const message =
      error?.response?.data?.detail ||
      error.message ||
      'Unable to predict match.';

    throw new Error(message);
  }
}

export async function simulateTournament() {
  try {
    const response = await api.post(
      '/api/simulate-tournament',
      {
        teams: [],
        seed: null
      }
    );

    return response.data;

  } catch (error) {

    console.error(error);

    const message =
      error?.response?.data?.detail ||
      error.message ||
      'Unable to simulate tournament.';

    throw new Error(message);
  }
}

export async function runMonteCarlo(iterations) {
  try {

    const response = await api.post(
      '/api/monte-carlo',
      {
        iterations
      }
    );

    return response.data;

  } catch (error) {

    console.error(error);

    const message =
      error?.response?.data?.detail ||
      error.message ||
      'Unable to run Monte Carlo simulation.';

    throw new Error(message);
  }
}