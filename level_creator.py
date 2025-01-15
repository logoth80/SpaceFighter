import json
import random

enemy_list = []
meteor_list = []

for i in range(200):
    meteor_list.append({"t": 2000 + i * 4000, "y": random.randint(0, 20) * 5})

for wave in range(20):
    start_time = 5000 + wave * 25000  # Each wave starts 25 seconds apart
    enemy_type_in_wave = random.randint(1, 4)
    for i in range(7):  # 5 enemies per wave
        if random.random() >= 0.5:
            kind = None
        else:
            kind = random.choice(["weapon", "life", "invulnerability"])
        enemy_list.append(
            {
                "t": start_time + i * 1000,  # Spawn each enemy 1 second apart
                "y": random.randint(2, 18) * 5,
                "hp": 3,
                "k": enemy_type_in_wave,
                "w": 1,
                "b": kind,
            }
        )

# Assuming enemy_list is already created as in your code
with open("l1.json", "w") as f:
    for enemy in enemy_list:
        f.write(json.dumps(enemy) + "\n")

with open("l1m.json", "w") as f:
    for meteor in meteor_list:
        f.write(json.dumps(meteor) + "\n")
