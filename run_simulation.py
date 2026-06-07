from fifa_wc_simulator.models.predict_match import predict_match
from fifa_wc_simulator.simulation.tournament_engine import (
    run_tournament_2026
)
from fifa_wc_simulator.simulation.monte_carlo import (
    run_monte_carlo,
    print_monte_carlo_summary
)


def main():

    while True:

        print("\n===================================")
        print("FIFA WORLD CUP SIMULATOR")
        print("===================================")

        print("1. Predict Match")
        print("2. Simulate World Cup")
        print("3. Monte Carlo Forecast")
        print("4. Exit")

        choice = input("\nEnter choice: ")

        # -----------------------------------
        # MATCH PREDICTION
        # -----------------------------------

        if choice == "1":

            team1 = input("\nEnter Home Team: ")
            team2 = input("Enter Away Team: ")

            result = predict_match(
                team1,
                team2
            )

            print("\n===================================")
            print(f"{team1} vs {team2}")
            print("===================================\n")

            print(result)

        # -----------------------------------
        # WORLD CUP SIMULATION
        # -----------------------------------

        elif choice == "2":

            result = run_tournament_2026()

            print("\n===================================")
            print("WORLD CUP RESULTS")
            print("===================================\n")

            print(
                f"Champion   : "
                f"{result['champion']}"
            )

            print(
                f"Runner Up  : "
                f"{result['runner_up']}"
            )

            print(
                f"Third Place: "
                f"{result['third_place']}"
            )

        # -----------------------------------
        # MONTE CARLO
        # -----------------------------------

        elif choice == "3":

            iterations = int(
                input(
                    "\nNumber of simulations: "
                )
            )

            results = run_monte_carlo(
                iterations=iterations
            )

            print_monte_carlo_summary(
                results
            )

        # -----------------------------------
        # EXIT
        # -----------------------------------

        elif choice == "4":

            print("\nExiting simulator...")
            break

        else:

            print("\nInvalid choice.")


if __name__ == "__main__":

    main()