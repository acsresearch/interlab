

export type Context = {
    _type: "Context",
    name: string,
    kind?: string,
    uid: string,
    state?: string,
    meta?: { color?: string }
    children?: Context[]
    inputs?: any,
    result?: any,
    error?: any,
    start_time?: string,
    end_time?: string,
}

export function gatherKinds(ctx: Context, kinds: Set<string>) {
    if (ctx.kind !== undefined && ctx.kind !== null) {
        kinds.add(ctx.kind)
    }
    if (ctx.children) {
        for (const child of ctx.children) {
            gatherKinds(child, kinds)
        }
    }
}

export function duration(ctx: Context): number | null {
    if (ctx.start_time && ctx.end_time) {
        const start = new Date(ctx.start_time);
        const end = new Date(ctx.end_time);
        return end.getTime() - start.getTime();
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