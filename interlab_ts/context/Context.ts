import { Tag } from "./Tag";
import { ContextState } from "./ContextState";
import { generateUid } from "../utils";

export class Context {
    name: string;
    kind?: string;
    inputs: { [key: string]: any };
    result?: any;
    error?: any;
    state: ContextState;
    uid: string; // Unique identifier for the context
    children: Context[];
    tags: Tag[];
    startTime?: Date;
    endTime?: Date;
    meta?: { [key: string]: any };
    // Other properties as needed

    constructor(
        name: string,
        kind?: string,
        inputs?: { [key: string]: any },
        meta?: { [key: string]: any },
        tags?: (string | Tag)[]
    ) {
        this.name = name;
        this.kind = kind;
        this.inputs = inputs || {};
        this.meta = meta;
        this.result = null;
        this.error = null;
        this.state = ContextState.New;
        this.uid = generateUid(name); // Implement this function to generate a unique ID
        this.children = [];
        this.tags = tags ? tags.map(Tag.intoTag) : [];
    }

    enter(): void {
        this.state = ContextState.Open;
        this.startTime = new Date();
        // Add additional enter logic here
    }

    exit(): void {
        this.state = ContextState.Finished;
        this.endTime = new Date();
        // Add additional exit logic here
    }

  addTag(tag: string | Tag): void {
        const newTag = Tag.intoTag(tag);
        this.tags.push(newTag);
    }

    addEvent(
        name: string,
        kind?: string,
        data?: any,
        meta?: { [key: string]: any },
        tags?: (string | Tag)[]
    ): Context {
        const event = new Context(name, kind, undefined, meta, tags);
        this.children.push(event);
        return event;
    }

    addInput(name: string, value: any): void {
        if (!this.inputs) {
            this.inputs = {};
        }
        if (name in this.inputs) {
            throw new Error(`Input ${name} already exists`);
        }
        this.inputs[name] = serializeWithType(value); // Assuming serializeWithType exists
    }

    addInputs(inputs: { [key: string]: any }): void {
        if (!this.inputs) {
            this.inputs = {};
        }
        Object.keys(inputs).forEach(name => {
            if (name in this.inputs) {
                throw new Error(`Input ${name} already exists`);
            }
            this.inputs[name] = serializeWithType(inputs[name]);
        });
    }

    set_result(value: any): void {
        this.result = serializeWithType(value); // Assuming serializeWithType exists
    }

    set_error(exc: any): void {
        this.state = ContextState.Error;
        this.error = serializeWithType(exc); // Assuming serializeWithType exists
    }

    has_tag_name(tag_name: string): boolean {
        return this.tags.some(tag => tag.name === tag_name);
    }

    find_contexts(predicate: (context: Context) => boolean): Context[] {
        const result: Context[] = [];
        const helper = (context: Context) => {
            if (predicate(context)) {
                result.push(context);
            }
            context.children.forEach(child => helper(child));
        };
        helper(this);
        return result;
    }
    // Additional methods for handling inputs, results, errors, serialization, etc.
}