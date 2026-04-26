import streamlit as st
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

# Ucitavamo lokalne biblioteke
from database import init_db, save_chat_message, get_chat_history, get_chat_list, get_next_chat_id
from ai_agent import get_ai_chat_session
from tools import (
    get_current_balance, get_expenses_last_30_days, get_revenue_last_30_days,
    get_expenses_by_category, get_monthly_revenue_expenses,
    get_recent_activities, get_upcoming_obligations,
    get_yoy_comparison, get_golden_month, calculate_health_score,
    get_goal_progress, forecast_cash_flow, get_ai_insights
)

# Inicijalizacija na pocetku
load_dotenv()
init_db()

st.set_page_config(page_title="FinAssist.ai", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        color-scheme: light;
        font-family: 'Inter', system-ui, sans-serif;
        color: #111827;
        background-color: #F7F9FC;
    }

    html, body, [data-testid="stAppViewContainer"], .css-18e3th9, .css-1d391kg,
    .main .block-container, .stApp, .st-bd {
        background: #F7F9FC !important;
    }

    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
    }

    .st-emotion-cache-zy6yx3 {
        padding-top: 0 !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #111827 !important;
        pointer-events: none;
        cursor: default;
        text-decoration: none;
    }

    .stMarkdown p, .stText, .css-1cpxqw2 p,
    .stTextInput>div>div>input, .stButton>button, .stMarkdown span, .stMarkdown div {
        color: #374151 !important;
    }

    [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stSidebar"] {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
        border-right: 1px solid rgba(15,23,42,0.08);
        display: block !important;
        visibility: visible !important;
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
        height: auto !important;
        min-height: 100vh !important;
        position: relative !important;
        transform: translateX(0) !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"][aria-expanded="true"] {
        display: block !important;
        visibility: visible !important;
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
        height: auto !important;
        min-height: 100vh !important;
        transform: translateX(0) !important;
        opacity: 1 !important;
    }

    [data-testid="collapsedControl"],
    button[title="Collapse sidebar"],
    button[title="Expand sidebar"] {
        display: none !important;
    }

    [data-testid="stSidebar"] * {
        color: #1F2937 !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        display: block;
        width: 100%;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 12px;
        background: transparent;
        border: 1px solid transparent;
        color: #1F2937 !important;
        cursor: pointer;
        transition: background-color 0.2s ease, box-shadow 0.2s ease, color 0.2s ease;
        font-weight: 500;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: #FFFFFF;
        box-shadow: 0 10px 24px rgba(15,23,42,0.08);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label[aria-checked="true"] {
        background: #E0E7FF;
        color: #4F46E5 !important;
        font-weight: 600;
        border-color: transparent;
    }

    .sidebar-heading {
        font-size: 1.05rem;
        margin-bottom: 1rem;
        color: #111827;
        font-weight: 700;
    }

    .kpi-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        padding: 24px;
        margin: 10px 0;
    }

    .kpi-label {
        font-size: 14px;
        font-weight: 500;
        color: #6B7280;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 14px;
    }

    .kpi-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
    }

    .kpi-pill.positive {
        background: rgba(16, 185, 129, 0.12);
        color: #047857;
    }

    .kpi-pill.negative {
        background: rgba(248, 113, 113, 0.12);
        color: #B91C1C;
    }

    .chart-card {
        background: #FFFFFF;
        border-radius: 20px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        padding: 24px;
        margin-bottom: 20px;
    }

    .chart-card h3 {
        margin-top: 0;
        margin-bottom: 18px;
        color: #111827;
    }

    .right-panel h3 {
        margin-top: 0;
        margin-bottom: 18px;
    }

    .chat-body {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        padding-right: 4px;
    }

    .chat-bubble {
        border-radius: 20px;
        padding: 16px 18px;
        line-height: 1.6;
        color: #111827 !important;
    }

    .chat-bubble.user-bubble {
        background: #EFF6FF !important;
        color: #1F2937 !important;
    }

    .chat-bubble.assistant-bubble {
        background: #FFFFFF !important;
        box-shadow: 0 12px 24px rgba(15,23,42,0.08);
        border: 1px solid rgba(15,23,42,0.08);
        color: #1F2937 !important;
    }

    .stChatMessage > div {
        background: transparent !important;
        border: none !important;
    }

    .advisor-card {
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        border-left: 6px solid;
        box-shadow: 0 4px 12px rgba(15,23,42,0.08);
        background: #FFFFFF;
    }

    .advisor-card.critical {
        border-left-color: #EF4444;
        background: linear-gradient(135deg, #FFF5F5 0%, #FFFFFF 100%);
    }

    .advisor-card.tax {
        border-left-color: #3B82F6;
        background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
    }

    .advisor-card.investment {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
    }

    .card-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .critical .card-title {
        color: #DC2626;
    }

    .tax .card-title {
        color: #1D4ED8;
    }

    .investment .card-title {
        color: #047857;
    }

    .card-content {
        font-size: 14px;
        line-height: 1.6;
        color: #374151;
        margin-bottom: 12px;
    }

    .card-highlight {
        font-weight: 600;
        font-size: 18px;
    }

    .card-action {
        font-size: 13px;
        font-weight: 500;
        padding: 10px 14px;
        border-radius: 8px;
        display: inline-block;
        margin-top: 12px;
    }

    .card-action.critical {
        background: rgba(239, 68, 68, 0.15);
        color: #DC2626;
    }

    .card-action.tax {
        background: rgba(59, 130, 246, 0.15);
        color: #1D4ED8;
    }

    .card-action.investment {
        background: rgba(16, 185, 129, 0.15);
        color: #047857;
    }

    [data-testid="stChatInput"] {
        margin-top: auto !important;
        margin-bottom: 0 !important;
        align-self: stretch;
    }

    .history-toggle .stButton>button,
    .stButton>button {
        background: #ffffff;
        color: #1F2937;
        border: 1px solid rgba(107,114,128,0.35);
        border-radius: 14px;
        padding: 12px 16px;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        margin-bottom: 18px;
    }

    .stButton>button:hover {
        background: #F3F4F6;
        border-color: rgba(107,114,128,0.5);
    }

    .history-list {
        background: #F8FAFC;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 18px;
    }

    .history-item {
        padding: 12px 14px;
        border-radius: 14px;
        background: #FFFFFF;
        border: 1px solid rgba(15,23,42,0.06);
        margin-bottom: 10px;
    }

    .stTextInput>div>div>input {
        border-radius: 16px !important;
        border: 1px solid rgba(15,23,42,0.12) !important;
    }

    .chat-body .stContainer {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
    }

    .chart-marker {
        display: none;
    }
    div[data-testid="column"]:has(.chart-marker) {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05) !important;
        padding: 24px !important;
    }

    /* Stilizuje naslov unutar te kolone (kao tvoj .chart-card h3) */
    div[data-testid="column"]:has(.chart-marker) h3 {
        margin-top: 0 !important;
        margin-bottom: 18px !important;
        color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Glavni layout: sidebar + 2 kolone
with st.sidebar:
    st.markdown('<div class="sidebar-heading">Navigacija</div>', unsafe_allow_html=True)
    selected_tab = st.radio(
        "Odaberi stranicu",
        ["Početna", "Analitika", "Savetnik", "Podešavanja"],
        label_visibility="collapsed"
    )

col_main, col_chat = st.columns([0.7, 0.3])

# SREDIŠNJI DASHBOARD
with col_main:
    if selected_tab == "Početna":
        # Naslov
        st.markdown("# Moja Kompanija DOO")
        st.markdown("### Pregled finansija i statusa poslovanja", unsafe_allow_html=True)

        # KPI Kartice
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        balance = get_current_balance()
        expenses = get_expenses_last_30_days()
        revenue = get_revenue_last_30_days()

        with col_kpi1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">💳 Trenutno Stanje</div>
                <div class="kpi-value">{balance:,.0f} RSD</div>
                <div class="kpi-pill positive">+5% od prošlog meseca</div>
            </div>
            """, unsafe_allow_html=True)

        with col_kpi2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">📉 Troškovi (30d)</div>
                <div class="kpi-value">{expenses:,.0f} RSD</div>
                <div class="kpi-pill negative">-3.4% od prošlog meseca</div>
            </div>
            """, unsafe_allow_html=True)

        with col_kpi3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">📈 Prihodi (30d)</div>
                <div class="kpi-value">{revenue:,.0f} RSD</div>
                <div class="kpi-pill positive">+11% od prošlog meseca</div>
            </div>
            """, unsafe_allow_html=True)

# Grafikoni
        col_chart1, col_chart2 = st.columns([1, 1.5])

        with col_chart1:
            # TAJNI MARKER (CSS će zbog ovoga pretvoriti kolonu u belu karticu)
            st.markdown('<div class="chart-marker"></div>', unsafe_allow_html=True)
            st.markdown('<h3>Prihodi prema kategorijama</h3>', unsafe_allow_html=True)
            
            expenses_by_cat = get_expenses_by_category()
            if expenses_by_cat:
                fig_pie = px.pie(
                    values=list(expenses_by_cat.values()),
                    names=list(expenses_by_cat.keys()),
                    title=None, # Sklonili smo title iz plotlija da ne bude dupli sa <h3>
                    color_discrete_sequence=['#60A5FA', '#93C5FD', '#A5B4FC', '#818CF8', '#6366F1']
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=1)))
                fig_pie.update_layout(
                    margin=dict(t=10, b=10, l=0, r=0),
                    legend=dict(orientation='h', y=-0.08, x=0.5, xanchor='center'),
                    font_color='#334155',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            # TAJNI MARKER 
            st.markdown('<div class="chart-marker"></div>', unsafe_allow_html=True)
            st.markdown('<h3>Prihodi i Rashodi po Mesecima</h3>', unsafe_allow_html=True)
            
            revenues, expenses = get_monthly_revenue_expenses()
            months = sorted(set(revenues.keys()) | set(expenses.keys()))
            rev_values = [revenues.get(m, 0) for m in months]
            exp_values = [expenses.get(m, 0) for m in months]

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=months, y=rev_values, name='Prihodi', marker_color='#34D399', text=rev_values, textposition='outside'))
            fig_bar.add_trace(go.Bar(x=months, y=exp_values, name='Rashodi', marker_color='#FB923C', text=exp_values, textposition='outside'))
            fig_bar.update_layout(
                margin=dict(t=10, b=10, l=0, r=0),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                bargap=0.22,
                bargroupgap=0.12,
                font_color='#334155',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showline=False, tickfont=dict(color='#4B5563')),
                yaxis=dict(gridcolor='rgba(15,23,42,0.08)', zeroline=False, showline=False, tickfont=dict(color='#4B5563'))
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)

        # Tabele
        tab1, tab2 = st.tabs(["Nedavne Aktivnosti", "Predstojeće Obaveze"])

        with tab1:
            activities = get_recent_activities()
            if activities:
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                for act in activities:
                    st.write(f"**{act[0].capitalize()}**: {act[1]} - {act[2]:,.0f} RSD ({act[3]})")
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            obligations = get_upcoming_obligations()
            if obligations:
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                for obl in obligations:
                    st.write(f"**{obl[0].capitalize()}**: {obl[1]} - {obl[2]:,.0f} RSD ({obl[3]})")
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif selected_tab == "Analitika":
        st.markdown("# Analitika")
        st.markdown("### Dubinska analiza poslovanja")

        # Sekcija 1: Kontekst i Kriva učenja (Retrospektiva)
        st.markdown("## 1. Kontekst i Kriva učenja (Retrospektiva)")
        
        col_retro1, col_retro2, col_retro3 = st.columns([1, 1, 2])
        
        with col_retro1:
            yoy = get_yoy_comparison()
            if 'error' not in yoy:
                fig_spark = go.Figure()
                fig_spark.add_trace(go.Scatter(
                    x=['Prethodni Q', 'Trenutni Q'],
                    y=[yoy['previous_quarter'], yoy['current_quarter']],
                    mode='lines+markers',
                    line=dict(color='#4F46E5', width=3),
                    marker=dict(size=8)
                ))
                fig_spark.update_layout(
                    title='YoY Poređenje Kvartala',
                    showlegend=False,
                    margin=dict(t=40, b=20, l=20, r=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#334155'
                )
                st.plotly_chart(fig_spark, use_container_width=True)
        
        with col_retro2:
            golden = get_golden_month()
            st.metric("Zlatni Mesec", golden.get('month', 'N/A'), f"{golden.get('revenue', 0):,.0f} RSD")
        
        with col_retro3:
            insights = get_ai_insights()
            st.markdown("**AI Insights:**")
            st.write(insights)

        # Sekcija 2: Business Health Score & Real-time (Sadašnjost)
        st.markdown("## 2. Business Health Score & Real-time (Sadašnjost)")
        
        health = calculate_health_score()
        if 'error' not in health:
            col_health1, col_health2 = st.columns([1, 2])
            
            with col_health1:
                # Gauge chart
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=health['score'],
                    title={'text': "Health Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#4F46E5"},
                        'steps': [
                            {'range': [0, 30], 'color': "#EF4444"},
                            {'range': [30, 70], 'color': "#F59E0B"},
                            {'range': [70, 100], 'color': "#10B981"}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#334155'
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Klik za dijagnostiku
                if st.button("Dijagnostika"):
                    st.info(health['diagnostics'])
            
            with col_health2:
                # Live Goal Tracker
                goals = get_goal_progress()
                for goal in goals:
                    progress = goal['progress']
                    shadow = 100 - progress  # Pretpostavka da je trenutno 100% cilj
                    fig_progress = go.Figure()
                    fig_progress.add_trace(go.Bar(
                        x=[progress],
                        y=[''],
                        orientation='h',
                        marker=dict(color='#10B981'),
                        name='Ostvareno'
                    ))
                    fig_progress.add_trace(go.Bar(
                        x=[shadow],
                        y=[''],
                        orientation='h',
                        marker=dict(color='rgba(16, 185, 129, 0.3)'),
                        name='Do cilja'
                    ))
                    fig_progress.update_layout(
                        title=goal['goal'],
                        barmode='stack',
                        showlegend=False,
                        margin=dict(t=40, b=20, l=20, r=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(range=[0, 100])
                    )
                    st.plotly_chart(fig_progress, use_container_width=True)
                
                # Vitalni organi
                col_vit1, col_vit2, col_vit3 = st.columns(3)
                balance = get_current_balance()
                obligations = get_upcoming_obligations()
                receivables = sum([obl[2] for obl in obligations if obl[0] == 'faktura'])
                
                with col_vit1:
                    st.metric("💰 Keš", f"{balance:,.0f} RSD")
                with col_vit2:
                    st.metric("📉 Dugovanja", f"{sum([obl[2] for obl in obligations if obl[0] == 'faktura']):,.0f} RSD")
                with col_vit3:
                    st.metric("📈 Potraživanja", f"{receivables:,.0f} RSD")

        # Sekcija 3: 90-dnevni Horizont (Budućnost)
        st.markdown("## 3. 90-dnevni Horizont (Budućnost)")
        
        forecast = forecast_cash_flow(90)
        if 'error' not in forecast:
            # Linijski grafikon sa zonom poverenja
            days = [f['day'] for f in forecast['forecast']]
            balances = [f['balance'] for f in forecast['forecast']]
            
            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(
                x=days,
                y=balances,
                mode='lines',
                line=dict(color='#4F46E5', width=3),
                name='Projekcija'
            ))
            # Zona poverenja (placeholder)
            upper = [b * 1.1 for b in balances]
            lower = [b * 0.9 for b in balances]
            fig_forecast.add_trace(go.Scatter(
                x=days + days[::-1],
                y=upper + lower[::-1],
                fill='toself',
                fillcolor='rgba(79, 70, 229, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Zona poverenja'
            ))
            fig_forecast.update_layout(
                title='Cash Flow Forecast (90 dana)',
                xaxis_title='Dani',
                yaxis_title='Saldo (RSD)',
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#334155'
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Smart Alerts
            if forecast['alerts']:
                for alert in forecast['alerts']:
                    st.warning(alert)
    
    elif selected_tab == "Savetnik":
        st.markdown("# 🎯 Finansijski Strateg | Kontrolna tabla")
        
        # PROAKTIVNE KARTICE
        st.markdown("### Preporuke za Vaš Biznis")
        
        # Kartica 1 - CRVENA (Kritično)
        st.markdown("""
        <div class="advisor-card critical">
            <div class="card-title">🚨 KRITIČNO: Kašnjenje Uplata Klijenta</div>
            <div class="card-content">
                <strong>Firma XYZ</strong> je zakašnjela sa uplatomm od <span class="card-highlight">250.000 RSD</span>
                <br>
                <strong>Status:</strong> 15 dana u kašnjenju
                <br><br>
                ⚠️ <strong>Alarm za likvidnost:</strong> Nedostaje vam keš za nadolazeće obaveze. 
                Preporučujem da odmah kontaktirate Firmu XYZ i razmotriti opciju:
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li>Faktoring (do 90% vrednosti)</li>
                    <li>Privremeni mikro-kredit (kratkoročno)</li>
                </ul>
            </div>
            <div class="card-action critical">
                ⏰ HITNO: Kontaktirajte klijenta danas
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Kartica 2 - PLAVA (Poresko)
        st.markdown("""
        <div class="advisor-card tax">
            <div class="card-title">💼 PORESKO: PDV Limit - 78% Popunjenost</div>
            <div class="card-content">
                Trenutno ste iskoristili <span class="card-highlight">78% od PDV limita</span> za ovaj period.
                <br>
                <strong>Preostalo:</strong> 22% (pribz. 180.000 RSD)
                <br><br>
                💡 <strong>Savet za optimizaciju:</strong> Razmotrite ulaganje u poresku infrastrukturu:
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Softver za evidenciju:</strong> ~50.000 RSD (PDV odbitna stavka)</li>
                    <li><strong>Stručna pomoć:</strong> ~30.000 RSD (PDV odbitna stavka)</li>
                </ul>
                Ova ulaganja će optimizovati vašu poresku poziciju.
            </div>
            <div class="card-action tax">
                🔍 Analizirajte mogućnosti ulaganja
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Kartica 3 - ZELENA (Investiciono)
        st.markdown("""
        <div class="advisor-card investment">
            <div class="card-title">📈 INVESTICIONO: Oročena Štednja - Odličan Prihod</div>
            <div class="card-content">
                Na osnovu viška od <span class="card-highlight">350.000 RSD</span> koji se pojavljuje krajem meseca,
                <br>
                predlažem oročenu štednju na <strong>90 dana sa kamatom od 4.2%</strong>.
                <br><br>
                📊 <strong>Predviđeni prihod:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li>350.000 RSD × 4.2% × (90/365) = <strong>3.640 RSD</strong></li>
                    <li>Bez rizika, bez komplikacija</li>
                </ul>
                To bi vam omogućilo dodatni keš-flow i zaštitu od inflacije.
            </div>
            <div class="card-action investment">
                ✓ Kontaktirajte banku za oročenu štednju
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # SIMULIRANI GRAFIKON - CASH FLOW 30 DANA
        st.markdown("### 📊 Predviđeni Cash Flow - Narednih 30 Dana")
        
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Mockup podaci
        today = datetime.now()
        days_list = [(today + timedelta(days=i)).strftime("%d.%m") for i in range(31)]
        
        # Simulirani cash flow sa trendoima
        np.random.seed(42)
        base_balance = 1500000
        cash_flow = []
        
        for i in range(31):
            # Trend: početak meseca poboljšanja, sredina pada, kraj oporavka
            if i < 10:
                change = np.random.uniform(50000, 120000)  # Poboljšanje
            elif i < 20:
                change = np.random.uniform(-100000, -30000)  # Pada
            else:
                change = np.random.uniform(80000, 150000)  # Oporavak
            
            base_balance += change
            cash_flow.append(max(base_balance, 0))  # Sprečavanje negativnog balanssa
        
        # Kreiranje DataFrame-a
        df_cash = pd.DataFrame({
            'Dan': days_list,
            'Saldo (RSD)': cash_flow
        })
        
        # Prikaz kao line_chart
        st.line_chart(
            df_cash.set_index('Dan'),
            use_container_width=True,
            height=350,
            color=['#4F46E5']
        )
        
        # Legenda ispod grafika
        col_legend1, col_legend2, col_legend3 = st.columns(3)
        with col_legend1:
            st.markdown("""
            **📈 Zelena zona:** Likvidnost je dobra
            """)
        with col_legend2:
            st.markdown("""
            **🟡 Žuta zona:** Pažljivo sa novcem
            """)
        with col_legend3:
            st.markdown("""
            **🔴 Crvena zona:** Rizik od insolventnosti
            """)
    
    elif selected_tab == "Podešavanja":
        st.markdown("# Podešavanja")
        st.write("Konfiguracija aplikacije...")

# DESNI PANEL - CHAT
with col_chat:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    
    # 1. HAMBURGER MENI (Mali padajući meni na vrhu)
    # st.popover kreira dugme koje, kada se klikne, otvara plutajući prozor
    with st.popover("☰", help="Prikaži istoriju chatova"):
        st.markdown("**Istorija Chatova**")
        chat_list = get_chat_list()
        if chat_list:
            for chat in chat_list:
                if st.button(f"{chat['naslov'][:24]}... ({chat['datum'][:10]})", key=f"hist_{chat['chat_id']}"):
                    st.session_state.current_chat_id = chat['chat_id']
                    st.session_state.messages =[]
                    stare_poruke = get_chat_history(chat['chat_id'])
                    for msg in stare_poruke:
                        if msg["role"] in ["user", "model"]:
                            st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
                    st.rerun()
        else:
            st.markdown('<div class="history-item">Nema istorije još uvek.</div>', unsafe_allow_html=True)

    # 2. CHAT KONTEJNER SA FIKSNOM VISINOM I SCROLLBAR-om
    # Parametar 'height' je ključan! Zaključava visinu i sprečava širenje stranice na dole.
    # Prilagodi broj 600 (piksela) visini tvog ekrana/dizajna.
    chat_container = st.container(height=600)
    
    with chat_container:
        if "messages" not in st.session_state:
            st.session_state.messages =[]
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(f'<div class="chat-bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                with st.chat_message("assistant"):
                    st.markdown(f'<div class="chat-bubble assistant-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    
    # 3. CHAT INPUT (Streamlit ga automatski lepi za dno kolone)
    if prompt := st.chat_input("Pitaj me nešto o finansijama...", key="chat_input"):
        if "chat_session" not in st.session_state:
            try:
                client, chat = get_ai_chat_session()
                st.session_state.gemini_client = client
                st.session_state.chat_session = chat
                if "current_chat_id" not in st.session_state:
                    st.session_state.current_chat_id = get_next_chat_id()
            except Exception as e:
                st.error(f"Greška: {e}")
                st.stop()
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)
        save_chat_message("user", prompt, st.session_state.current_chat_id)
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Analiziram..."):
                    try:
                        response = st.session_state.chat_session.send_message(prompt)
                        st.markdown(f'<div class="chat-bubble assistant-bubble">{response.text}</div>', unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "model", "content": response.text})
                        save_chat_message("model", response.text, st.session_state.current_chat_id)
                    except Exception as e:
                        st.error(f"Greška: {e}")