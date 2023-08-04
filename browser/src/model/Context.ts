
export type Tag = {
    name: string,
    color?: string,
}

export type ContextMeta = {
    color?: string,
    color_bg?: string,
    color_border?: string,
}

export type Context = {
    _type: "Context",
    name: string,
    kind?: string,
    uid: string,
    state?: string,
    meta?: ContextMeta,
    children?: Context[],
    inputs?: any,
    result?: any,
    error?: any,
    start_time?: string,
    end_time?: string,
    tags?: (Tag | string)[],
}

export function gatherKindsAndTags(ctx: Context, result: Set<string>) {
    if (ctx.kind !== undefined && ctx.kind !== null) {
        result.add(ctx.kind)
    }
    if (ctx.tags) {
        for (const tag of ctx.tags) {
            if (typeof tag === 'string') {
                result.add(tag)
            } else {
                result.add(tag.name)
            }
        }
    }
    if (ctx.children) {
        for (const child of ctx.children) {
            gatherKindsAndTags(child, result)
        }
    }
}


export function collectTags(contexts: Context[]): Tag[] {
    const result: Tag[] = [];
    for (const ctx of contexts) {
        if (ctx.tags) {
            for (const tagOrString of ctx.tags) {
                let tag = typeof tagOrString === 'string' ? { "name": tagOrString } : tagOrString;
                if (!result.find((t) => t.name === tag.name)) {
                    result.push(tag);
                }
            }
        }
    }
    return result;
}

export function hasTag(context: Context, tagName: string) {
    if (context.tags) {
        for (const tag of context.tags) {
            if (typeof tag === 'string') {
                if (tag === tagName) {
                    return true;
                }
            } else {
                if (tag.name === tagName) {
                    return true
                }
            }
        }
    }
    return false
}

export function duration(ctx: Context): number | null {
    if (ctx.start_time && ctx.end_time) {
        const start = new Date(ctx.start_time);
        const end = new Date(ctx.end_time);
        return end.getTime() - start.getTime();
    } else if (ctx.start_time && !ctx.end_time && ctx.state === "open") {
        const start = new Date(ctx.start_time);
        return Date.now() - start.getTime();
    } else {
        return null;
    }
}


export function getContextAge(ctx: Context): number | null {
    if (ctx.start_time) {
        const start = new Date(ctx.start_time);
        return Date.now() - start.getTime();
    } else {
        return null;
    }
}


export function getAllChildren(ctx: Context): string[] {
    const result: string[] = [];
    function _crawl(ctx: Context) {
        result.push(ctx.uid);
        if (ctx.children) {
            for (const c of ctx.children) {
                _crawl(c);
            }
        }
    }
    _crawl(ctx);
    return result;
}