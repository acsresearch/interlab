import { type } from "os";


export function shorten_string(text: string, max_length: number = 35): string {
    if (text.length >= max_length) {
        return text.slice(0, max_length - 4) + " ..."
    } else {
        return text
    }
}

export function short_repr(obj: any): string {
    let result;
    if (typeof obj === 'number') {
        result = obj.toString();
    } else if (typeof obj === 'string') {
        result = obj
    } else if (obj._type) {
        result = obj._type;
    } else {
        result = "<object>";
    }
    return shorten_string(result);
}