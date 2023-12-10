import { colorForString } from "../utils";

export abstract class BaseActor {
    name: string;
    style: { [key: string]: any };

    constructor(name?: string, style?: { [key: string]: any }) {
        this.name = name || `actor-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`;
        this.style = style || {};
        // Additional logic for 'color' in style, assuming 'randomColor' function exists
        if (!this.style["color"]) {
            this.style["color"] = colorForString(this.name); // Assume randomColor() returns a color string
        }
    }

    abstract copy(): BaseActor;
    abstract query(prompt?: any, expectedType?: any, ...kwargs: any[]): Event; // Event type is assumed
    abstract observe(event: Event | any, origin?: string): void; // Event type is assumed
}
