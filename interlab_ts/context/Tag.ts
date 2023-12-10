export class Tag {
    name: string;
    color?: string;

    constructor(name: string, color?: string) {
        this.name = name;
        this.color = color;
    }

    // Static method to convert a string or Tag into a Tag object
    static intoTag(obj: string | Tag): Tag {
        if (typeof obj === "string") {
            return new Tag(obj);
        } else {
            return obj;
        }
    }
}
