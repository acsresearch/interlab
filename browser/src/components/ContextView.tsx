import { useState } from "react";
import { Context } from "../model/Context";
import { BrowserConfig, Opener } from "./DataBrowser";
import { ContextDetailsDialog } from "./ContextDetails";
import { ContextNode } from "./ContextNode";


export type ContextEnv = {
    config: BrowserConfig,
    opened: Set<string>,
    setOpen: Opener,
    showContextDetails: (ctx: Context) => void,
}


export function ContextView(props: { context: Context, config: BrowserConfig, opened: Set<string>, setOpen: Opener }) {
    const [ctxDetails, setCtxDetails] = useState<Context | null>(null);

    const env: ContextEnv = {
        config: props.config,
        opened: props.opened,
        setOpen: props.setOpen,
        showContextDetails: setCtxDetails
    }

    return <>
        <div style={{ maxHeight: "calc(100vh - 70px)", overflow: 'auto' }}><ContextNode env={env} context={props.context} depth={0} /></div>
        {ctxDetails && <ContextDetailsDialog context={ctxDetails} onClose={() => setCtxDetails(null)} />}
    </>
}