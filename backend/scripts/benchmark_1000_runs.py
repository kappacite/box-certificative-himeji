import time
import sys
import random
import statistics
from typing import Dict
from app import create_app
from dao.models import PlaceModel
from dataobject.place import Place
from compare_algorithms import (
    generate_synthetic_places,
    calculate_tour_distance,
    ortools_optimize_bench,
    nn_2opt_optimize,
)


def run_1000_benchmarks():
    print("Initializing Flask App Context to fetch seeded places...")
    app = create_app("development")

    with app.app_context():
        place_models = PlaceModel.query.all()
        if not place_models:
            print(
                "Error: No places found in database. Run 'python seed_places.py' first."
            )
            sys.exit(1)

        all_places = [
            Place(
                id=pm.id,
                name=pm.name,
                latitude=pm.latitude,
                longitude=pm.longitude,
                owner_id=pm.owner_id,
                visibility=pm.visibility,
            )
            for pm in place_models
        ]

    # Generate synthetic places to reach 1000 locations
    all_places = generate_synthetic_places(all_places, 1000)

    num_runs = 1000
    results_n5 = []
    results_n10 = []

    print(f"Starting {num_runs} simulations for N=5 and N=10...")

    for i in range(1, num_runs + 1):
        if i % 100 == 0:
            print(f"-> Processing simulation {i}/{num_runs}...")

        # --- N = 5 ---
        random.seed(5000 + i)
        sample_n5 = random.sample(all_places, 5)

        # OR-Tools N=5
        t0 = time.perf_counter()
        tour_ort_5 = ortools_optimize_bench(sample_n5)
        time_ort_5 = (time.perf_counter() - t0) * 1000
        dist_ort_5 = calculate_tour_distance(tour_ort_5)

        # NN+2opt N=5
        t0 = time.perf_counter()
        tour_nn_5 = nn_2opt_optimize(sample_n5)
        time_nn_5 = (time.perf_counter() - t0) * 1000
        dist_nn_5 = calculate_tour_distance(tour_nn_5)

        results_n5.append(
            {
                "ort_dist": dist_ort_5,
                "ort_time": time_ort_5,
                "nn_dist": dist_nn_5,
                "nn_time": time_nn_5,
            }
        )

        # --- N = 10 ---
        random.seed(10000 + i)
        sample_n10 = random.sample(all_places, 10)

        # OR-Tools N=10
        t0 = time.perf_counter()
        tour_ort_10 = ortools_optimize_bench(sample_n10)
        time_ort_10 = (time.perf_counter() - t0) * 1000
        dist_ort_10 = calculate_tour_distance(tour_ort_10)

        # NN+2opt N=10
        t0 = time.perf_counter()
        tour_nn_10 = nn_2opt_optimize(sample_n10)
        time_nn_10 = (time.perf_counter() - t0) * 1000
        dist_nn_10 = calculate_tour_distance(tour_nn_10)

        results_n10.append(
            {
                "ort_dist": dist_ort_10,
                "ort_time": time_ort_10,
                "nn_dist": dist_nn_10,
                "nn_time": time_nn_10,
            }
        )

    # --- Analysis & Statistics Compilation ---
    def compile_stats(results_list) -> Dict:
        ort_dists = [r["ort_dist"] for r in results_list]
        ort_times = [r["ort_time"] for r in results_list]
        nn_dists = [r["nn_dist"] for r in results_list]
        nn_times = [r["nn_time"] for r in results_list]

        wins_ort = 0
        wins_nn = 0
        ties = 0

        for r in results_list:
            if r["ort_dist"] < r["nn_dist"] - 1e-4:
                wins_ort += 1
            elif r["nn_dist"] < r["ort_dist"] - 1e-4:
                wins_nn += 1
            else:
                ties += 1

        return {
            "avg_ort_dist": statistics.mean(ort_dists),
            "avg_nn_dist": statistics.mean(nn_dists),
            "avg_ort_time": statistics.mean(ort_times),
            "avg_nn_time": statistics.mean(nn_times),
            "min_ort_dist": min(ort_dists),
            "max_ort_dist": max(ort_dists),
            "min_nn_dist": min(nn_dists),
            "max_nn_dist": max(nn_dists),
            "min_ort_time": min(ort_times),
            "max_ort_time": max(ort_times),
            "min_nn_time": min(nn_times),
            "max_nn_time": max(nn_times),
            "wins_ort": wins_ort,
            "wins_nn": wins_nn,
            "ties": ties,
        }

    stats_n5 = compile_stats(results_n5)
    stats_n10 = compile_stats(results_n10)

    # --- Markdown Report Generation ---
    report_md = []
    report_md.append("# Rapport de Test de Robustesse Massif : 1000 Runs à N=5 et N=10")
    report_md.append("")
    report_md.append(
        "Ce rapport présente l'analyse statistique agrégée de 1000 simulations "
        "aléatoires et indépendantes pour de petites tailles d'itinéraires ($N=5$ "
        "et $N=10$). Il permet d'étudier le comportement d'OR-Tools (configuré "
        "avec `RegisterTransitMatrix` et `Christofides`) face à `NN+2-opt` à "
        "très petite échelle."
    )
    report_md.append("")

    def append_section_md(report_list, title, stats):
        avg_gain_pct = (
            (stats["avg_nn_dist"] - stats["avg_ort_dist"]) / stats["avg_nn_dist"]
        ) * 100

        report_list.append(f"## 📊 Résultats pour {title}")
        report_list.append("")
        report_list.append("- **Nombre de simulations** : 1000")
        report_list.append(
            f"- **Victoires OR-Tools (itinéraire plus court)** : **{stats['wins_ort']} / 1000**"
        )
        report_list.append(
            f"- **Victoires NN + 2-opt (itinéraire plus court)** : {stats['wins_nn']} / 1000"
        )
        report_list.append(f"- **Égalités strictes** : {stats['ties']} / 1000")
        report_list.append("")

        t_diff = stats["avg_ort_time"] - stats["avg_nn_time"]
        report_list.append(
            "| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |"
        )
        report_list.append("| :--- | :---: | :---: | :---: |")
        report_list.append(
            f"| **Distance Moyenne** | {stats['avg_ort_dist']:.2f} km | "
            f"{stats['avg_nn_dist']:.2f} km | OR-Tools réduit de {avg_gain_pct:.2f}% |"
        )
        report_list.append(
            f"| **Temps Moyen de Calcul** | {stats['avg_ort_time']:.2f} ms | "
            f"{stats['avg_nn_time']:.2f} ms | Différence de {t_diff:+.2f} ms |"
        )
        report_list.append(
            f"| **Distance Min / Max** | {stats['min_ort_dist']:.2f} / "
            f"{stats['max_ort_dist']:.2f} km | {stats['min_nn_dist']:.2f} / "
            f"{stats['max_nn_dist']:.2f} km | -"
        )
        report_list.append(
            f"| **Temps Min / Max** | {stats['min_ort_time']:.2f} / "
            f"{stats['max_ort_time']:.2f} ms | {stats['min_nn_time']:.2f} / "
            f"{stats['max_nn_time']:.2f} ms | -"
        )
        report_list.append("")

    append_section_md(report_md, "N = 5 lieux", stats_n5)
    append_section_md(report_md, "N = 10 lieux", stats_n10)

    # Observations
    gain_5 = (
        (stats_n5["avg_nn_dist"] - stats_n5["avg_ort_dist"]) / stats_n5["avg_nn_dist"]
    ) * 100
    gain_10 = (
        (stats_n10["avg_nn_dist"] - stats_n10["avg_ort_dist"])
        / stats_n10["avg_nn_dist"]
    ) * 100

    report_md.append("## 🔍 Analyse Comparative et Robustesse :")
    report_md.append("")
    report_md.append(
        f"- **Taux d'Égalités Élevé à N=5** : À $N=5$, il y a "
        f"**{stats_n5['ties'] / 10}%** d'égalités strictes entre les deux "
        f"algorithmes. À cette échelle, le nombre de permutations possibles "
        f"est très réduit ($5! = 120$) et les deux heuristiques trouvent "
        f"presque toujours le même chemin optimal."
    )
    report_md.append(
        f"- **Écart à N=10** : À $N=10$ ($10! \\approx 3.6$ millions de "
        f"permutations), les égalités chutent à **{stats_n10['ties'] / 10}%**. "
        f"OR-Tools gagne dans **{stats_n10['wins_ort'] / 10}%** des cas "
        f"(gain de {gain_10:.2f}% de distance en moyenne), ce qui montre que "
        f"même sur des problèmes de taille modeste, OR-Tools commence à faire "
        f"la différence."
    )
    report_md.append(
        f"- **Efficacité Temporelle** : Pour $N=5$, OR-Tools s'exécute en "
        f"moyenne en **{stats_n5['avg_ort_time']:.2f} ms** (contre "
        f"{stats_n5['avg_nn_time']:.2f} ms pour NN+2-opt). Pour $N=10$, il "
        f"met **{stats_n10['avg_ort_time']:.2f} ms** (contre "
        f"{stats_n10['avg_nn_time']:.2f} ms pour NN+2-opt). Ces temps sont "
        f"extrêmement faibles et garantissent une réactivité totale de l'API."
    )
    report_md.append("")

    filepath = "docs/benchmark_1000_runs.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(report_md) + "\n")

    # --- CLI Summary Print ---
    print("\n" + "=" * 100)
    print("SYNTHÈSE DES 1000 BENCHMARKS à N=5 et N=10")
    print("=" * 100)
    print(" Taille N=5 lieux :")
    print(
        f"   - Victoires OR-Tools : {stats_n5['wins_ort']}/1000 | "
        f"Victoires NN+2-opt : {stats_n5['wins_nn']}/1000 | "
        f"Égalités : {stats_n5['ties']}/1000"
    )
    print(
        f"   - Distance Moyenne   : OR-Tools: {stats_n5['avg_ort_dist']:.2f} km | "
        f"NN+2-opt: {stats_n5['avg_nn_dist']:.2f} km | "
        f"Gain: {gain_5:.2f}%"
    )
    print(
        f"   - Temps Moyen        : OR-Tools: {stats_n5['avg_ort_time']:.2f} ms | "
        f"NN+2-opt: {stats_n5['avg_nn_time']:.2f} ms"
    )
    print("-" * 100)
    print(" Taille N=10 lieux :")
    print(
        f"   - Victoires OR-Tools : {stats_n10['wins_ort']}/1000 | "
        f"Victoires NN+2-opt : {stats_n10['wins_nn']}/1000 | "
        f"Égalités : {stats_n10['ties']}/1000"
    )
    print(
        f"   - Distance Moyenne   : OR-Tools: {stats_n10['avg_ort_dist']:.2f} km | "
        f"NN+2-opt: {stats_n10['avg_nn_dist']:.2f} km | "
        f"Gain: {gain_10:.2f}%"
    )
    print(
        f"   - Temps Moyen        : OR-Tools: {stats_n10['avg_ort_time']:.2f} ms | "
        f"NN+2-opt: {stats_n10['avg_nn_time']:.2f} ms"
    )
    print("=" * 100 + "\n")
    print(f"Rapport complet généré dans : {filepath}")


if __name__ == "__main__":
    run_1000_benchmarks()
