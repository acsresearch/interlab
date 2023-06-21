

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