import { Configuration, LogLevel } from "@azure/msal-browser";
import { PublicClientApplication } from "@azure/msal-browser";

// Azure environment configuration
const clientId = process.env.AZURE_CLIENT_ID || "";
const tenantId = process.env.AZURE_TENANT_ID || "";
const redirectUri = process.env.AZURE_REDIRECT_URI || window.location.origin;
const authority = `https://login.microsoftonline.com/${tenantId}`;

// Validation for required configuration
if (!clientId || !tenantId) {
    console.error('MSAL Configuration Error: Missing required Azure AD configuration');
    console.error('Required: AZURE_CLIENT_ID, AZURE_TENANT_ID');
}

export const msalConfig: Configuration = {
    auth: {
        clientId,
        authority,
        redirectUri,
        postLogoutRedirectUri: redirectUri,
        navigateToLoginRequestUrl: false,
    },
    cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: false,
    },
    system: {
        loggerOptions: {
            loggerCallback: (
                level: LogLevel,
                message: string,
                containsPii: boolean
            ): void => {
                if (containsPii) return;
                
                // Only log in development or when debug mode is enabled
                const shouldLog = process.env.NODE_ENV === 'development' || process.env.DEBUG_MODE === 'true';
                if (!shouldLog && level !== LogLevel.Error) return;
                
                const prefix = '[MSAL]';
                switch (level) {
                    case LogLevel.Error:
                        console.error(`${prefix} ${message}`);
                        break;
                    case LogLevel.Info:
                        console.info(`${prefix} ${message}`);
                        break;
                    case LogLevel.Verbose:
                        console.debug(`${prefix} ${message}`);
                        break;
                    case LogLevel.Warning:
                        console.warn(`${prefix} ${message}`);
                        break;
                }
            },
            logLevel: process.env.NODE_ENV === 'production' ? LogLevel.Error : LogLevel.Verbose,
        },
    },
};

export const loginRequest = {
    scopes: ["User.Read", "openid", "profile", "email"],
    prompt: "select_account",
};

export const apiRequest = {
    scopes: [`api://${clientId}/.default`],
};
export const msalInstance = new PublicClientApplication(msalConfig);
