import tkinter as tk
from tkinter import filedialog, IntVar, BooleanVar, StringVar
import json

def submit():
    params = {
        "Distributions Parameters": {
            "Order generation IAT mean": iat_mean.get(),
            "Service time mean": service_mean.get(),
            "Duration mean": duration_mean.get(),
            "Duration sigma": duration_sigma.get(),
            "Volume mean": volume_mean.get(),
            "Volume sigma": volume_sigma.get(),
            "Venue-related parameters": venue_params_file.get()
        },
        "Simulation & KPI-related Settings": {
            "Simulation time": sim_time.get(),
            "Energy consumption per second": energy_per_sec.get(),
            "Energy consumption per meter": energy_per_meter.get(),
            "Random Seed": random_seed.get(),
            "Batch run": batch_run.get(),
            "Run it for": run_times.get() if batch_run.get() else None,
            "Output file": output_file.get()
        },
        "Behavioral Settings": {
            "Number of Type 1 Truck": type1_trucks.get(),
            "Number of Type 2 Truck": type2_trucks.get(),
            "Number of Type 3 Truck": type3_trucks.get(),
            "Number of Type 4 Truck": type4_trucks.get(),
            "Map": map_file.get(),
            "Start delivery threshold": start_threshold.get(),
            "Maximum waiting time": max_waiting.get(),
            "Truck parameters": truck_params_file.get()
        },
        "Visualization Settings": {
            "Real-time dashboard": real_time_dashboard.get(),
            "Real-time process visualization": real_time_visualization.get()
        }
    }
    print(json.dumps(params, indent=4))
    root.destroy()

def toggle_batch_run():
    if batch_run.get():
        run_times_label.grid(row=13, column=1, sticky='w')
        run_times_entry.grid(row=13, column=2)
    else:
        run_times_label.grid_forget()
        run_times_entry.grid_forget()

root = tk.Tk()
root.title("Simulation Parameters")

def create_section(title, row):
    tk.Label(root, text=title, font=("Helvetica", 16)).grid(row=row, column=0, columnspan=3, sticky='w')
    tk.Canvas(root, height=2, bd=0, highlightthickness=0, bg="#d3d3d3").grid(row=row+1, column=0, columnspan=3, sticky='we')

