import { useState } from "react";
import { TracingNode, gatherKindsAndTags } from "../model/TracingNode";
import { OpenerMode } from "./DataBrowser";
import { TracingNodeView } from "./TracingNodeView";

const config = { themeWithBoxes: false };

export function SingleNodeScreen(props: { node: TracingNode }) {
    const [opened, setOpened] = useState<Set<string>>(() => {
        const s = new Set<string>();
        gatherKindsAndTags(props.node, s);
        s.add(props.node.uid)
        return s
    });

    /* Copy pasted from DataBrowser, need some refactoring */
    function setOpen(keys: string | string[], mode: OpenerMode) {
        setOpened((op) => {
            const o = new Set(op);
            if (!Array.isArray(keys)) {
                keys = [keys]
            }
            if (mode === OpenerMode.Toggle) {
                for (const key of keys) {
                    if (!o.delete(key)) {
                        o.add(key)
                    }
                }
            } else if (mode === OpenerMode.Open) {
                for (const key of keys) {
                    o.add(key)
                }
            } else {
                for (const key of keys) {
                    o.delete(key)
                }
            }
            return o;
        })
    }

    return <TracingNodeView node={props.node} opened={opened} setOpen={setOpen} config={config} />
}