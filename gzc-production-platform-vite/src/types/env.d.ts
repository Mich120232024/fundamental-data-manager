/// <reference types="webpack-env" />

declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: 'development' | 'production' | 'test';
    REACT_APP_API_URL?: string;
    REACT_APP_MSAL_CLIENT_ID?: string;
    REACT_APP_MSAL_TENANT_ID?: string;
  }
}