# Distributions Parameters
create_section("Distributions Parameters", 0)
tk.Label(root, text="Order generation IAT mean (minutes):", anchor="w").grid(row=2, column=0, sticky='w')
iat_mean = tk.DoubleVar()
tk.Entry(root, textvariable=iat_mean).grid(row=2, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Service time mean (minutes):", anchor="w").grid(row=3, column=0, sticky='w')
service_mean = tk.DoubleVar()
tk.Entry(root, textvariable=service_mean).grid(row=3, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Duration mean (minutes):", anchor="w").grid(row=4, column=0, sticky='w')
duration_mean = tk.DoubleVar()
tk.Entry(root, textvariable=duration_mean).grid(row=4, column=1, sticky='w')
tk.Label(root, text="sigma:", anchor="w").grid(row=4, column=2, sticky='w')
duration_sigma = tk.DoubleVar()
tk.Entry(root, textvariable=duration_sigma).grid(row=4, column=3, sticky='w')

tk.Label(root, text="Volume mean (minutes):", anchor="w").grid(row=5, column=0, sticky='w')
volume_mean = tk.DoubleVar()
tk.Entry(root, textvariable=volume_mean).grid(row=5, column=1, sticky='w')
tk.Label(root, text="sigma:", anchor="w").grid(row=5, column=2, sticky='w')
volume_sigma = tk.DoubleVar()
tk.Entry(root, textvariable=volume_sigma).grid(row=5, column=3, sticky='w')

tk.Label(root, text="Venue-related parameters file:", anchor="w").grid(row=6, column=0, sticky='w')
venue_params_file = StringVar()
tk.Entry(root, textvariable=venue_params_file).grid(row=6, column=1, sticky='w')
tk.Button(root, text="Browse", command=lambda: venue_params_file.set(filedialog.askopenfilename())).grid(row=6, column=2)

# Simulation & KPI-related Settings
create_section("Simulation & KPI-related Settings", 7)
tk.Label(root, text="Simulation time (hours):", anchor="w").grid(row=9, column=0, sticky='w')
sim_time = tk.DoubleVar()
tk.Entry(root, textvariable=sim_time).grid(row=9, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Energy consumption per second (kWh/s):", anchor="w").grid(row=10, column=0, sticky='w')
energy_per_sec = tk.DoubleVar()
tk.Entry(root, textvariable=energy_per_sec).grid(row=10, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Energy consumption per meter (kWh/m):", anchor="w").grid(row=11, column=0, sticky='w')
energy_per_meter = tk.DoubleVar()
tk.Entry(root, textvariable=energy_per_meter).grid(row=11, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Random Seed:", anchor="w").grid(row=12, column=0, sticky='w')
random_seed = tk.IntVar()
tk.Entry(root, textvariable=random_seed).grid(row=12, column=1, columnspan=2, sticky='w')

batch_run = BooleanVar()
tk.Checkbutton(root, text="Batch run?", variable=batch_run, command=toggle_batch_run).grid(row=13, column=0, sticky='w')
run_times_label = tk.Label(root, text="Run it for (times):", anchor="w")
run_times = tk.IntVar()
run_times_entry = tk.Entry(root, textvariable=run_times)

tk.Label(root, text="Output file:", anchor="w").grid(row=14, column=0, sticky='w')
output_file = StringVar()
tk.Entry(root, textvariable=output_file).grid(row=14, column=1, sticky='w')
tk.Button(root, text="Browse", command=lambda: output_file.set(filedialog.asksaveasfilename(defaultextension=".csv"))).grid(row=14, column=2)

# Behavioral Settings
create_section("Behavioral Settings", 15)
tk.Label(root, text="Number of Type 1 Truck:", anchor="w").grid(row=17, column=0, sticky='w')
type1_trucks = tk.IntVar()
tk.Entry(root, textvariable=type1_trucks).grid(row=17, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Number of Type 2 Truck:", anchor="w").grid(row=18, column=0, sticky='w')
type2_trucks = tk.IntVar()
tk.Entry(root, textvariable=type2_trucks).grid(row=18, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Number of Type 3 Truck:", anchor="w").grid(row=19, column=0, sticky='w')
type3_trucks = tk.IntVar()
tk.Entry(root, textvariable=type3_trucks).grid(row=19, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Number of Type 4 Truck:", anchor="w").grid(row=20, column=0, sticky='w')
type4_trucks = tk.IntVar()
tk.Entry(root, textvariable=type4_trucks).grid(row=20, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Map file:", anchor="w").grid(row=21, column=0, sticky='w')
map_file = StringVar()
tk.Entry(root, textvariable=map_file).grid(row=21, column=1, sticky='w')
tk.Button(root, text="Browse", command=lambda: map_file.set(filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")]))).grid(row=21, column=2)

tk.Label(root, text="Start delivery threshold (volume unit):", anchor="w").grid(row=22, column=0, sticky='w')
start_threshold = tk.DoubleVar()
tk.Entry(root, textvariable=start_threshold).grid(row=22, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Maximum waiting time (minutes):", anchor="w").grid(row=23, column=0, sticky='w')
max_waiting = tk.DoubleVar()
tk.Entry(root, textvariable=max_waiting).grid(row=23, column=1, columnspan=2, sticky='w')

tk.Label(root, text="Truck parameters file:", anchor="w").grid(row=24, column=0, sticky='w')
truck_params_file = StringVar()
tk.Entry(root, textvariable=truck_params_file).grid(row=24, column=1, sticky='w')
tk.Button(root, text="Browse", command=lambda: truck_params_file.set(filedialog.askopenfilename())).grid(row=24, column=2)

# Visualization Settings
create_section("Visualization Settings", 25)
real_time_dashboard = BooleanVar()
tk.Checkbutton(root, text="Real-time dashboard", variable=real_time_dashboard).grid(row=27, column=0, sticky='w')

real_time_visualization = BooleanVar()
tk.Checkbutton(root, text="Real-time process visualization", variable=real_time_visualization).grid(row=27, column=1, sticky='w')

# Submit Button
tk.Button(root, text="Submit", command=submit).grid(row=28, column=0, columnspan=3)

root.mainloop()
