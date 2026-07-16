import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import base64

st.set_page_config(
    page_title="Dashboard UMP Indonesia",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE ─────────────────────────────────────────────────────
for k, v in {"theme": "light", "sb_open": True, "selected_prov": ["DKI JAKARTA","JAWA BARAT","JAWA TENGAH","JAWA TIMUR","BALI"], "pilih_semua": True}.items():
    st.session_state.setdefault(k, v)

IS_DARK = st.session_state.theme == "dark"
SB_OPEN = st.session_state.sb_open

T = dict(
    bg  = "#09090b" if IS_DARK else "#f9fafb",
    card= "#18181b" if IS_DARK else "#ffffff",
    text= "#fafafa"  if IS_DARK else "#111827",
    sub = "#a1a1aa"  if IS_DARK else "#6b7280",
    bdr = "#27272a"  if IS_DARK else "#e5e7eb",
    cp  = "#18181b"  if IS_DARK else "#ffffff",
    cpp = "#09090b"  if IS_DARK else "#f9fafb",
    ct  = "#a1a1aa"  if IS_DARK else "#6b7280",
    cg  = "#27272a"  if IS_DARK else "#f3f4f6",
    cl  = "#3f3f46"  if IS_DARK else "#e5e7eb",
    lb  = "rgba(9,9,11,.97)"   if IS_DARK else "rgba(255,255,255,.97)",
    sb  = "#000000"  if IS_DARK else "#ffffff",
)

# favicon base64 for header logo
_fav = Path(__file__).parent / "favicon.png"
_fav_b64 = base64.b64encode(_fav.read_bytes()).decode() if _fav.exists() else ""

_d = IS_DARK
_btn_col  = "#f5f5f5" if _d else "#111827"
_btn_bg   = "#27272a" if _d else "#ffffff"
_btn_bdr  = "#3f3f46" if _d else "#d1d5db"

# ── CSS: inject vars (dynamic) + load static file ─────────────────────
_css_static = (Path(__file__).parent / "style.css").read_text()
_sb_label   = "#e2e8f0" if IS_DARK else "#1f2937"

st.markdown(f"""
<style>
:root{{
  --bg:{T['bg']};--card:{T['card']};--text:{T['text']};--sub:{T['sub']};
  --bdr:{T['bdr']};--cg:{T['cg']};--sb:{T['sb']};--sb-w:{'0px' if not SB_OPEN else '288px'};--sb-btn-left:{'10px' if not SB_OPEN else '126px'};
  --btn-col:{_btn_col};--btn-bg:{_btn_bg};--btn-bdr:{_btn_bdr};
  --sb-label:{_sb_label};
}}
{_css_static}
</style>
""", unsafe_allow_html=True)
# ── DATA ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    p = Path(__file__).parent / "ump.xlsx"
    if not p.exists():
        st.error("❌ File ump.xlsx tidak ditemukan."); st.stop()
    df = pd.read_excel(p)
    return df[df["TIPE"]=="PROVINSI"].copy(), df[df["TIPE"]=="NASIONAL"].copy()

prov_df, nat_df = load_data()
ALL_PROV = sorted(prov_df["PROVINSI"].unique().tolist())
ALL_YEAR = sorted(prov_df["TAHUN"].unique().tolist())

COLORS = [
    "#3b82f6","#10b981","#f59e0b","#8b5cf6","#06b6d4","#84cc16","#f97316","#ec4899",
    "#14b8a6","#6366f1","#a3e635","#fb923c","#e879f9","#22d3ee","#4ade80","#fbbf24",
    "#c084fc","#67e8f9","#86efac","#fdba74","#d8b4fe","#a5f3fc","#bbf7d0","#fed7aa",
    "#f9a8d4","#b2f5ea","#c3dafe","#fcd34d","#f0abfc","#93c5fd","#6ee7b7","#fde68a",
    "#e9d5ff","#bae6fd","#99f6e4","#d1fae5","#dbeafe","#fef9c3",
]

def fmt_rp(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return "—"
    return f"Rp {v/1_000_000:.2f} Jt" if v >= 1_000_000 else f"Rp {v/1_000:.0f} Rb"

# ── CHART BUILDERS ────────────────────────────────────────────────────
def _theme(is_dark):
    return dict(
        bg  = "#09090b" if is_dark else "#f9fafb",
        card= "#18181b" if is_dark else "#ffffff",
        text= "#fafafa"  if is_dark else "#111827",
        sub = "#a1a1aa"  if is_dark else "#6b7280",
        bdr = "#27272a"  if is_dark else "#e5e7eb",
        cp  = "#18181b"  if is_dark else "#ffffff",
        cpp = "#09090b"  if is_dark else "#f9fafb",
        ct  = "#a1a1aa"  if is_dark else "#6b7280",
        cg  = "#27272a"  if is_dark else "#f3f4f6",
        cl  = "#3f3f46"  if is_dark else "#e5e7eb",
        lb  = "rgba(9,9,11,.97)"   if is_dark else "rgba(255,255,255,.97)",
    )

@st.cache_data
def build_trend(prov_rows, nat_rows, selected_prov, show_nat, is_dark, n_years):
    import pandas as _pd
    f_prov = _pd.DataFrame(prov_rows, columns=["PROVINSI","TAHUN","UPAH"])
    f_nat  = _pd.DataFrame(nat_rows,  columns=["TAHUN","UPAH"])
    T2 = _theme(is_dark)
    fig = go.Figure()
    for i, (prov, grp) in enumerate(f_prov.groupby("PROVINSI")):
        g = grp.sort_values("TAHUN")
        c = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=g["TAHUN"], y=g["UPAH"], mode="lines+markers", name=prov,
            line=dict(color=c, width=1.5), marker=dict(size=4, color=c), opacity=0.85,
            hovertemplate=f"<b>{prov}</b><br>Tahun: %{{x}}<br>UMP: Rp %{{y:,.0f}}<extra></extra>"
        ))
    if show_nat:
        n = f_nat.sort_values("TAHUN")
        fig.add_trace(go.Scatter(
            x=n["TAHUN"], y=n["UPAH"], mode="lines+markers", name="🇮🇩 Rata-rata Nasional",
            line=dict(color="#dc2626", width=3.5), marker=dict(size=7, color="#dc2626", symbol="diamond"),
            hovertemplate="<b>Rata-rata Nasional</b><br>Tahun: %{x}<br>UMP: Rp %{y:,.0f}<extra></extra>"
        ))
    many = len(selected_prov) > 15
    fig.update_layout(
        paper_bgcolor=T2["cp"], plot_bgcolor=T2["cpp"], height=430,
        margin=dict(t=10, r=10, b=50, l=85), hovermode="closest",
        legend=dict(font=dict(size=11, color=T2["text"]), bgcolor=T2["lb"],
                    bordercolor=T2["bdr"], borderwidth=1,
                    orientation="h" if many else "v",
                    x=0 if many else 1, y=-0.18 if many else 1,
                    xanchor="left", yanchor="top"),
        xaxis=dict(title=dict(text="Tahun", font=dict(color=T2["sub"], size=12)),
                   gridcolor=T2["cg"], linecolor=T2["cl"], tickfont=dict(size=11, color=T2["ct"]),
                   dtick=2 if n_years > 20 else 1),
        yaxis=dict(title=dict(text="UMP (Rp)", font=dict(color=T2["sub"], size=12)),
                   gridcolor=T2["cg"], linecolor=T2["cl"], tickformat=",.0f",
                   tickprefix="Rp ", tickfont=dict(size=11, color=T2["ct"])),
        transition_duration=0,
    )
    return fig

