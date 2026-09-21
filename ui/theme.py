import streamlit as st


def apply():
    st.markdown(
        '''<style>
        :root {
            --fintoran-blue: #2563EB;
            --fintoran-blue-dark: #1D4ED8;
            --fintoran-text: #111827;
            --fintoran-muted: #667085;
            --fintoran-border: #E4E7EC;
            --fintoran-surface: #FFFFFF;
            --fintoran-background: #F8FAFC;
        }

        .stApp { background: var(--fintoran-background); }
        .block-container,
        [data-testid="stAppViewContainer"] .main .block-container {
            max-width: 1280px;
            padding-top: 4.75rem !important;
            padding-bottom: 2.5rem;
            overflow: visible !important;
        }

        .fintoran-brand {
            color: var(--fintoran-text);
            font-size: 2rem;
            font-weight: 750;
            line-height: 1.35;
            letter-spacing: -0.045em;
            margin: 0;
            padding: 0.1rem 0 0;
            overflow: visible;
        }

        .fintoran-auth-brand {
            text-align: center;
            margin: 0 auto 0.5rem auto;
            min-height: 2.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: visible;
        }

        .fintoran-auth-tagline {
            color: var(--fintoran-muted);
            font-size: 0.92rem;
            line-height: 1.5;
            text-align: center;
            max-width: 620px;
            margin: 0 auto 1.5rem auto;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--fintoran-surface);
            border-color: var(--fintoran-border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(16, 24, 40, 0.06);
            padding: 0.35rem 0.45rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTabs"] {
            margin-top: -0.2rem;
        }

        .fintoran-auth-card-label [data-testid="stTextInput"] label {
            font-weight: 600;
            color: var(--fintoran-text);
        }

        [data-testid="stTextInput"] input {
            min-height: 2.85rem;
            border-radius: 9px;
            border-color: #D0D5DD;
            background: #FFFFFF;
        }

        [data-testid="stTextInput"] input:focus {
            border-color: var(--fintoran-blue);
            box-shadow: 0 0 0 1px var(--fintoran-blue);
        }

        [data-testid="stFormSubmitButton"] button {
            min-height: 2.9rem;
            border-radius: 9px;
            font-weight: 650;
            margin-top: 0.45rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTabs"] button[role="tab"] {
            font-weight: 600;
            color: #667085;
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--fintoran-blue-dark);
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stAlert"] { border-radius: 9px; }

        .fintoran-muted { color: #667085; }
        div[data-testid="stMetric"] {
            border: 1px solid #E4E7EC;
            border-radius: 12px;
            padding: .75rem;
            background: #fff;
        }
        .source-card {
            border: 1px solid #E4E7EC;
            border-radius: 10px;
            padding: 12px;
            margin: 8px 0;
            background: #FAFAFA;
        }

        @media (max-width: 700px) {
            .block-container,
            [data-testid="stAppViewContainer"] .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 3.25rem !important;
            }
            .fintoran-brand { font-size: 1.75rem; }
            .fintoran-auth-tagline { font-size: 0.88rem; margin-bottom: 1rem; }
            [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.15rem; border-radius: 13px; }
        }
        </style>''',
        unsafe_allow_html=True,
    )
