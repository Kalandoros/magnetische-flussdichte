import numpy as np
import plotly.graph_objs as go
from plotly.colors import sample_colorscale
from plotly.subplots import make_subplots
import plotly.io as pio

# Browser-Ausgabe erzwingen
pio.renderers.default = 'browser'

# --- 1. Parameter ---
I_rms, f, mu_0 = 2000.0, 50.0, 4 * np.pi * 1e-7
L_calc, L_plot, r_wire = 2000000.0, 100.0, 0.01
alpha_rad = np.radians(45.0)
C_SCALE = 'Viridis'

phases = [
    {'name':'L1', 'pos':(-6.0, 20.0), 'shift':0, 'color':'red'},
    {'name':'L2', 'pos':(0.0, 25.0), 'shift':2 * np.pi / 3, 'color':'green'},
    {'name':'L3', 'pos':(6.0, 20.0), 'shift':4 * np.pi / 3, 'color':'blue'}
]

def get_b_vector_segment_vectorized(P_x, P_y, P_z, start, end, I_t):
    L_vec = end - start
    L_mag = np.linalg.norm(L_vec)
    unit_L = L_vec / L_mag
    dx, dy, dz = P_x - start[0], P_y - start[1], P_z - start[2]
    d = dx * unit_L[0] + dy * unit_L[1] + dz * unit_L[2]
    r_perp_x, r_perp_y, r_perp_z = dx - d * unit_L[0], dy - d * unit_L[1], dz - d * unit_L[2]
    r_mag_raw = np.sqrt(r_perp_x**2 + r_perp_y**2 + r_perp_z**2)
    r_mag = np.maximum(r_mag_raw, r_wire)
    cos_theta1 = d / np.sqrt(d**2 + r_mag**2)
    cos_theta2 = (L_mag - d) / np.sqrt((L_mag - d)**2 + r_mag**2)
    B_mag = (mu_0 * I_t) / (4 * np.pi * r_mag) * (cos_theta1 + cos_theta2)
    B_mag *= np.where(r_mag_raw < r_wire, r_mag_raw / r_wire, 1.0)
    Bx_dir = unit_L[1] * r_perp_z - unit_L[2] * r_perp_y
    By_dir = unit_L[2] * r_perp_x - unit_L[0] * r_perp_z
    Bz_dir = unit_L[0] * r_perp_y - unit_L[1] * r_perp_x
    dir_norm = np.maximum(np.sqrt(Bx_dir**2 + By_dir**2 + Bz_dir**2), 1e-12)
    return B_mag * (Bx_dir / dir_norm), B_mag * (By_dir / dir_norm), B_mag * (Bz_dir / dir_norm)

def calculate_field_with_bend(X, Y, Z):
    t_steps = np.linspace(0, 1 / f, 12)
    B_total_sq_sum = np.zeros_like(X)
    Y_grid = np.full_like(X, Y) if np.isscalar(Y) else Y
    Z_grid = np.full_like(X, Z) if np.isscalar(Z) else Z
    for t in t_steps:
        Bx_sum, By_sum, Bz_sum = np.zeros_like(X), np.zeros_like(X), np.zeros_like(X)
        for p in phases:
            I_t = I_rms * np.sqrt(2) * np.sin(2 * np.pi * f * t + p['shift'])
            px, py = p['pos']
            s1_start, s1_end = np.array([px, py, -L_calc / 2]), np.array([px, py, 0])
            B1x, B1y, B1z = get_b_vector_segment_vectorized(X, Y_grid, Z_grid, s1_start, s1_end, I_t)
            dir_vec = np.array([np.sin(alpha_rad), 0, np.cos(alpha_rad)])
            s2_start, s2_end = s1_end, s1_end + (L_calc / 2) * dir_vec
            B2x, B2y, B2z = get_b_vector_segment_vectorized(X, Y_grid, Z_grid, s2_start, s2_end, I_t)
            Bx_sum += (B1x + B2x); By_sum += (B1y + B2y); Bz_sum += (B1z + B2z)
        B_total_sq_sum += (Bx_sum**2 + By_sum**2 + Bz_sum**2)
    return np.sqrt(B_total_sq_sum / len(t_steps)) * 1e6

# --- 2. Daten berechnen ---
res = 80
# Grid für Frontschnitt (Plot 1)
coords_side = np.linspace(-L_plot / 2, L_plot / 2, res)
y_coords_side = np.linspace(0, 45, res)
X_side, Y_side = np.meshgrid(coords_side, y_coords_side)

# Größeres Grid für Draufsicht (Plot 2), damit beim Pannen überall Daten vorhanden sind
L_plot_top = L_plot * 3
coords_top = np.linspace(-L_plot_top / 2, L_plot_top / 2, res)
X_top, Z_top = np.meshgrid(coords_top, coords_top)