@st.cache_data
def build_rank(rank_rows, nat_rv, show_nat, rank_year, is_dark):
    import pandas as _pd
    rank_d = _pd.DataFrame(rank_rows, columns=["PROVINSI","UPAH"])
    T2 = _theme(is_dark)
    fig = go.Figure()
    if not rank_d.empty:
        colors_r = ["#16a34a" if w >= (nat_rv or 0) else "#dc2626" for w in rank_d["UPAH"]]
        fig.add_trace(go.Bar(
            x=rank_d["UPAH"], y=rank_d["PROVINSI"], orientation="h",
            marker=dict(color=colors_r, opacity=0.85),
            hovertemplate="<b>%{y}</b><br>UMP: Rp %{x:,.0f}<extra></extra>",
        ))
        if nat_rv and show_nat:
            fig.add_vline(x=nat_rv, line_dash="dash", line_color="#dc2626", line_width=2)
            fig.add_annotation(x=nat_rv, y=len(rank_d) - 0.5,
                text=f"Nasional: {fmt_rp(nat_rv)}", font=dict(color="#dc2626", size=10),
                showarrow=False, xanchor="left", yanchor="bottom")
    fig.update_layout(
        paper_bgcolor=T2["cp"], plot_bgcolor=T2["cpp"],
        height=max(380, len(rank_d) * 22 + 60),
        margin=dict(t=10, r=20, b=50, l=155),
        xaxis=dict(title=dict(text="UMP (Rp)", font=dict(color=T2["sub"], size=11)),
                   tickformat=",.0f", gridcolor=T2["cg"], linecolor=T2["cl"], tickfont=dict(size=10, color=T2["ct"])),
        yaxis=dict(tickfont=dict(size=10, color=T2["text"]), automargin=True),
        showlegend=False,
        transition_duration=0,
    )
    return fig

