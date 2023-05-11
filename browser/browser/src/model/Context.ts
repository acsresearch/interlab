

export type Context = {
    _type: "Context",
    name: string,
    kind?: string,
    uuid: string,
    state?: string,
    children?: Context[]
    inputs?: any,
    result?: any,
    error?: any,
}