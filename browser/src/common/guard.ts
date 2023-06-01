import axios, { AxiosError } from "axios";
import { AddInfo } from "./info";


export async function callGuard<T>(fn: () => Promise<T>, addInfo: AddInfo, customErrors?: Map<number, string>): Promise<T | null> {
    try {
        return await fn()
    } catch (error) {
        if (axios.isAxiosError(error)) {
            const e = error as AxiosError;
            if (customErrors && e.response?.status && customErrors.has(e.response!.status)) {
                addInfo("error", customErrors.get(e.response!.status)!);
            } else {
                addInfo("error", e.message);
            }
        } else {
            addInfo("error", "Unknown error");
            console.log(error);
        }
        return null;
    }
}