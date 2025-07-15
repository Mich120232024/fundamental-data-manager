import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { Layout } from 'react-grid-layout';
import { layoutService } from '@services/api/layoutService';

export interface LayoutComponent {
  id: string;
  type: string;
  props: Record<string, any>;
  layout?: Layout;
}

interface LayoutState {
  layouts: Record<string, Record<string, Layout[]>>;
  components: Record<string, LayoutComponent[]>;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  loadLayout: (layoutId: string) => Promise<void>;
  saveLayout: (layoutId: string) => Promise<void>;
  updateLayout: (layoutId: string, layouts: Record<string, Layout[]>) => void;
  addComponent: (layoutId: string, component: LayoutComponent) => void;
  removeComponent: (layoutId: string, componentId: string) => void;
  updateComponentProps: (layoutId: string, componentId: string, props: Record<string, any>) => void;
  clearError: () => void;
}

export const useLayoutStore = create<LayoutState>()(
  devtools(
    persist(
      immer((set, get) => ({
        layouts: {},
        components: {},
        isLoading: false,
        error: null,

        loadLayout: async (layoutId: string) => {
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            const layoutData = await layoutService.getLayout(layoutId);
            set((state) => {
              state.layouts[layoutId] = layoutData.layouts;
              state.components[layoutId] = layoutData.components;
              state.isLoading = false;
            });
          } catch (error) {
            set((state) => {
              state.error = error instanceof Error ? error.message : 'Failed to load layout';
              state.isLoading = false;
            });
          }
        },

        saveLayout: async (layoutId: string) => {
          const { layouts, components } = get();
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            await layoutService.saveLayout(layoutId, {
              layouts: layouts[layoutId] || {},
              components: components[layoutId] || [],
            });
            set((state) => {
              state.isLoading = false;
            });
          } catch (error) {
            set((state) => {
              state.error = error instanceof Error ? error.message : 'Failed to save layout';
              state.isLoading = false;
            });
          }
        },

        updateLayout: (layoutId: string, newLayouts: Record<string, Layout[]>) => {
          set((state) => {
            state.layouts[layoutId] = newLayouts;
          });
        },

        addComponent: (layoutId: string, component: LayoutComponent) => {
          set((state) => {
            if (!state.components[layoutId]) {
              state.components[layoutId] = [];
            }
            
            // Add default layout if not provided
            if (!component.layout) {
              const existingComponents = state.components[layoutId];
              const y = existingComponents.length * 2;
              component.layout = {
                i: component.id,
                x: 0,
                y,
                w: 4,
                h: 2,
              };
            }

            state.components[layoutId].push(component);
            
            // Update layouts
            Object.keys(state.layouts[layoutId] || {}).forEach((breakpoint) => {
              if (!state.layouts[layoutId]) {
                state.layouts[layoutId] = {};
              }
              if (!state.layouts[layoutId][breakpoint]) {
                state.layouts[layoutId][breakpoint] = [];
              }
              state.layouts[layoutId][breakpoint].push({
                ...component.layout!,
                i: component.id,
              });
            });
          });
        },

        removeComponent: (layoutId: string, componentId: string) => {
          set((state) => {
            // Remove from components
            if (state.components[layoutId]) {
              state.components[layoutId] = state.components[layoutId].filter(
                (c) => c.id !== componentId
              );
            }

            // Remove from layouts
            if (state.layouts[layoutId]) {
              Object.keys(state.layouts[layoutId]).forEach((breakpoint) => {
                state.layouts[layoutId][breakpoint] = state.layouts[layoutId][breakpoint].filter(
                  (l) => l.i !== componentId
                );
              });
            }
          });
        },

        updateComponentProps: (layoutId: string, componentId: string, props: Record<string, any>) => {
          set((state) => {
            const component = state.components[layoutId]?.find((c) => c.id === componentId);
            if (component) {
              component.props = { ...component.props, ...props };
            }
          });
        },

        clearError: () => {
          set((state) => {
            state.error = null;
          });
        },
      })),
      {
        name: 'layout-store',
        partialize: (state) => ({
          layouts: state.layouts,
          components: state.components,
        }),
      }
    )
  )
);