# Hilfsfunktion für Isolinien
def add_contours_custom(fig, z_data, x, y, row, col, show_cb=False):
    htemp = "X: %{x:.1f}m<br>Y/Z: %{y:.1f}m<br><b>B: %{z:.2f} uT</b><extra></extra>"
    # Zielbereich: 0.9 uT Linie + 1-10 uT (1er) + 10-200 uT (10er)
    z_09 = 0.9
    z_1 = 1.0
    z_10 = 10.0
    z_200 = 200.0

    # 0.9 uT als eigene Linie
    fig.add_trace(go.Contour(
        z=z_data, x=x, y=y, colorscale=C_SCALE, autocontour=False,
        contours=dict(start=z_09, end=z_09, size=0.1, coloring='lines', showlines=True, showlabels=True),
        line=dict(color='black', width=2),
        showscale=False, hovertemplate=htemp
    ), row=row, col=col)

    # 1-10 uT in 1er-Schritten
    fig.add_trace(go.Contour(
        z=z_data, x=x, y=y, colorscale=C_SCALE, autocontour=False,
        contours=dict(start=z_1, end=z_10, size=1.0, coloring='lines', showlines=True, showlabels=True),
        line=dict(width=1),
        showscale=False, zmin=z_1, zmax=z_200, hovertemplate=htemp
    ), row=row, col=col)

    # 10-200 uT in 10er-Schritten + Farblegende
    fig.add_trace(go.Contour(
        z=z_data, x=x, y=y, colorscale=C_SCALE, autocontour=False,
        contours=dict(start=z_10, end=z_200, size=10.0, coloring='lines', showlines=True, showlabels=True),
        line=dict(width=1.5),
        showscale=show_cb, zmin=z_1, zmax=z_200,
        colorbar=dict(
            title="B [uT]",
            x=1.02, y=0.5,
            tickvals=[1, 2, 5, 10, 20, 50, 100, 200],
            ticktext=["1", "2", "5", "10", "20", "50", "100", "200"]
        ) if show_cb else None,
        hovertemplate=htemp
    ), row=row, col=col)

# Isolinien über den gesamten Wertebereich (globales zmin/zmax)
def add_contours_fullrange(fig, z_data, x, y, row, col, zmin, zmax, show_cb=False, nlevels=30):
    htemp = "X: %{x:.1f}m<br>Y/Z: %{y:.1f}m<br><b>B: %{z:.2f} ÂµT</b><extra></extra>"
    step = (zmax - zmin) / max(nlevels, 1)
    if step <= 0:
        step = 1.0
    fig.add_trace(go.Contour(
        z=z_data, x=x, y=y, colorscale=C_SCALE, autocontour=False,
        contours=dict(start=zmin, end=zmax, size=step, coloring='lines', showlines=True),
        line_width=1.2, showscale=show_cb, zmin=zmin, zmax=zmax,
        colorbar=dict(title="B [ÂµT]", x=1.02, y=0.5) if show_cb else None,
        hovertemplate=htemp
    ), row=row, col=col)

# --- FENSTER 1: Schnitt mit Z-Slider (Frontansicht folgt der Leitungsrichtung) ---
def calculate_front_slice(U, V, s_val):
    # Ebene senkrecht zur lokalen Leitungsrichtung
    if s_val <= 0:
        t_dir = np.array([0.0, 0.0, 1.0])
        origin = np.array([0.0, 0.0, s_val])
        x_axis = np.array([1.0, 0.0, 0.0])
    else:
        t_dir = np.array([np.sin(alpha_rad), 0.0, np.cos(alpha_rad)])
        origin = s_val * t_dir
        x_axis = np.array([np.cos(alpha_rad), 0.0, -np.sin(alpha_rad)])

    Xg = origin[0] + U * x_axis[0]
    Yg = V
    Zg = origin[2] + U * x_axis[2]
    return calculate_field_with_bend(Xg, Yg, Zg)

s_slices = np.arange(-L_plot / 2, L_plot / 2 + 1, 1)
B_slices = [calculate_front_slice(X_side, Y_side, s_val) for s_val in s_slices]

fig1 = make_subplots(rows=1, cols=1, subplot_titles=[f"Schnitt (s={s_slices[0]:.0f} m)"])
add_contours_custom(fig1, B_slices[0], coords_side, y_coords_side, 1, 1, show_cb=True)
for p in phases:
    px, py = p['pos']
    px_front = px if s_slices[0] <= 0 else px * np.cos(alpha_rad)
    fig1.add_trace(go.Scatter(x=[px_front], y=[py], mode='markers',
                               marker=dict(color=p['color'], size=12), name=p['name']))