@st.cache_data
def build_growth(growth_rows, chart_h, is_dark, dtick):
    import pandas as _pd
    nat_sorted = _pd.DataFrame(growth_rows, columns=["TAHUN","UPAH","growth"])
    T2 = _theme(is_dark)
    fig = go.Figure()
    if not nat_sorted.empty:
        colors_g = ["rgba(22,163,74,.85)" if g >= 0 else "rgba(220,38,38,.85)" for g in nat_sorted["growth"]]
        fig.add_trace(go.Bar(
            x=nat_sorted["TAHUN"], y=nat_sorted["growth"], marker=dict(color=colors_g),
            text=[f"{g:.1f}%" for g in nat_sorted["growth"]],
            textposition="outside", textfont=dict(size=9, color=T2["ct"]), cliponaxis=False,
            hovertemplate="Tahun %{x}<br>YoY: <b>%{y:.2f}%</b><extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor=T2["cp"], plot_bgcolor=T2["cpp"], height=chart_h,
        margin=dict(t=24, r=15, b=50, l=60),
        xaxis=dict(title=dict(text="Tahun", font=dict(color=T2["sub"], size=11)),
                   gridcolor=T2["cg"], linecolor=T2["cl"], tickfont=dict(size=11, color=T2["ct"]), dtick=dtick),
        yaxis=dict(title=dict(text="Pertumbuhan (%)", font=dict(color=T2["sub"], size=11)),
                   gridcolor=T2["cg"], linecolor=T2["cl"], ticksuffix="%",
                   tickfont=dict(size=11, color=T2["ct"]),
                   zeroline=True, zerolinecolor="#94a3b8", zerolinewidth=1.5),
        transition_duration=0,
    )
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("◀" if SB_OPEN else "▶", key="sb_toggle"):
        st.session_state.sb_open = not SB_OPEN; st.rerun()
    if st.button("🌙  Dark Mode" if IS_DARK else "☀️  Light Mode", key="theme_btn"):
        st.session_state.theme = "light" if IS_DARK else "dark"; st.rerun()
    st.markdown("---")

    st.markdown("<div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-top:6px;margin-bottom:4px;'>📅 Rentang Tahun</div>", unsafe_allow_html=True)
    year_range = st.slider("Tahun", min_value=min(ALL_YEAR), max_value=max(ALL_YEAR),
                           value=(min(ALL_YEAR), max(ALL_YEAR)), label_visibility="collapsed")
    from_yr, to_yr = year_range
    st.caption(f"📌 **{from_yr}** hingga **{to_yr}** ({to_yr - from_yr + 1} tahun)")
    st.markdown("---")

    st.markdown("<div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-top:6px;margin-bottom:4px;'>🏢 Filter Provinsi</div>", unsafe_allow_html=True)
    show_nat = st.checkbox("Tampilkan Rata-rata Nasional", value=True)
    pilih_semua = st.checkbox("Pilih Semua Provinsi", value=st.session_state.pilih_semua)
    st.session_state.pilih_semua = pilih_semua

    if pilih_semua:
        selected_prov = ALL_PROV
        st.caption(f"✅ Semua **{len(ALL_PROV)}** provinsi dipilih")
    else:
        selected_prov = st.multiselect("Pilih provinsi:", options=ALL_PROV,
            default=st.session_state.selected_prov,
            placeholder="Cari & pilih provinsi...", key="ms_prov")
        st.session_state.selected_prov = selected_prov or st.session_state.selected_prov
        if not selected_prov:
            st.warning("⚠️ Pilih minimal 1 provinsi"); st.stop()
        st.caption(f"✅ **{len(selected_prov)}** dari {len(ALL_PROV)} provinsi dipilih")
    st.markdown("---")

    filt_years = [y for y in ALL_YEAR if from_yr <= y <= to_yr]
    st.markdown("<div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-top:6px;margin-bottom:4px;'>🏆 Tahun Ranking</div>", unsafe_allow_html=True)
    rank_year = int(st.number_input("Tahun ranking:", label_visibility="collapsed",
        min_value=int(min(filt_years)), max_value=int(max(filt_years)),
        value=int(max(filt_years)), step=1))
    st.caption(f"📌 {int(min(filt_years))} – {int(max(filt_years))}")



# ── FILTERED DATA ─────────────────────────────────────────────────────
f_prov = prov_df[prov_df["PROVINSI"].isin(selected_prov) & prov_df["TAHUN"].isin(filt_years)]
f_nat  = nat_df[nat_df["TAHUN"].isin(filt_years)]

# ── HEADER ────────────────────────────────────────────────────────────
_logo = (f'<img src="data:image/png;base64,{_fav_b64}" style="height:48px;width:48px;object-fit:contain;border-radius:8px;" />'
         if _fav_b64 else
         '<div style="width:48px;height:48px;background:rgba(255,255,255,.15);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:28px;">💹</div>')

st.markdown(f"""
<div class="ump-header" style="background:linear-gradient(135deg,#7f1d1d,#b91c1c,#dc2626,#ef4444);
  padding:18px 24px;border-radius:12px;margin-bottom:18px;box-shadow:0 4px 24px rgba(127,29,29,.3);">
  <div style="display:flex;align-items:center;gap:14px;">
    <span style="font-size:38px;">🇮🇩</span>
    <div style="flex:1;">
      <div style="font-size:20px;font-weight:800;letter-spacing:-.02em;">Dashboard UMP Indonesia</div>
      <div style="font-size:12px;opacity:.8;margin-top:3px;">
        Upah Minimum Provinsi &bull; <b>{len(selected_prov)}</b> Provinsi &bull; <b>{from_yr}–{to_yr}</b>
      </div>
    </div>
    {_logo}
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────
nat_now_v  = nat_df.loc[nat_df["TAHUN"] == to_yr,     "UPAH"].iat[0] if (nat_df["TAHUN"] == to_yr).any()     else None
nat_prev_v = nat_df.loc[nat_df["TAHUN"] == to_yr - 1, "UPAH"].iat[0] if (nat_df["TAHUN"] == to_yr - 1).any() else None
nat_from_v = nat_df.loc[nat_df["TAHUN"] == from_yr,   "UPAH"].iat[0] if (nat_df["TAHUN"] == from_yr).any()   else None
prov_to = f_prov[f_prov["TAHUN"] == to_yr]
highest = prov_to.loc[prov_to["UPAH"].idxmax()] if not prov_to.empty else None
lowest  = prov_to.loc[prov_to["UPAH"].idxmin()] if not prov_to.empty else None
n    = to_yr - from_yr
yoy  = (nat_now_v - nat_prev_v) / nat_prev_v * 100 if nat_now_v and nat_prev_v else None
cagr = ((nat_now_v / nat_from_v) ** (1 / n) - 1) * 100 if nat_now_v and nat_from_v and n > 0 else None

_green = "#4ade80" if IS_DARK else "#16a34a"
_grey  = "#a1a1aa" if IS_DARK else "#6b7280"

def _kpi(label, value, icon, delta_text, delta_color, tip=""):
    badge = (f'<span style="background:{delta_color};color:#fff;font-size:11px;font-weight:600;'
             f'padding:3px 8px;border-radius:6px;">{icon} {delta_text}</span>') if delta_text else ""
    tooltip = f'<div class="kpi-tip">{tip}</div>' if tip else ""
    return (f'<div class="kpi-card" style="background:{T["card"]};border:1px solid {T["bdr"]};'
            f'border-radius:12px;padding:14px 18px;box-shadow:0 1px 3px rgba(0,0,0,.1);">'
            f'{tooltip}'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;'
            f'color:{T["sub"]};margin-bottom:6px;">{label}</div>'
            f'<div style="font-size:20px;font-weight:800;color:{T["text"]};margin-bottom:8px;">{value}</div>'
            f'{badge}</div>')

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(_kpi("💰 Rata-rata Nasional", fmt_rp(nat_now_v), "▲", f"{yoy:+.1f}% vs {to_yr-1}" if yoy else "", _green, f"UMP rata-rata nasional tahun {to_yr}"), unsafe_allow_html=True)
with c2: st.markdown(_kpi("🏆 UMP Tertinggi", fmt_rp(highest["UPAH"]) if highest is not None else "—", "▲", highest["PROVINSI"] if highest is not None else "", _green, f"Provinsi UMP tertinggi tahun {to_yr}"), unsafe_allow_html=True)
with c3: st.markdown(_kpi("📉 UMP Terendah", fmt_rp(lowest["UPAH"]) if lowest is not None else "—", "▼", lowest["PROVINSI"] if lowest is not None else "", "#dc2626", f"Provinsi UMP terendah tahun {to_yr}"), unsafe_allow_html=True)
with c4: st.markdown(_kpi("📈 Pertumbuhan CAGR", f"{cagr:.1f}%" if cagr else "—", "▶", f"Nasional {from_yr}–{to_yr}" if cagr else "", _grey, "Compound Annual Growth Rate UMP Nasional"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TREND CHART ───────────────────────────────────────────────────────
st.markdown(f"""<div class="chart-box">
  <div class="chart-title">📈 Tren UMP per Provinsi</div>
  <div class="chart-sub">Pergerakan upah minimum dari waktu ke waktu &bull; Klik legenda untuk sembunyikan/tampilkan provinsi</div>
</div>""", unsafe_allow_html=True)
# prep hashable args for cached chart builders
_prov_rows = tuple(f_prov[f_prov["PROVINSI"].isin(selected_prov)][["PROVINSI","TAHUN","UPAH"]].itertuples(index=False, name=None))
_nat_rows  = tuple(f_nat[["TAHUN","UPAH"]].itertuples(index=False, name=None))
st.plotly_chart(build_trend(_prov_rows, _nat_rows, tuple(selected_prov), show_nat, IS_DARK, len(filt_years)),
    use_container_width=True, config=dict(displaylogo=False))

# ── RANKING + GROWTH ──────────────────────────────────────────────────
col_r, col_g = st.columns([1.2, 0.8])

with col_r:
    st.markdown(f"""<div class="chart-box">
      <div class="chart-title">🏆 Ranking UMP Provinsi Tahun {rank_year}</div>
      <div class="chart-sub"><span style="color:#16a34a">■ Hijau</span> = di atas rata-rata nasional &nbsp;|&nbsp; <span style="color:#dc2626">■ Merah</span> = di bawah rata-rata nasional</div>
    </div>""", unsafe_allow_html=True)
    _rank_df = prov_df[prov_df["PROVINSI"].isin(selected_prov) & (prov_df["TAHUN"] == rank_year)].sort_values("UPAH")
    nat_rv   = nat_df.loc[nat_df["TAHUN"] == rank_year, "UPAH"].iat[0] if (nat_df["TAHUN"] == rank_year).any() else None
    _rank_rows = tuple(_rank_df[["PROVINSI","UPAH"]].itertuples(index=False, name=None))
    st.plotly_chart(build_rank(_rank_rows, nat_rv, show_nat, rank_year, IS_DARK),
        use_container_width=True, config=dict(displaylogo=False))

with col_g:
    st.markdown(f"""<div class="chart-box">
      <div class="chart-title">📊 Pertumbuhan YoY Nasional</div>
      <div class="chart-sub"><span style="color:#16a34a">■ Hijau</span> = naik &nbsp;|&nbsp; <span style="color:#dc2626">■ Merah</span> = turun</div>
    </div>""", unsafe_allow_html=True)
    _nat_g = nat_df[nat_df["TAHUN"].isin(filt_years)].sort_values("TAHUN").copy()
    _nat_g["growth"] = _nat_g["UPAH"].pct_change() * 100
    _nat_g = _nat_g.dropna(subset=["growth"])
    chart_h = max(380, len(_rank_df) * 22 + 60)
    dtick   = 2 if len(filt_years) > 20 else 1
    _growth_rows = tuple(_nat_g[["TAHUN","UPAH","growth"]].itertuples(index=False, name=None))
    st.plotly_chart(build_growth(_growth_rows, chart_h, IS_DARK, dtick),
        use_container_width=True, config=dict(displaylogo=False))

# ── FOOTER ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""<div style="text-align:center;font-size:11px;color:{T['sub']};padding:6px 0;line-height:1.8;">
<b style="color:{T['text']};">&copy; Fariz Sidki</b>
</div>""", unsafe_allow_html=True)