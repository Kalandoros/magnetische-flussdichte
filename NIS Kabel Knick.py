import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio

pio.renderers.default = 'browser'

# --- 1. Parameter ---
I_rms = 1000.0
f = 50.0
mu_0 = 4 * np.pi * 1e-7
L_calc = 2000000.0
L_plot = 100.0
r_wire = 0.01
alpha_deg = 45.0
alpha_rad = np.radians(alpha_deg)
# Neue Farbskala ohne Schwarz
C_SCALE = 'Viridis'

phases = [{'pos':(-6.0, 20.0), 'shift':0}, {'pos':(0.0, 25.0), 'shift':2 * np.pi / 3}, {'pos':(6.0, 20.0), 'shift':4 * np.pi / 3}]

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
coords = np.linspace(-L_plot / 2, L_plot / 2, res)
X_top, Z_top = np.meshgrid(coords, coords)
B_top_1m = calculate_field_with_bend(X_top, 1.0, Z_top)
B_top_3m = calculate_field_with_bend(X_top, 3.0, Z_top)
y_coords = np.linspace(0, 45, res)
X_side, Y_side = np.meshgrid(coords, y_coords)
B_side = calculate_field_with_bend(X_side, Y_side, 0.0)

# --- 3. Plotting 2D (Fenster 1) ---
fig2d = make_subplots(rows=1, cols=3, subplot_titles=("Schnitt (z=0)", "Draufsicht 1m", "Draufsicht 3m"))

def add_contours(fig, z_data, x, y, col, show_cb=False):
    htemp = "X: %{x:.1f}m<br>Z/Y: %{y:.1f}m<br><b>B: %{z:.2f} µT</b><extra></extra>"
    fig.add_trace(go.Contour(z=z_data, x=x, y=y, colorscale=C_SCALE, autocontour=False,
                             contours=dict(start=1, end=9, size=1, coloring='lines', showlines=True, showlabels=True),
                             line_width=1, showscale=False, hovertemplate=htemp), row=1, col=col)
    fig.add_trace(go.Contour(z=z_data, x=x, y=y, colorscale=C_SCALE, autocontour=False,
                             contours=dict(start=10, end=150, size=10, coloring='lines', showlines=True, showlabels=True),
                             line_width=2, colorbar=dict(title="B [µT]", x=1.02) if show_cb else None,
                             showscale=show_cb, hovertemplate=htemp), row=1, col=col)

add_contours(fig2d, B_side, coords, y_coords, 1)
add_contours(fig2d, B_top_1m, coords, coords, 2)
add_contours(fig2d, B_top_3m, coords, coords, 3, show_cb=True)

for col in [2, 3]:
    for p in phases:
        px = p['pos'][0]
        fig2d.add_trace(go.Scatter(x=[px, px, px + L_plot*np.sin(alpha_rad)], y=[-L_plot/2, 0, L_plot*np.cos(alpha_rad)],
                                   mode='lines', line=dict(color='black', width=2), hoverinfo='skip'), row=1, col=col)

fig2d.update_layout(title_text="2D Analyse (Farbe: Viridis, Leiter: Schwarz)", paper_bgcolor='white', plot_bgcolor='white')
fig2d.show()

# --- 4. 3D Plot (Fenster 2) ---
# Kleineres Mesh für 3D Performance
res3d = 30
c3d = np.linspace(-L_plot/2, L_plot/2, res3d)
y3d = np.linspace(0, 40, res3d)
X3, Y3, Z3 = np.meshgrid(c3d, y3d, c3d)
B3D = calculate_field_with_bend(X3, Y3, Z3)

fig3d = go.Figure()

# 3D Isosurfaces (Hüllen gleicher Feldstärke)
fig3d.add_trace(go.Isosurface(
    x=X3.flatten(), y=Y3.flatten(), z=Z3.flatten(), value=B3D.flatten(),
    isomin=1, isomax=20, surface_count=5, opacity=0.3, colorscale=C_SCALE,
    caps=dict(x_show=False, y_show=False, z_show=False),
    colorbar=dict(title="B [µT]")
))

# Leiter in 3D einzeichnen
for p in phases:
    px, py = p['pos']
    # Segment 1
    fig3d.add_trace(go.Scatter3d(x=[px, px], y=[py, py], z=[-L_plot/2, 0],
                                 mode='lines', line=dict(color='black', width=5)))
    # Segment 2
    fig3d.add_trace(go.Scatter3d(x=[px, px + L_plot*np.sin(alpha_rad)], y=[py, py], z=[0, L_plot*np.cos(alpha_rad)],
                                 mode='lines', line=dict(color='black', width=5)))

fig3d.update_layout(title="3D Feldverteilung im Raum", scene=dict(
    xaxis_title='Abstand X [m]', yaxis_title='Höhe Y [m]', zaxis_title='Längsrichtung Z [m]',
    aspectmode='data'
))
fig3d.show()