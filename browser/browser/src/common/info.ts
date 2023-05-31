
export type Severity = "error" | "success"

export type InfoMessage = {
    severity: Severity
    message: string
}

export type AddInfo = (s: Severity, m: string) => void;