import tkinter as tk
from tkinter import filedialog, IntVar, BooleanVar, StringVar, DoubleVar, messagebox
import json

def get_simulation_params():
    params = {}

    def submit():
        nonlocal params
        # 检查空字段
        missing_fields = []
        if not iat_mean.get():
            missing_fields.append("Order generation IAT mean")
        if not service_mean.get():
            missing_fields.append("Service time mean")
        if not duration_mean.get():
            missing_fields.append("Event Duration Shift mean")
        if not duration_sigma.get():
            missing_fields.append("Event Duration Shift sigma")
        if not volume_mean.get():
            missing_fields.append("Volume mean")
        if not volume_sigma.get():
            missing_fields.append("Volume sigma")
        if not venue_params_file.get():
            missing_fields.append("Venue-related parameters")
        if not sim_time.get():
            missing_fields.append("Simulation time")
        if not random_seed.get():
            missing_fields.append("Random Seed")
        if not output_file.get():
            missing_fields.append("Output file")
        if not ritsch_trucks.get():
            missing_fields.append("Number of Ritsch Truck")
        if not dongfeng_trucks.get():
            missing_fields.append("Number of Dongfeng Truck")
        if not isuzu_trucks.get():
            missing_fields.append("Number of Isuzu Truck")
        if not volvo_trucks.get():
            missing_fields.append("Number of Volvo Truck")
        if not map_file.get():
            missing_fields.append("Map")
        if not start_threshold.get():
            missing_fields.append("Start delivery threshold")
        if not max_waiting.get():
            missing_fields.append("Maximum waiting time")
        if not speed_motorway.get():
            missing_fields.append("Speed on Motorway")
        if not speed_city_street.get():
            missing_fields.append("Speed on City Street")
        if not truck_params_file.get():
            missing_fields.append("Truck parameters")

        if missing_fields:
            messagebox.showwarning("Missing Fields", "Please fill the following fields:\n" + "\n".join(missing_fields))
            return

        params = {
            "Distributions Parameters": {
                "Order generation IAT mean": iat_mean.get(),
                "Service time mean": service_mean.get(),
                "Event Duration Shift mean": duration_mean.get(),
                "Event Duration Shift sigma": duration_sigma.get(),
                "Volume mean": volume_mean.get(),
                "Volume sigma": volume_sigma.get(),
                "Venue-related parameters": venue_params_file.get()
            },
            "Simulation & KPI-related Settings": {
                "Simulation time": sim_time.get(),
                "Random Seed": random_seed.get(),
                "Batch run": batch_run.get(),
                "Run it for": run_times.get() if batch_run.get() else None,
                "Output file": output_file.get()
            },
            "Behavioral Settings": {
                "Number of Ritsch Truck": ritsch_trucks.get(),
                "Number of Dongfeng Truck": dongfeng_trucks.get(),
                "Number of Isuzu Truck": isuzu_trucks.get(),
                "Number of Volvo Truck": volvo_trucks.get(),
                "Map": map_file.get(),
                "Start delivery threshold": start_threshold.get(),
                "Maximum waiting time": max_waiting.get(),
                "Speed on Motorway": speed_motorway.get(),
                "Speed on City Street": speed_city_street.get(),
                "Truck parameters": truck_params_file.get()
            },
            "Visualization Settings": {
                "Real-time dashboard": real_time_dashboard.get(),
                "Real-time process visualization": real_time_visualization.get()
            }
        }
        root.destroy()

    def toggle_batch_run():
        if batch_run.get():
            batch_run_label.config(text="Run it for (times):")
            run_times_entry.grid(row=13, column=1, columnspan=2, sticky='w')
        else:
            batch_run_label.config(text="Batch run?")
            run_times_entry.grid_forget()

    def load_defaults():
        with open('default_params.json', 'r') as file:
            defaults = json.load(file)
        
        iat_mean.set(defaults["Distributions Parameters"]["Order generation IAT mean"])
        service_mean.set(defaults["Distributions Parameters"]["Service time mean"])
        duration_mean.set(defaults["Distributions Parameters"]["Event Duration Shift mean"])
        duration_sigma.set(defaults["Distributions Parameters"]["Event Duration Shift sigma"])
        volume_mean.set(defaults["Distributions Parameters"]["Volume mean"])
        volume_sigma.set(defaults["Distributions Parameters"]["Volume sigma"])
        venue_params_file.set(defaults["Distributions Parameters"]["Venue-related parameters"])

        sim_time.set(defaults["Simulation & KPI-related Settings"]["Simulation time"])
        random_seed.set(defaults["Simulation & KPI-related Settings"]["Random Seed"])
        batch_run.set(defaults["Simulation & KPI-related Settings"]["Batch run"])
        if defaults["Simulation & KPI-related Settings"]["Batch run"]:
            run_times.set(defaults["Simulation & KPI-related Settings"]["Run it for"])
            batch_run_label.config(text="Run it for (times):")
            run_times_entry.grid(row=13, column=1, columnspan=2, sticky='w')
        else:
            batch_run_label.config(text="Batch run?")
            run_times_entry.grid_forget()
        output_file.set(defaults["Simulation & KPI-related Settings"]["Output file"])

        ritsch_trucks.set(defaults["Behavioral Settings"]["Number of Ritsch Truck"])
        dongfeng_trucks.set(defaults["Behavioral Settings"]["Number of Dongfeng Truck"])
        isuzu_trucks.set(defaults["Behavioral Settings"]["Number of Isuzu Truck"])
        volvo_trucks.set(defaults["Behavioral Settings"]["Number of Volvo Truck"])
        map_file.set(defaults["Behavioral Settings"]["Map"])
        start_threshold.set(defaults["Behavioral Settings"]["Start delivery threshold"])
        max_waiting.set(defaults["Behavioral Settings"]["Maximum waiting time"])
        speed_motorway.set(defaults["Behavioral Settings"]["Speed on Motorway"])
        speed_city_street.set(defaults["Behavioral Settings"]["Speed on City Street"])
        truck_params_file.set(defaults["Behavioral Settings"]["Truck parameters"])

        real_time_dashboard.set(defaults["Visualization Settings"]["Real-time dashboard"])
        real_time_visualization.set(defaults["Visualization Settings"]["Real-time process visualization"])

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

    tk.Label(root, text="Event Duration Shift mean (hours):", anchor="w").grid(row=4, column=0, sticky='w')
    duration_mean = tk.DoubleVar()
    tk.Entry(root, textvariable=duration_mean, width=10).grid(row=4, column=1, sticky='w')
    tk.Label(root, text="sigma:", anchor="w").grid(row=4, column=2, sticky='w')
    duration_sigma = tk.DoubleVar()
    tk.Entry(root, textvariable=duration_sigma, width=10).grid(row=4, column=3, sticky='w')

    tk.Label(root, text="Volume mean (minutes):", anchor="w").grid(row=5, column=0, sticky='w')
    volume_mean = tk.DoubleVar()
    tk.Entry(root, textvariable=volume_mean, width=10).grid(row=5, column=1, sticky='w')
    tk.Label(root, text="sigma:", anchor="w").grid(row=5, column=2, sticky='w')
    volume_sigma = tk.DoubleVar()
    tk.Entry(root, textvariable=volume_sigma, width=10).grid(row=5, column=3, sticky='w')

    tk.Label(root, text="Venue-related parameters file:", anchor="w").grid(row=6, column=0, sticky='w')
    venue_params_file = StringVar()
    tk.Entry(root, textvariable=venue_params_file).grid(row=6, column=1, sticky='w')
    tk.Button(root, text="Browse", command=lambda: venue_params_file.set(filedialog.askopenfilename())).grid(row=6, column=2)

    # Simulation & KPI-related Settings
    create_section("Simulation & KPI-related Settings", 7)
    tk.Label(root, text="Simulation time (seconds):", anchor="w").grid(row=9, column=0, sticky='w')
    sim_time = tk.DoubleVar()
    tk.Entry(root, textvariable=sim_time).grid(row=9, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Random Seed:", anchor="w").grid(row=10, column=0, sticky='w')
    random_seed = tk.IntVar()
    tk.Entry(root, textvariable=random_seed).grid(row=10, column=1, columnspan=2, sticky='w')

    batch_run = BooleanVar()
    batch_run_label = tk.Checkbutton(root, text="Batch run?", variable=batch_run, command=toggle_batch_run)
    batch_run_label.grid(row=11, column=0, sticky='w')
    run_times = tk.IntVar()
    run_times_entry = tk.Entry(root, textvariable=run_times)

    tk.Label(root, text="Output file:", anchor="w").grid(row=12, column=0, sticky='w')
    output_file = StringVar()
    tk.Entry(root, textvariable=output_file).grid(row=12, column=1, sticky='w')
    tk.Button(root, text="Browse", command=lambda: output_file.set(filedialog.asksaveasfilename(defaultextension=".csv"))).grid(row=12, column=2)

    # Behavioral Settings
    create_section("Behavioral Settings", 13)
    tk.Label(root, text="Number of Ritsch Truck:", anchor="w").grid(row=15, column=0, sticky='w')
    ritsch_trucks = tk.IntVar()
    tk.Entry(root, textvariable=ritsch_trucks).grid(row=15, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Number of Dongfeng Truck:", anchor="w").grid(row=16, column=0, sticky='w')
    dongfeng_trucks = tk.IntVar()
    tk.Entry(root, textvariable=dongfeng_trucks).grid(row=16, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Number of Isuzu Truck:", anchor="w").grid(row=17, column=0, sticky='w')
    isuzu_trucks = tk.IntVar()
    tk.Entry(root, textvariable=isuzu_trucks).grid(row=17, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Number of Volvo Truck:", anchor="w").grid(row=18, column=0, sticky='w')
    volvo_trucks = tk.IntVar()
    tk.Entry(root, textvariable=volvo_trucks).grid(row=18, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Map file:", anchor="w").grid(row=19, column=0, sticky='w')
    map_file = StringVar()
    tk.Entry(root, textvariable=map_file).grid(row=19, column=1, sticky='w')
    tk.Button(root, text="Browse", command=lambda: map_file.set(filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")]))).grid(row=19, column=2)

    tk.Label(root, text="Start delivery threshold (volume):", anchor="w").grid(row=20, column=0, sticky='w')
    start_threshold = tk.DoubleVar()
    tk.Entry(root, textvariable=start_threshold).grid(row=20, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Maximum waiting time (minutes):", anchor="w").grid(row=21, column=0, sticky='w')
    max_waiting = tk.DoubleVar()
    tk.Entry(root, textvariable=max_waiting).grid(row=21, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Speed on Motorway (km/h):", anchor="w").grid(row=22, column=0, sticky='w')
    speed_motorway = tk.DoubleVar()
    tk.Entry(root, textvariable=speed_motorway).grid(row=22, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Speed on City Street (km/h):", anchor="w").grid(row=23, column=0, sticky='w')
    speed_city_street = tk.DoubleVar()
    tk.Entry(root, textvariable=speed_city_street).grid(row=23, column=1, columnspan=2, sticky='w')

    tk.Label(root, text="Truck parameters file:", anchor="w").grid(row=24, column=0, sticky='w')
    truck_params_file = StringVar()
    tk.Entry(root, textvariable=truck_params_file).grid(row=24, column=1, sticky='w')
    tk.Button(root, text="Browse", command=lambda: truck_params_file.set(filedialog.askopenfilename())).grid(row=24, column=2)

    # Visualization Settings
    create_section("Visualization Settings", 25)
    real_time_dashboard = BooleanVar()
    tk.Checkbutton(root, text="Real-time dashboard", variable=real_time_dashboard).grid(row=26, column=0, sticky='w')

    real_time_visualization = BooleanVar()
    tk.Checkbutton(root, text="Real-time process visualization", variable=real_time_visualization).grid(row=26, column=1, sticky='w')

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=27, column=0, columnspan=3)
    tk.Button(button_frame, text="Submit", command=submit).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=1, padx=5)

    root.mainloop()
    
    return params
