import logging
from pathlib import Path

from fifa_wc_simulator.models.predict_match import predict_match
from fifa_wc_simulator.models.team_lookup import list_team_names
from fifa_wc_simulator.preprocessing.validate_raw import validate_raw_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    """Entry point for the FIFA World Cup Simulator project."""
    logging.info("FIFA World Cup Simulator")
    base_path = Path(__file__).resolve().parent
    logging.info("Project root: %s", base_path)

    raw_ok, messages = validate_raw_datasets()
    for line in messages:
        logging.info(line)
    if not raw_ok:
        logging.error("Fix raw datasets before running simulations.")
        return

    teams = list_team_names()
    logging.info("Loaded %d teams from team_features.csv", len(teams))

    if len(teams) >= 2:
        sample = predict_match(teams[0], teams[1])
        logging.info(
            "Sample prediction (%s vs %s, source=%s): win=%.2f draw=%.2f loss=%.2f",
            teams[0],
            teams[1],
            sample.get("source"),
            sample["win_probability"],
            sample["draw_probability"],
            sample["loss_probability"],
        )


if __name__ == "__main__":
    main()
