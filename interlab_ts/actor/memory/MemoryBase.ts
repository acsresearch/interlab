export abstract class BaseMemory {
    format: FormatBase; // FormatBase type is assumed

    constructor(format?: FormatBase) {
        this.format = format;
    }

    abstract copy(): BaseMemory;
    abstract addEvent(event: Event): void; // Event type is assumed
    abstract getEvents(query?: any): Event[]; // Event type is assumed
}