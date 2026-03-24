from model import LondonCommuteModel

m = LondonCommuteModel(n_commuters=5000, seed=42)
m.step()

for i in range(16):
    m.step()
    print(f"Hour={m.current_hour:02d}:00  "
          f"Gini={m._accessibility_gini():.4f}  "
          f"Palma={m._accessibility_palma():.2f}  "
          f"Mean={m._mean_accessibility():.1f}  "
          f"Commute={m._mean_commute_time():.1f}min")