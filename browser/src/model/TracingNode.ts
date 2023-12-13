
export type Tag = {
    name: string,
    color?: string,
}

export type TracingNodeMeta = {
    color?: string,
    color_bg?: string,
    color_border?: string,
}

export type TracingNode = {
    _type: "TracingNode",
    name: string,
    kind?: string,
    uid: string,
    state?: string,
    meta?: TracingNodeMeta,
    children?: TracingNode[],
    inputs?: any,
    result?: any,
    error?: any,
    start_time?: string,
    end_time?: string,
    tags?: (Tag | string)[],
}

export function gatherKindsAndTags(node: TracingNode, result: Set<string>) {
    if (node.kind !== undefined && node.kind !== null) {
        result.add(node.kind)
    }
    if (node.tags) {
        for (const tag of node.tags) {
            if (typeof tag === 'string') {
                result.add(tag)
            } else {
                result.add(tag.name)
            }
        }
    }
    if (node.children) {
        for (const child of node.children) {
            gatherKindsAndTags(child, result)
        }
    }
}


export function collectTags(nodes: TracingNode[]): Tag[] {
    const result: Tag[] = [];
    for (const ctx of nodes) {
        if (ctx.tags) {
            for (const tagOrString of ctx.tags) {
                const tag = typeof tagOrString === 'string' ? { "name": tagOrString } : tagOrString;
                if (!result.find((t) => t.name === tag.name)) {
                    result.push(tag);
                }
            }
        }
    }
    return result;
}

export function hasTag(node: TracingNode, tagName: string) {
    if (node.tags) {
        for (const tag of node.tags) {
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

export function duration(ctx: TracingNode): number | null {
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


export function getNodeAge(node: TracingNode): number | null {
    if (node.start_time) {
        const start = new Date(node.start_time);
        return Date.now() - start.getTime();
    } else {
        return null;
    }
}


export function getAllChildren(node: TracingNode): string[] {
    const result: string[] = [];
    function _crawl(node: TracingNode) {
        result.push(node.uid);
        if (node.children) {
            for (const c of node.children) {
                _crawl(c);
            }
        }
    }
    _crawl(node);
    return result;
}