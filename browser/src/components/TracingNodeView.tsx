import { useState } from "react";
import { TracingNode } from "../model/TracingNode";
import { BrowserConfig, Opener } from "./DataBrowser";
import { NodeDetailsDialog } from "./NodeDetails";
import { TreeNode } from "./TreeNode";


export type NodeViewEnv = {
    config: BrowserConfig,
    opened: Set<string>,
    setOpen: Opener,
    showNodeDetails: (ctx: TracingNode) => void,
}


export function TracingNodeView(props: { node: TracingNode, config: BrowserConfig, opened: Set<string>, setOpen: Opener }) {
    const [ctxDetails, setNodeDetails] = useState<TracingNode | null>(null);

    const env: NodeViewEnv = {
        config: props.config,
        opened: props.opened,
        setOpen: props.setOpen,
        showNodeDetails: setNodeDetails
    }

    return <>
        <div style={{ maxHeight: "calc(100vh - 70px)", overflow: 'auto' }}><TreeNode env={env} node={props.node} depth={0} /></div>
        {ctxDetails && <NodeDetailsDialog node={ctxDetails} onClose={() => setNodeDetails(null)} />}
    </>
}