frames = []
for s_val, b_data in zip(s_slices, B_slices):
    marker_updates = []
    for p in phases:
        px, py = p['pos']
        px_front = px if s_val <= 0 else px * np.cos(alpha_rad)
        marker_updates.append(go.Scatter(x=[px_front], y=[py]))

    frames.append(go.Frame(
        name=f"s={s_val:.0f}",
        data=[go.Contour(z=b_data), go.Contour(z=b_data), go.Contour(z=b_data), *marker_updates],
        layout=go.Layout(title_text=f"Schnitt (s={s_val:.0f} m)")
    ))

fig1.frames = frames
fig1.update_layout(
    title="Vertikaler Schnitt (Z-Slider)",
    height=800,
    width=900,
    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
    sliders=[{
        "currentvalue": {"prefix": "s = ", "suffix": " m"},
        "pad": {"t": 50},
        "steps": [
            {"label": f"{s_val:.0f}", "method": "animate",
             "args": [[f"s={s_val:.0f}"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
            for s_val in s_slices
        ],
    }]
)
fig1.show()

# --- FENSTER 2: Draufsicht mit Y-Slider ---
y_slices = np.arange(0, int(y_coords_side.max()) + 1, 1)
B_top_slices = [calculate_field_with_bend(X_top, y_val, Z_top) for y_val in y_slices]

fig2 = make_subplots(rows=1, cols=1, subplot_titles=[f"Draufsicht (y={y_slices[0]:.0f} m)"])
add_contours_custom(fig2, B_top_slices[0], coords_top, coords_top, 1, 1, show_cb=True)
for p in phases:
    px = p['pos'][0]
    fig2.add_trace(go.Scatter(x=[px, px, px + L_plot_top*np.sin(alpha_rad)],
                              y=[-L_plot_top/2, 0, L_plot_top*np.cos(alpha_rad)],
                              mode='lines', line=dict(color=p['color'], width=3),
                              showlegend=True, name=p['name']))

frames2 = []
for y_val, b_data in zip(y_slices, B_top_slices):
    frames2.append(go.Frame(
        name=f"y={y_val:.0f}",
        data=[go.Contour(z=b_data), go.Contour(z=b_data), go.Contour(z=b_data)],
        traces=[0, 1, 2],
        layout=go.Layout(title_text=f"Draufsicht (y={y_val:.0f} m)")
    ))

fig2.frames = frames2
fig2.update_layout(
    title="Draufsicht (Y-Slider)",
    height=700,
    width=900,
    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
    sliders=[{
        "currentvalue": {"prefix": "y = ", "suffix": " m"},
        "pad": {"t": 50},
        "steps": [
            {"label": f"{y_val:.0f}", "method": "animate",
             "args": [[f"y={y_val:.0f}"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
            for y_val in y_slices
        ],
    }]
)
fig2.show()

# --- FENSTER 3: 3D Plot (Korrekt nach oben!) ---
res3d = 30
c3d = np.linspace(-L_plot/2, L_plot/2, res3d)
y3d = np.linspace(0, 50, res3d) # Höhe
X3, Y3, Z3 = np.meshgrid(c3d, y3d, c3d)
B3D = calculate_field_with_bend(X3, Y3, Z3)

fig3 = go.Figure()

fig3.add_trace(go.Isosurface(
    # 90° Linksrotation in der X-Z Ebene: (X,Z) -> (-Z, X)
    x=(-Z3).flatten(),
    y=X3.flatten(),
    z=Y3.flatten(),
    value=B3D.flatten(),
    isomin=1, isomax=30, surface_count=8, opacity=0.3, colorscale=C_SCALE,
    caps=dict(x_show=False, y_show=False, z_show=False),
    colorbar=dict(title="B [µT]", yanchor="middle", y=0.5)
))

for p in phases:
    px, py = p['pos']
    # Leiterpfad: X=px, Höhe=py (Z-Achse), Längsrichtung in Y
    fig3.add_trace(go.Scatter3d(
        x=[L_plot / 2, 0, -L_plot * np.cos(alpha_rad)],
        y=[px, px, px + L_plot * np.sin(alpha_rad)],
        z=[py, py, py],
        mode='lines', line=dict(color=p['color'], width=8), name=p['name']
    ))

fig3.update_layout(
    title="3D Feldverteilung (Höhe = Z-Achse)",
    scene=dict(
        xaxis_title='Längsrichtung Z [m]',
        yaxis_title='Abstand X [m]',
        zaxis_title='Höhe Y [m]',
        zaxis=dict(range=[0, 50]),
        aspectratio=dict(x=1, y=0.5, z=1)
    ),
    legend=dict(orientation="h", yanchor="top", y=0.1, xanchor="center", x=0.5),
    width=1100, height=850
)
fig3.show()

# --- FENSTER 4: Karte (OpenStreetMap, Nordost-Schweiz) ---
# Lokales Koordinatensystem (Meter) -> WGS84 (Lat/Lon) Approximation
def meters_to_latlon(x_m, y_m, lat0, lon0):
    meters_per_deg_lat = 111320.0
    meters_per_deg_lon = 111320.0 * np.cos(np.radians(lat0))
    lat = lat0 + (y_m / meters_per_deg_lat)
    lon = lon0 + (x_m / meters_per_deg_lon)
    return lat, lon

# Konturlinien fuer Mapbox: mit matplotlib erzeugen, in Plotly als Scattermapbox zeichnen
def build_mapbox_contours(lat_grid, lon_grid, z_grid, levels, colorscale):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError("matplotlib wird zum Berechnen der Konturlinien benoetigt.") from exc

    fig = plt.figure()
    cs = plt.contour(lon_grid, lat_grid, z_grid, levels=levels)
    traces = []
    level_min = min(levels)
    level_max = max(levels)
    for lvl, segs in zip(cs.levels, cs.allsegs):
        if np.isclose(lvl, 0.9):
            color = "black"
            width = 2
        else:
            t = 0.0 if level_max == level_min else (lvl - level_min) / (level_max - level_min)
            color = sample_colorscale(colorscale, t)[0]
            width = 1.5 if lvl >= 10 else 1
        for seg in segs:
            if seg.shape[0] < 2:
                continue
            lon = seg[:, 0]
            lat = seg[:, 1]
            traces.append(go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode="lines",
                line=dict(color=color, width=width),
                showlegend=False
            ))
    plt.close(fig)
    return traces

# Fester Punkt in Nordost-Schweiz (freies Feld, ungefaehr)
base_lat = 47.55
base_lon = 9.25

# Auswahl eines Y-Slices fuer die Karte (z.B. 1 m Hoehe)
y_map = 1
if y_map < y_slices[0]:
    y_map = y_slices[0]
if y_map > y_slices[-1]:
    y_map = y_slices[-1]
idx_map = int(y_map - y_slices[0])
B_map = B_top_slices[idx_map]

# Grid in Lat/Lon umrechnen (X -> Ost/West, Z -> Nord/Sued)
lat_grid, lon_grid = meters_to_latlon(X_top, Z_top, base_lat, base_lon)
levels = [0.9] + list(np.arange(1, 11, 1)) + list(np.arange(20, 201, 10))

fig_map = go.Figure()
fig_map.add_trace(go.Densitymapbox(
    lat=lat_grid.flatten(),
    lon=lon_grid.flatten(),
    z=B_map.flatten(),
    radius=12,
    colorscale=C_SCALE,
    zmin=1,
    zmax=200,
    colorbar=dict(
        title="B [uT]",
        x=0.5, xanchor="center",
        y=0, yanchor="bottom",
        len=0.5,
        thickness=14
    ),
    name="B-Feld"
))

# Isolinien wie in Plot 2 (0.9 uT, 1-10 uT, 10-200 uT)
for trace in build_mapbox_contours(lat_grid, lon_grid, B_map, levels, C_SCALE):
    fig_map.add_trace(trace)

# Leiterverlauf als Linien auf der Karte
for p in phases:
    px = p['pos'][0]
    # Leiterlinie im Top-View (X/Z Ebene)
    x_line = np.array([px, px, px + L_plot_top * np.sin(alpha_rad)])
    z_line = np.array([-L_plot_top / 2, 0, L_plot_top * np.cos(alpha_rad)])
    lat_line, lon_line = meters_to_latlon(x_line, z_line, base_lat, base_lon)
    fig_map.add_trace(go.Scattermapbox(
        lat=lat_line, lon=lon_line,
        mode='lines',
        line=dict(color=p['color'], width=3),
        name=p['name']
    ))

fig_map.update_layout(
    title=f"Karte (Swissimage, swisstopo) - Feld bei y={y_map} m",
    mapbox=dict(
        style="white-bg",
        center=dict(lat=base_lat, lon=base_lon),
        zoom=12,
        layers=[{
            "sourcetype": "raster",
            "source": [
                "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
            ],
            "below": "traces"
        }]
    ),
    margin=dict(l=0, r=0, t=40, b=80),
    showlegend=True,
    legend=dict(orientation="h", x=0.5, xanchor="center", y=0, yanchor="bottom"),
    height=700,
    width=1000
)
fig_map.show()
