import { useState } from "react";
import { OpenerMode } from "./DataBrowser";
import { Button } from "@mui/material";
import { ContextEnv } from "./ContextView";


enum OverflowDirection {
    Vertical,
    Horizontal,
    Both,
}

export function OverflowWrapper(props: { uid: string, env: ContextEnv, reducedWidth: number, children: React.ReactNode }) {
    const [over, setOver] = useState<OverflowDirection | null>(null);
    const isOpen = over !== null && props.env.opened.has(props.uid);

    let className;
    if (!isOpen) {
        switch (over) {
            case null: className = undefined; break;
            case OverflowDirection.Vertical: className = "overflow-gradient-v"; break;
            case OverflowDirection.Horizontal: className = "overflow-gradient-h"; break;
            case OverflowDirection.Both: className = "overflow-gradient-vh"; break;
        }
    }

    return <><div
        className={className}
        style={{
            maxWidth: isOpen ? undefined : `calc(100vw - ${550 + props.reducedWidth}px)`,
            maxHeight: isOpen ? undefined : "6em",
            whiteSpace: "pre-wrap",
            overflow: isOpen ? undefined : "hidden"
        }}
        ref={(e) => {
            if (e) {
                if (over === null && e) {
                    if (e.offsetHeight < e.scrollHeight) {
                        setOver(e.offsetWidth < e.scrollWidth ? OverflowDirection.Both : OverflowDirection.Vertical);
                    } else if (e.offsetWidth < e.scrollWidth) {
                        setOver(OverflowDirection.Horizontal);
                    }
                }

            }
        }}
    >{props.children}</div>
        {over !== null && <Button onClick={() => { props.env.setOpen(props.uid, OpenerMode.Toggle) }}>{isOpen ? "Collapse item" : "Expand item"}</Button>}
    </>
}