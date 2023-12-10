export class ActorEvent {
    data: any;
    origin?: string;

    constructor(data: any, origin?: string) {
        this.data = data;
        this.origin = origin;
    }
}
