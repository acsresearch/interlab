

export function shorten_string(text: string, max_length: number = 35): string {
    if (text.length >= max_length) {
        return text.slice(0, max_length - 4) + " ..."
    } else {
        return text
    }
}