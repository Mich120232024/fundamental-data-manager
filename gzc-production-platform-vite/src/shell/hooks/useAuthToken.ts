import { useMsal } from "@azure/msal-react";
import { useCallback } from "react";
import { loginRequest } from "../components/auth/msalConfig"; // ✅ Uses shared config reference

export default function useAuthToken() {
    const { instance, accounts } = useMsal();

    const getToken = useCallback(async () => {
        console.debug("[useAuthToken] Attempting to retrieve token…");

        if (!instance || accounts.length === 0) {
            console.warn(
                "[useAuthToken] MSAL not ready or no signed-in account."
            );
            throw new Error("MSAL not initialized or no active account.");
        }

        const activeAccount = accounts[0];
        const request = {
            ...loginRequest, // ✅ includes `scopes` from config
            account: activeAccount,
        };

        try {
            const response = await instance.acquireTokenSilent(request);
            console.debug("[useAuthToken] Token acquired successfully.");
            return response.accessToken;
        } catch (err) {
            console.error("[useAuthToken] Token acquisition failed:", err);
            throw err;
        }
    }, [instance, accounts]);

    return { getToken };
}
