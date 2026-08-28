/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./static/**/*.js",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#eff6ff',
                    100: '#dbeafe',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a'
                },
                slate: {
                    950: '#090d16',
                    900: '#0b0f19',
                    850: '#111827',
                    800: '#1e293b',
                    700: '#334155',
                    600: '#475569',
                    500: '#64748b',
                    400: '#94a3b8',
                    300: '#cbd5e1',
                    200: '#e2e8f0',
                    100: '#f1f5f9',
                    50: '#f8fafc'
                }
            },
            fontFamily: {
                sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                display: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'sans-serif']
            },
            spacing: {
                '18': '4.5rem',
                '88': '22rem'
            },
            borderRadius: {
                'none': '0px',
                'sm': '0.125rem',   /* 2px */
                'DEFAULT': '0.25rem', /* 4px */
                'md': '0.25rem',   /* 4px */
                'lg': '0.25rem',   /* 4px */
                'xl': '0.375rem',  /* 6px */
                '2xl': '0.375rem', /* 6px */
                '3xl': '0.5rem',   /* 8px max */
                'full': '9999px'
            }
        }
    },
    plugins: [],
}

