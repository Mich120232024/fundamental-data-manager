import { theme } from '../theme';

/**
 * ThemeAdapter - Applies our design system to GZC components
 * This preserves ALL GZC functionality while overlaying our visual design
 * The engineer will recognize their complete code structure
 */
export const ThemeAdapter: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="gzc-theme-override">
      <style>{`
        /* Map GZC Tailwind variables to our theme */
        .gzc-theme-override {
          /* GZC Colors → Our Theme */
          --gzc-primary: ${theme.primary};
          --gzc-secondary: ${theme.secondary};
          --gzc-background: ${theme.background};
          --gzc-surface: ${theme.surface};
          --gzc-surface-alt: ${theme.surfaceAlt};
          --gzc-text: ${theme.text};
          --gzc-text-secondary: ${theme.textSecondary};
          --gzc-border: ${theme.border};
          --gzc-success: ${theme.success};
          --gzc-danger: ${theme.danger};
          --gzc-warning: ${theme.warning};
          --gzc-info: ${theme.info};
        }

        /* Override GZC's Tailwind classes */
        .gzc-theme-override .bg-gzc-white { background-color: ${theme.background}; }
        .gzc-theme-override .bg-gzc-black { background-color: ${theme.background}; }
        .gzc-theme-override .dark\\:bg-gzc-black { background-color: ${theme.background}; }
        .gzc-theme-override .bg-gzc-primary { background-color: ${theme.primary}; }
        .gzc-theme-override .text-gzc-primary { color: ${theme.primary}; }
        .gzc-theme-override .border-gzc-primary { border-color: ${theme.primary}; }
        
        /* GZC Components stay untouched - only colors change */
        .gzc-theme-override .bg-white { background-color: ${theme.surface}; }
        .gzc-theme-override .bg-gray-50 { background-color: ${theme.surfaceAlt}; }
        .gzc-theme-override .bg-gray-100 { background-color: ${theme.surfaceAlt}; }
        .gzc-theme-override .text-gray-600 { color: ${theme.textSecondary}; }
        .gzc-theme-override .text-gray-900 { color: ${theme.text}; }
        .gzc-theme-override .border-gray-200 { border-color: ${theme.border}; }

        /* Override Bootstrap for fx-client */
        .gzc-theme-override .btn-primary {
          background-color: ${theme.primary} !important;
          border-color: ${theme.primary} !important;
        }
        .gzc-theme-override .btn-primary:hover {
          background-color: ${theme.primaryHover} !important;
          border-color: ${theme.primaryHover} !important;
        }
        .gzc-theme-override .table {
          color: ${theme.text} !important;
          background-color: ${theme.surface} !important;
        }
        .gzc-theme-override .table-striped > tbody > tr:nth-of-type(odd) {
          background-color: ${theme.surfaceAlt} !important;
        }
        .gzc-theme-override .modal-content {
          background-color: ${theme.surface} !important;
          color: ${theme.text} !important;
          border: 1px solid ${theme.border} !important;
        }
        .gzc-theme-override .modal-header {
          border-bottom-color: ${theme.border} !important;
        }
        .gzc-theme-override .form-control {
          background-color: ${theme.surfaceAlt} !important;
          border-color: ${theme.border} !important;
          color: ${theme.text} !important;
        }

        /* Apply our typography */
        .gzc-theme-override {
          font-family: ${theme.fontFamily};
        }
        .gzc-theme-override h1 { 
          font-size: ${theme.typography.h1.fontSize}; 
          font-weight: ${theme.typography.h1.fontWeight};
        }
        .gzc-theme-override h2 { 
          font-size: ${theme.typography.h2.fontSize}; 
          font-weight: ${theme.typography.h2.fontWeight};
        }
        .gzc-theme-override h3 { 
          font-size: ${theme.typography.h3.fontSize}; 
          font-weight: ${theme.typography.h3.fontWeight};
        }
        .gzc-theme-override h4 { 
          font-size: ${theme.typography.h4.fontSize}; 
          font-weight: ${theme.typography.h4.fontWeight};
        }
      `}</style>
      {children}
    </div>
  );
};