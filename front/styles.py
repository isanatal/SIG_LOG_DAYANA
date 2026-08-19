CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ================================================================
       ANIMACIONES CLAVE
       ================================================================ */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(5,150,105,0.2); }
        50% { box-shadow: 0 0 20px rgba(5,150,105,0.4); }
    }
    @keyframes countUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes ripple {
        0% { transform: scale(0.8); opacity: 1; }
        100% { transform: scale(2.4); opacity: 0; }
    }
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }

    /* ---- Fixes de expansion de contenedores ---- */
    .stLayoutWrapper { height: auto !important; }
    .stHorizontalBlock { height: auto !important; }
    .stVerticalBlock { height: auto !important; flex: 1 1 auto !important; }
    [data-testid="stForm"] { height: auto !important; }

    /* ---- Base ---- */
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
    .stApp {
        background: linear-gradient(180deg, #F0FDF4 0%, #F9FAFB 80px, #F9FAFB 100%);
    }
    h1, h2, h3 { color: #064E3B; letter-spacing: -0.025em; font-weight: 700; }

    /* ================================================================
       SIDEBAR
       ================================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(195deg, #064E3B 0%, #065F46 40%, #047857 100%);
        border-right: none;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #A7F3D0; font-size: 0.9rem; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF; }
    .sidebar-brand {
        padding: 0.75rem 0 0.25rem 0;
        margin-bottom: 0.5rem;
    }
    .sidebar-brand .brand-name {
        font-size: 1.7rem;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: -0.03em;
        line-height: 1.1;
        animation: fadeIn 0.5s ease;
    }
    .sidebar-brand .brand-sub {
        font-size: 0.82rem;
        color: #A7F3D0;
        font-weight: 400;
        margin-top: 0.2rem;
        animation: fadeIn 0.7s ease;
    }
    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.15);
        margin: 0.75rem 0;
    }
    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 600;
        color: #D1FAE5;
        font-size: 0.92rem;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] label {
        color: #D1FAE5 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
        background: rgba(255,255,255,0.15) !important;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(5,150,105,0.3);
    }
    [data-testid="stSidebar"] [data-baseweb="radio"]:hover {
        background: rgba(255,255,255,0.08) !important;
        border-radius: 10px;
    }
    .sidebar-footer {
        font-size: 0.78rem;
        color: rgba(255,255,255,0.5);
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.12);
        line-height: 1.6;
    }
    .sidebar-footer code {
        background: rgba(255,255,255,0.12);
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.75rem;
        color: #A7F3D0;
    }

    /* Sidebar nav item icon */
    .nav-icon {
        display: inline-block;
        width: 22px;
        text-align: center;
        margin-right: 6px;
        font-size: 1rem;
    }
    .nav-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: #D1FAE5;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.1rem 0.45rem;
        border-radius: 999px;
        margin-left: 6px;
        vertical-align: middle;
    }

    /* ================================================================
       TARJETAS
       ================================================================ */
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.4s ease;
    }
    .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, #059669, #10B981);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .card::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(5,150,105,0.03), transparent);
        transition: left 0.5s ease;
    }
    .card:hover {
        border-color: #A7F3D0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08), 0 12px 32px rgba(5,150,105,0.1);
        transform: translateY(-3px);
    }
    .card:hover::before { opacity: 1; }
    .card:hover::after { left: 100%; }
    .card-title {
        font-weight: 700;
        color: #064E3B;
        margin-bottom: 0.35rem;
        font-size: 1.02rem;
        transition: color 0.2s ease;
    }
    .card:hover .card-title { color: #059669; }
    .card-text { color: #6B7280; font-size: 0.9rem; line-height: 1.55; }
    .card-module { }
    .pasos { margin: 0; padding-left: 1.25rem; color: #4B5563; line-height: 1.8; }
    .pasos li { margin-bottom: 0.4rem; animation: fadeIn 0.3s ease; }
    .pasos li b { color: #059669; }

    /* Card con icono animado */
    .card-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
    }

    /* ================================================================
       HERO DE INICIO
       ================================================================ */
    .hero {
        background: linear-gradient(135deg, #064E3B 0%, #047857 40%, #059669 70%, #10B981 100%);
        color: #FFFFFF;
        border-radius: 20px;
        padding: 2.5rem 3rem;
        box-shadow: 0 8px 30px rgba(5,150,105,0.25), 0 2px 8px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease;
    }
    .hero::after {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero::before {
        content: '';
        position: absolute;
        bottom: -30%; left: -10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    .hero h1 {
        color: #FFFFFF;
        margin: 0 0 0.5rem 0;
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        position: relative;
        z-index: 1;
    }
    .hero p {
        color: #D1FAE5;
        font-size: 1.05rem;
        margin: 0;
        line-height: 1.65;
        max-width: 700px;
        position: relative;
        z-index: 1;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 999px;
        padding: 0.3rem 1rem;
        font-size: 0.8rem;
        color: #D1FAE5;
        font-weight: 500;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
        animation: bounceIn 0.8s ease;
    }

    /* ================================================================
       ENCABEZADO DE MODULO
       ================================================================ */
    .modulo-header {
        border-left: 5px solid #059669;
        padding: 0.75rem 0 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #ECFDF5 0%, transparent 60%);
        border-radius: 0 12px 12px 0;
        animation: slideInLeft 0.5s ease;
    }
    .modulo-header h1 { margin: 0; font-size: 1.8rem; font-weight: 800; }
    .modulo-header p { margin: 0.25rem 0 0 0; color: #6B7280; font-size: 0.92rem; }

    /* ================================================================
       TITULO DE PANEL DENTRO DE FORMULARIOS
       ================================================================ */
    .panel-titulo {
        font-size: 1.1rem;
        font-weight: 700;
        color: #064E3B;
        margin-bottom: 1rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid #D1FAE5;
    }
    .panel-titulo span {
        display: block;
        font-size: 0.82rem;
        font-weight: 400;
        color: #9CA3AF;
        margin-top: 0.2rem;
    }

    /* ================================================================
       METRICAS (KPI CARDS)
       ================================================================ */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 1.1rem 1.35rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.02);
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.5s ease;
    }
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, #059669, #10B981);
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(5,150,105,0.12);
        border-color: #A7F3D0;
    }
    [data-testid="stMetricLabel"] p {
        color: #6B7280;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        color: #064E3B;
        font-weight: 800;
        animation: countUp 0.6s ease;
    }
    [data-testid="stMetricDelta"] > div {
        font-weight: 600 !important;
    }

    /* KPI variante destacada */
    .kpi-highlight {
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5) !important;
        border-color: #059669 !important;
    }
    .kpi-highlight::before {
        background: linear-gradient(90deg, #047857, #059669, #10B981) !important;
        height: 4px !important;
    }

    /* ================================================================
       BOTONES
       ================================================================ */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #D1D5DB;
        background: #FFFFFF;
        color: #374151;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.55rem 1.4rem;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    .stButton > button::after {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at center, rgba(5,150,105,0.15) 0%, transparent 70%);
        transform: scale(0);
        transition: transform 0.4s ease;
    }
    .stButton > button:hover {
        border-color: #059669;
        color: #059669;
        box-shadow: 0 4px 12px rgba(5,150,105,0.15);
        transform: translateY(-2px);
    }
    .stButton > button:hover::after {
        transform: scale(2.5);
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #059669, #10B981) !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(5,150,105,0.3) !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover,
    [data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #047857, #059669) !important;
        box-shadow: 0 4px 16px rgba(5,150,105,0.4) !important;
        transform: translateY(-2px);
    }

    /* Boton de peligro */
    .stButton > button[kind="secondary"] {
        background: #FFFFFF;
        border-color: #E5E7EB;
    }
    div[data-testid="stForm"] .stButton > button:last-child {
        background: #FFFFFF;
        border: 1px solid #FCA5A5;
        color: #DC2626;
    }
    div[data-testid="stForm"] .stButton > button:last-child:hover {
        background: #FEF2F2;
        border-color: #DC2626;
        box-shadow: 0 2px 8px rgba(220,38,38,0.15);
    }

    /* ================================================================
       INPUTS
       ================================================================ */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: #D1D5DB !important;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stDateInput"] input:focus {
        border-color: #059669 !important;
        box-shadow: 0 0 0 3px rgba(5,150,105,0.12) !important;
    }
    [data-baseweb="select"] {
        border-radius: 10px !important;
    }

    /* ================================================================
       TABS
       ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #F3F4F6;
        border-radius: 12px;
        padding: 0.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #059669 !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(5,150,105,0.05);
    }

    /* ================================================================
       TABLA
       ================================================================ */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E5E7EB;
        transition: border-color 0.2s ease;
    }
    [data-testid="stDataFrame"]:hover {
        border-color: #A7F3D0;
    }

    /* ================================================================
       ALERTAS
       ================================================================ */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        animation: fadeInUp 0.3s ease;
    }

    /* ================================================================
       TOAST
       ================================================================ */
    [data-testid="stToast"] {
        border-radius: 12px;
        border-left: 4px solid #059669;
        animation: slideInRight 0.3s ease;
    }

    /* ================================================================
       DIVIDER
       ================================================================ */
    [data-testid="stDivider"] hr {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1.25rem 0;
    }

    /* ================================================================
       EXPANDERS
       ================================================================ */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #064E3B;
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    .streamlit-expanderHeader:hover {
        background: #F0FDF4;
    }
    details[open] summary {
        border-radius: 10px 10px 0 0;
    }

    /* ================================================================
       SCROLLBAR
       ================================================================ */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: #D1D5DB;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

    /* ================================================================
       BADGES / CHIPS
       ================================================================ */
    .chip {
        display: inline-block;
        background: #ECFDF5;
        color: #047857;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        border: 1px solid #A7F3D0;
        animation: fadeIn 0.3s ease;
    }
    .chip-warning {
        background: #FFFBEB;
        color: #D97706;
        border-color: #FDE68A;
    }
    .chip-danger {
        background: #FEF2F2;
        color: #DC2626;
        border-color: #FECACA;
    }
    .chip-info {
        background: #EFF6FF;
        color: #2563EB;
        border-color: #BFDBFE;
    }
    .chip-purple {
        background: #F5F3FF;
        color: #7C3AED;
        border-color: #DDD6FE;
    }

    /* Status indicator dot */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        vertical-align: middle;
    }
    .status-active { background: #10B981; box-shadow: 0 0 6px rgba(16,185,129,0.5); }
    .status-maintenance { background: #F59E0B; box-shadow: 0 0 6px rgba(245,158,11,0.5); }
    .status-inactive { background: #EF4444; box-shadow: 0 0 6px rgba(239,68,68,0.5); }

    /* ================================================================
       SUBTITULO DE SECCION
       ================================================================ */
    .section-subtitle {
        color: #6B7280;
        font-size: 0.92rem;
        font-weight: 400;
        margin-top: -0.75rem;
        margin-bottom: 1rem;
    }

    /* ================================================================
       INFO BOXES
       ================================================================ */
    .info-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        animation: fadeInUp 0.4s ease;
        transition: all 0.2s ease;
    }
    .info-box:hover {
        border-color: #86EFAC;
        box-shadow: 0 2px 8px rgba(5,150,105,0.08);
    }
    .info-box-title {
        font-weight: 700;
        color: #064E3B;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }
    .info-box-text {
        color: #374151;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    /* ================================================================
       KPI ROW
       ================================================================ */
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }

    /* ================================================================
       SEARCH BAR STYLES
       ================================================================ */
    .search-container {
        position: relative;
        margin-bottom: 1rem;
    }
    .search-bar {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 0.6rem 1rem 0.6rem 2.5rem;
        font-size: 0.9rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .search-bar:focus {
        border-color: #059669;
        box-shadow: 0 0 0 3px rgba(5,150,105,0.12);
        outline: none;
    }
    .search-icon {
        position: absolute;
        left: 0.8rem;
        top: 50%;
        transform: translateY(-50%);
        color: #9CA3AF;
        font-size: 0.9rem;
    }

    /* ================================================================
       ACTIVITY FEED
       ================================================================ */
    .activity-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid #F3F4F6;
        animation: fadeInUp 0.3s ease;
        transition: background 0.2s ease;
        border-radius: 8px;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .activity-item:hover {
        background: #F9FAFB;
    }
    .activity-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .activity-icon-green { background: #D1FAE5; color: #059669; }
    .activity-icon-blue { background: #DBEAFE; color: #2563EB; }
    .activity-icon-yellow { background: #FEF3C7; color: #D97706; }
    .activity-icon-red { background: #FEE2E2; color: #DC2626; }
    .activity-text { font-size: 0.88rem; color: #374151; line-height: 1.5; }
    .activity-time { font-size: 0.75rem; color: #9CA3AF; margin-top: 0.15rem; }

    /* ================================================================
       LOADING SKELETON
       ================================================================ */
    .skeleton {
        background: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
        height: 1rem;
    }
    .skeleton-card {
        background: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 16px;
        height: 120px;
    }

    /* ================================================================
       PROGRESS BAR
       ================================================================ */
    .progress-bar-container {
        background: #E5E7EB;
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #059669, #10B981);
        transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
    }
    .progress-bar-fill.warning {
        background: linear-gradient(90deg, #D97706, #F59E0B);
    }
    .progress-bar-fill.danger {
        background: linear-gradient(90deg, #DC2626, #EF4444);
    }

    /* ================================================================
       TOOLTIP / POPUP
       ================================================================ */
    .tooltip-trigger {
        position: relative;
        display: inline-block;
        cursor: help;
        border-bottom: 1px dashed #9CA3AF;
    }
    .tooltip-trigger:hover .tooltip-content {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }
    .tooltip-content {
        position: absolute;
        bottom: 120%;
        left: 50%;
        transform: translateX(-50%) translateY(5px);
        background: #064E3B;
        color: #FFFFFF;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        font-size: 0.78rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* ================================================================
       EMPTY STATE
       ================================================================ */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #9CA3AF;
    }
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    .empty-state-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .empty-state-text {
        font-size: 0.9rem;
        color: #9CA3AF;
    }

    /* ================================================================
       TABLE ENHANCED ROWS
       ================================================================ */
    .data-row {
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
    }
    .data-row:hover {
        background: #F0FDF4;
        border-left-color: #059669;
    }

    /* ================================================================
       CONTADOR ANIMADO
       ================================================================ */
    .counter-animated {
        font-size: 2rem;
        font-weight: 800;
        color: #064E3B;
        animation: countUp 0.6s ease;
        display: inline-block;
    }

    /* ================================================================
       STEP INDICATOR
       ================================================================ */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .step {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.85rem;
        color: #9CA3AF;
        transition: color 0.2s ease;
    }
    .step.active {
        color: #059669;
        font-weight: 600;
    }
    .step.completed {
        color: #10B981;
    }
    .step-number {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        border: 2px solid #D1D5DB;
        transition: all 0.2s ease;
    }
    .step.active .step-number {
        background: #059669;
        border-color: #059669;
        color: white;
    }
    .step.completed .step-number {
        background: #10B981;
        border-color: #10B981;
        color: white;
    }
    .step-connector {
        width: 24px;
        height: 2px;
        background: #E5E7EB;
    }
    .step.completed + .step-connector {
        background: #10B981;
    }

    /* ================================================================
       MICRO CHART (sparkline placeholder)
       ================================================================ */
    .micro-chart {
        height: 40px;
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
        border-radius: 8px;
        margin-top: 0.5rem;
        position: relative;
        overflow: hidden;
    }

    /* ================================================================
       NOTIFICATION BADGE
       ================================================================ */
    .notif-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #EF4444;
        color: white;
        font-size: 0.65rem;
        font-weight: 700;
        min-width: 18px;
        height: 18px;
        border-radius: 999px;
        padding: 0 5px;
        animation: pulse 2s infinite;
    }

    /* ================================================================
       GLASSMORPHISM CARD
       ================================================================ */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }

    /* ================================================================
       FORM IMPROVED
       ================================================================ */
    [data-testid="stForm"] {
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }
    [data-testid="stForm"]:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    [data-testid="stFormSubmitButton"] {
        margin-top: 0.75rem;
    }

    /* ================================================================
       CONTAINER ANIMATION WRAPPER
       ================================================================ */
    .animate-in {
        animation: fadeInUp 0.4s ease;
    }
    .animate-in-delayed {
        animation: fadeInUp 0.6s ease 0.1s both;
    }

    /* Ocultar menu hamburguesa y deploy de Streamlit */
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
